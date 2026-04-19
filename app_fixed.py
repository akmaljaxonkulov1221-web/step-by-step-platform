import os
import sys
import json
import shutil
from flask import Flask, render_template, request, redirect, url_for, session, flash, current_app, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta, date
import random
import string
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# CRITICAL: Set secret key for sessions to work
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'super-secret-key-for-sessions-to-work')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///education_complete.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Log configuration
logger.info(f"Flask app starting with SECRET_KEY: {app.config['SECRET_KEY'][:10]}...")
logger.info(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

# Handle errors globally
@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
    return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500

# PDF upload configuration
app.config['UPLOAD_FOLDER'] = 'uploads/pdfs'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'pdf'}

db = SQLAlchemy(app)

# Helper functions for file handling
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_upload_directory():
    upload_dir = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    return upload_dir

def check_password_hash(pw_hash, password):
    """Check if password matches hash"""
    from werkzeug.security import check_password_hash as werkzeug_check
    return werkzeug_check(pw_hash, password)

# ChatGPT Integration
try:
    from chatgpt_integration import chatgpt
    CHATGPT_AVAILABLE = True
except ImportError:
    CHATGPT_AVAILABLE = False
    print("ChatGPT integration not available, using fallback responses")

# PDF Parser Integration
try:
    from pdf_parser import PDFQuestionExtractor
    PDF_PARSER_AVAILABLE = True
except ImportError:
    PDF_PARSER_AVAILABLE = False
    print("PDF parser not available, using fallback responses")

# Models
class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='student')
    is_active = db.Column(db.Boolean, default=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Group(db.Model):
    __tablename__ = 'group'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    leader_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    students = db.relationship('User', backref='group', lazy=True, foreign_keys='User.group_id')
    leader = db.relationship('User', backref='led_group', lazy=True, foreign_keys=[Group.leader_id])

class Subject(db.Model):
    __tablename__ = 'subject'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    teacher = db.Column(db.String(100))
    pdf_file_path = db.Column(db.String(500))
    pdf_filename = db.Column(db.String(255))
    
    topics = db.relationship('Topic', backref='subject', lazy=True, cascade='all, delete-orphan')
    tests = db.relationship('Test', backref='subject', lazy=True, cascade='all, delete-orphan')

class Topic(db.Model):
    __tablename__ = 'topic'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    video_url = db.Column(db.String(500))
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    pdf_file_path = db.Column(db.String(500))
    pdf_filename = db.Column(db.String(255))

class Test(db.Model):
    __tablename__ = 'test'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=True)
    test_type = db.Column(db.String(20), nullable=False)
    test_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    duration_minutes = db.Column(db.Integer, default=60)
    is_active = db.Column(db.Boolean, default=True)
    pdf_file_path = db.Column(db.String(500))
    pdf_filename = db.Column(db.String(255))
    
    questions = db.relationship('Question', backref='test', lazy=True, cascade='all, delete-orphan')
    registrations = db.relationship('TestRegistration', backref='test', lazy=True, cascade='all, delete-orphan')
    results = db.relationship('TestResult', backref='test', lazy=True, cascade='all, delete-orphan')

class Question(db.Model):
    __tablename__ = 'question'
    
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(500), nullable=False)
    option_b = db.Column(db.String(500), nullable=False)
    option_c = db.Column(db.String(500), nullable=False)
    option_d = db.Column(db.String(500), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)
    points = db.Column(db.Integer, default=1)

class TestRegistration(db.Model):
    __tablename__ = 'test_registration'
    
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='test_registrations', lazy=True)

class TestResult(db.Model):
    __tablename__ = 'test_result'
    
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    total_points = db.Column(db.Integer, nullable=False)
    percentage = db.Column(db.Float, nullable=False)
    test_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='test_results', lazy=True)

class WeeklyTestSchedule(db.Model):
    __tablename__ = 'weekly_test_schedule'
    
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=True)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0-6 (Monday-Sunday)
    week_start_date = db.Column(db.Date, nullable=False)
    test_time = db.Column(db.Time, nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    
    group = db.relationship('Group', backref='weekly_schedules', lazy=True)
    subject = db.relationship('Subject', backref='weekly_schedules', lazy=True)
    test = db.relationship('Test', backref='weekly_schedules', lazy=True)

class DifficultTopic(db.Model):
    __tablename__ = 'difficult_topic'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)
    marked_date = db.Column(db.DateTime, default=datetime.utcnow)
    reason = db.Column(db.Text)
    
    user = db.relationship('User', backref='difficult_topics', lazy=True)
    topic = db.relationship('Topic', backref='marked_difficult', lazy=True)

class AIChat(db.Model):
    __tablename__ = 'ai_chat'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='ai_chats', lazy=True)

# Initialize database
def init_database():
    """Initialize database if it doesn't exist"""
    try:
        db.create_all()
        print("Database initialized successfully")
        
        # Create admin user if not exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@example.com',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Admin user created")
            
    except Exception as e:
        print(f"Database initialization error: {e}")

# Initialize database on startup
init_database()

# Routes
@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Username va password kiritilishi shart!', 'error')
            return render_template('login.html')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.is_active:
            session['logged_in'] = True
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.role == 'admin'
            
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
        else:
            flash('Username yoki password noto\'g\'ri!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    return redirect(url_for('login'))

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard"""
    if not session.get('logged_in') or not session.get('is_admin'):
        return redirect(url_for('login'))
    
    # Get statistics
    total_users = User.query.count()
    total_students = User.query.filter_by(role='student').count()
    total_groups = Group.query.count()
    total_subjects = Subject.query.count()
    total_tests = Test.query.count()
    
    return render_template('admin_dashboard.html', 
                         total_users=total_users,
                         total_students=total_students,
                         total_groups=total_groups,
                         total_subjects=total_subjects,
                         total_tests=total_tests)

@app.route('/admin/subjects')
def admin_subjects():
    """Admin subjects page"""
    if not session.get('logged_in') or not session.get('is_admin'):
        return redirect(url_for('login'))
    
    subjects = Subject.query.all()
    return render_template('admin_subjects.html', subjects=subjects)

@app.route('/admin/students')
def admin_students():
    """Admin students page"""
    if not session.get('logged_in') or not session.get('is_admin'):
        return redirect(url_for('login'))
    
    students = User.query.filter_by(role='student').all()
    groups = Group.query.all()
    return render_template('admin_students.html', students=students, groups=groups)

@app.route('/admin/groups')
def admin_groups():
    """Admin groups page"""
    if not session.get('logged_in') or not session.get('is_admin'):
        return redirect(url_for('login'))
    
    groups = Group.query.all()
    return render_template('admin_groups.html', groups=groups)

@app.route('/admin/tests')
def admin_tests():
    """Admin tests page"""
    if not session.get('logged_in') or not session.get('is_admin'):
        return redirect(url_for('login'))
    
    tests = Test.query.order_by(Test.test_date.desc()).all()
    subjects = Subject.query.all()
    return render_template('admin_tests.html', tests=tests, subjects=subjects)

@app.route('/student/dashboard')
def student_dashboard():
    """Student dashboard"""
    if not session.get('logged_in') or session.get('is_admin'):
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    return render_template('student_dashboard.html', user=user)

@app.route('/tests')
def tests():
    """Tests page for students"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    # Get weekly test schedule
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    
    schedule_data = {}
    days = ['Dushanba', 'Seshanba', 'Chorshanba', 'Payshanba', 'Juma', 'Shanba', 'Yakshanba']
    
    for day_index in range(7):
        current_day = week_start + timedelta(days=day_index)
        schedule = WeeklyTestSchedule.query.filter_by(
            week_start_date=week_start,
            day_of_week=day_index
        ).all()
        
        schedule_data[day_index] = {
            'date': current_day,
            'day_name': days[day_index],
            'schedule': schedule,
            'is_today': current_day == today
        }
    
    return render_template('weekly_tests.html', 
                         schedule_data=schedule_data, 
                         week_start=week_start, 
                         timedelta=timedelta, 
                         today=today)

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

# Initialize upload directory
ensure_upload_directory()

if __name__ == '__main__':
    app.run(debug=True)
