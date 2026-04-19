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

def check_password_hash(pw_hash, password):
    """Check if password matches hash"""
    from werkzeug.security import check_password_hash as werkzeug_check
    return werkzeug_check(pw_hash, password)


import random
import string
import logging

app = Flask(__name__)

# CRITICAL: Set secret key for sessions to work
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'super-secret-key-for-sessions-to-work')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///education_complete.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# PDF upload configuration
app.config['UPLOAD_FOLDER'] = 'uploads/pdfs'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'pdf'}

db = SQLAlchemy(app)

# Initialize database if it doesn't exist
def init_database():
    """Initialize database if it doesn't exist"""
    try:
        with app.app_context():
            # Create all tables
            db.create_all()
            print("Database initialized successfully")
    except Exception as e:
        print(f"Database initialization error: {e}")

# Initialize database on startup
init_database()

# Helper functions for file handling
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_upload_directory():
    upload_dir = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    return upload_dir

def create_weekly_schedule_for_group(group_id, week_start):
    """Create weekly test schedule for a group"""
    # Check if schedule already exists for this week
    existing_schedule = WeeklyTestSchedule.query.filter_by(
        group_id=group_id,
        week_start_date=week_start
    ).first()
    
    if existing_schedule:
        return  # Schedule already exists
    
    # Get available tests for this group
    available_tests = Test.query.filter_by(test_type='daily', is_active=True).all()
    
    if not available_tests:
        return  # No tests available
    
    # Select 7 tests (one for each day)
    selected_tests = available_tests[:7]  # Take first 7 tests
    
    # Create schedule for each day
    for day_num in range(1, 8):
        if day_num <= len(selected_tests):
            test = selected_tests[day_num - 1]
            
            schedule = WeeklyTestSchedule(
                group_id=group_id,
                subject_id=test.subject_id,
                test_id=test.id,
                day_number=day_num,
                week_start_date=week_start
            )
            db.session.add(schedule)
    
    db.session.commit()

# Database Models
class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_group_leader = db.Column(db.Boolean, default=False)
    needs_password_change = db.Column(db.Boolean, default=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=True)

    
    # Relationships
    group = db.relationship('Group', backref=db.backref('students', lazy=True, cascade='all, delete-orphan'), foreign_keys=[group_id])
    test_registrations = db.relationship('TestRegistration', backref='student', lazy=True, cascade='all, delete-orphan')
    test_results = db.relationship('TestResult', backref='student', lazy=True, cascade='all, delete-orphan')
    difficult_topics = db.relationship('DifficultTopic', backref='student', lazy=True, cascade='all, delete-orphan')

class Group(db.Model):
    __tablename__ = 'group'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    total_score = db.Column(db.Integer, default=0)

    
    # Relationships
    leader = db.relationship('User', backref=db.backref('led_group', uselist=False), foreign_keys=[User.group_id])
    schedules = db.relationship('Schedule', backref='group', lazy=True, cascade='all, delete-orphan')

class Subject(db.Model):
    __tablename__ = 'subject'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    pdf_file_path = db.Column(db.String(500))  # PDF fayl yo'li
    pdf_filename = db.Column(db.String(255))   # PDF fayl nomi

    
    # Relationships
    topics = db.relationship('Topic', backref='subject', lazy=True, cascade='all, delete-orphan')
    tests = db.relationship('Test', backref='subject', lazy=True, cascade='all, delete-orphan')
    schedules = db.relationship('Schedule', backref='subject', lazy=True, cascade='all, delete-orphan')

class Topic(db.Model):
    __tablename__ = 'topic'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    video_url = db.Column(db.String(500))
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    pdf_file_path = db.Column(db.String(500))  # PDF fayl yo'li
    pdf_filename = db.Column(db.String(255))   # PDF fayl nomi
    
    # Relationships
    marked_by = db.relationship('DifficultTopic', backref='topic', lazy=True, cascade='all, delete-orphan')


class AIChat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'))
    test_generated = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, nullable=True)
    
    user = db.relationship('User', backref=db.backref('ai_chats', lazy=True, cascade='all, delete-orphan'))
    topic = db.relationship('Topic', backref=db.backref('ai_chats', lazy=True))


class Certificate(db.Model):
    __tablename__ = 'certificate'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    certificate_number = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    issue_date = db.Column(db.DateTime, nullable=False)
    expiry_date = db.Column(db.DateTime)
    file_path = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, nullable=False)
    
    user = db.relationship('User', backref=db.backref('certificates', lazy=True, cascade='all, delete-orphan'))


class Test(db.Model):
    __tablename__ = 'test'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=True)
    test_type = db.Column(db.String(20), nullable=False)  # 'daily', 'dtm', 'comprehensive'
    test_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    duration_minutes = db.Column(db.Integer, default=60)
    is_active = db.Column(db.Boolean, default=True)
    pdf_file_path = db.Column(db.String(500))  # PDF fayl yo'li
    pdf_filename = db.Column(db.String(255))   # PDF fayl nomi
    
    # Relationships
    questions = db.relationship('Question', backref='test', lazy=True, cascade='all, delete-orphan')
    registrations = db.relationship('TestRegistration', backref='test', lazy=True, cascade='all, delete-orphan')
    results = db.relationship('TestResult', backref='test', lazy=True, cascade='all, delete-orphan')

class Question(db.Model):
    __tablename__ = 'question'
    
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(500), nullable=False)
    option_b = db.Column(db.String(500), nullable=False)
    option_c = db.Column(db.String(500), nullable=False)
    option_d = db.Column(db.String(500), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=False)


class TestRegistration(db.Model):
    __tablename__ = 'test_registration'
    
    id = db.Column(db.Integer, primary_key=True)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=False)

class TestResult(db.Model):
    __tablename__ = 'test_result'
    
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    percentage = db.Column(db.Float, nullable=False)
    points_earned = db.Column(db.Integer, default=0)
    taken_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=False)

class Schedule(db.Model):
    __tablename__ = 'schedule'
    
    id = db.Column(db.Integer, primary_key=True)
    day_of_week = db.Column(db.String(10), nullable=False)  # 'Monday', 'Tuesday', etc.
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

class WeeklyTestSchedule(db.Model):
    __tablename__ = 'weekly_test_schedule'
    
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=False)
    day_number = db.Column(db.Integer, nullable=False)  # 1-7 (hafta kunlari)
    week_start_date = db.Column(db.Date, nullable=False)  # Hafta boshlanishi sanasi
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    group = db.relationship('Group', backref='weekly_schedules')
    subject = db.relationship('Subject', backref='weekly_schedules')
    test = db.relationship('Test', backref='weekly_schedules')




class DifficultTopic(db.Model):
    __tablename__ = 'difficult_topic'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)
    marked_at = db.Column(db.DateTime, default=datetime.utcnow)

# Helper functions
def generate_username(first_name, last_name, group_name):
    """Generate unique username from first name, last name, and group"""
    base = f"{first_name.lower()}.{last_name.lower()}.{group_name.lower()}"
    username = base
    counter = 1
    
    while User.query.filter_by(username=username).first():
        username = f"{base}{counter}"
        counter += 1
    
    return username

def generate_password(length=8):
    """Generate random password"""
    characters = string.ascii_letters + string.digits + "!@#$%"
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

def calculate_dtm_points(rank, total_participants):
    """Calculate points for DTM test based on rank"""
    if rank == 1:
        return 100
    elif rank == 2:
        return 90
    elif rank == 3:
        return 80
    elif 4 <= rank <= 10:
        return 60
    elif 11 <= rank <= 20:
        return 40
    elif 21 <= rank <= int(total_participants * 0.6):
        return 20
    else:
        return 0

def calculate_daily_points(percentage):
    """Calculate points for daily test based on percentage"""
    if percentage >= 90:
        return 10
    elif percentage >= 80:
        return 8
    elif percentage >= 70:
        return 6
    elif percentage >= 60:
        return 4
    else:
        return 0

@app.context_processor
def inject_user():
    # Create a simple current_user object for templates
    class CurrentUser:
        def __init__(self):
            self.is_authenticated = session.get('logged_in', False)
            self.is_admin = session.get('is_admin', False)
            self.is_group_leader = session.get('is_group_leader', False)
            self.username = session.get('username', '')
            self.id = session.get('user_id', None)
        
        def is_authenticated_method(self):
            return self.is_authenticated
    
    return dict(current_user=CurrentUser(), datetime=datetime)

# Routes
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            return render_template('login.html', error="Login va parolni kiriting!")
        
        try:
            # Simple hardcoded admin login
            if username == 'admin' and password == 'admin123':
                # Create admin user if not exists
                admin_user = User.query.filter_by(username='admin').first()
                if not admin_user:
                    default_group = Group.query.filter_by(name='Admin').first()
                    if not default_group:
                        default_group = Group(name='Admin', total_score=0)
                        db.session.add(default_group)
                        db.session.flush()
                    
                    admin_user = User(
                        username='admin',
                        password_hash=generate_password_hash('admin123'),
                        first_name='Admin',
                        last_name='User',
                        group_id=default_group.id,
                        is_admin=True
                    )
                    db.session.add(admin_user)
                    db.session.commit()
                
                # Store user in session
                session['user_id'] = admin_user.id
                session['username'] = admin_user.username
                session['is_admin'] = admin_user.is_admin
                session['is_group_leader'] = admin_user.is_group_leader
                session['logged_in'] = True
                
                flash(f"Admin panelga xush kelibsiz, {admin_user.first_name}!", 'success')
                return redirect(url_for('admin_dashboard'))
            
            # Check regular users
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password_hash, password):
                session['user_id'] = user.id
                session['username'] = user.username
                session['is_admin'] = user.is_admin
                session['is_group_leader'] = user.is_group_leader
                session['logged_in'] = True
                
                if user.needs_password_change:
                    return redirect(url_for('change_password'))
                elif user.is_admin:
                    flash(f"Admin panelga xush kelibsiz, {user.first_name}!", 'success')
                    return redirect(url_for('admin_dashboard'))
                elif user.is_group_leader:
                    flash(f"Guruh rahbar paneliga xush kelibsiz, {user.first_name}!", 'success')
                    return redirect(url_for('group_leader_dashboard'))
                else:
                    flash(f"O'quvchi paneliga xush kelibsiz, {user.first_name}!", 'success')
                    return redirect(url_for('student_dashboard'))
            
            return render_template('login.html', error="Login yoki parol noto'g'ri!")
            
        except Exception as e:
            app.logger.error(f"Login error: {str(e)}")
            return render_template('login.html', error="Tizimda xatolik yuz berdi. Iltimos, qayta urinib ko'ring!")
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        group_id = request.form.get('group_id', type=int)
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        # Get groups for form
        groups = Group.query.filter(Group.name.in_(['101', '102', '103', '104', '105', '106', '107', '108'])).all()
        
        # Validation
        if not first_name or not last_name:
            return render_template('register.html', error="Ism va familiyani kiriting!", groups=groups)
        
        if not group_id:
            return render_template('register.html', error="Guruhni tanlang!", groups=groups)
        
        if not password or not confirm_password:
            return render_template('register.html', error="Parolni kiriting!", groups=groups)
        
        if password != confirm_password:
            return render_template('register.html', error="Parollar mos kelmadi!", groups=groups)
        
        if len(password) < 6:
            return render_template('register.html', error="Parol kamida 6 ta belgidan iborat bo'lishi kerak!", groups=groups)
        
        try:
            group = Group.query.get(group_id)
            if not group:
                return render_template('register.html', error="Guruh topilmadi!", groups=groups)
            
            # Check if user already exists with same name and group
            existing_user = User.query.filter_by(
                first_name=first_name,
                last_name=last_name,
                group_id=group_id
            ).first()
            
            if existing_user:
                # User already exists, just update password
                existing_user.password_hash = generate_password_hash(password)
                existing_user.updated_at = datetime.utcnow()
                db.session.commit()
                
                # Auto-login after password update
                session['logged_in'] = True
                session['user_id'] = existing_user.id
                session['is_admin'] = existing_user.is_admin
                session['is_group_leader'] = existing_user.is_group_leader
                session['username'] = existing_user.username
                
                flash(f"Siz allaqachon ro'yxatdan o'tgansiz! Login: {existing_user.username}", 'info')
                return redirect(url_for('student_dashboard'))
            
            # Generate automatic username
            username = generate_username(first_name, last_name, group.name)
            
            # Make username unique by adding number if needed
            base_username = username
            counter = 1
            while User.query.filter_by(username=username).first():
                username = f"{base_username}{counter}"
                counter += 1
            
            # Create new student
            new_user = User(
                username=username,
                password_hash=generate_password_hash(password),
                first_name=first_name,
                last_name=last_name,
                group_id=group_id,
                is_admin=False,
                is_group_leader=False
            )
            db.session.add(new_user)
            db.session.commit()
            
            # Auto-login after registration
            session['logged_in'] = True
            session['user_id'] = new_user.id
            session['is_admin'] = new_user.is_admin
            session['is_group_leader'] = new_user.is_group_leader
            session['username'] = new_user.username
            
            flash(f"Ro'yxatdan o'tdingiz! Sizning loginiz: {username}", 'success')
            return redirect(url_for('student_dashboard'))
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Registration error: {str(e)}")
            groups = Group.query.filter(Group.name.in_(['101', '102', '103', '104', '105', '106', '107', '108'])).all()
            return render_template('register.html', error="Ro'yxatdan o'tishda xatolik yuz berdi. Iltimos, qayta urinib ko'ring!", groups=groups)
    
    groups = Group.query.filter(Group.name.in_(['101', '102', '103', '104', '105', '106', '107', '108'])).all()
    return render_template('register.html', groups=groups)

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in', False):
        return redirect(url_for('login'))
    
    if session.get('is_admin', False):
        return redirect(url_for('admin_dashboard'))
    elif session.get('is_group_leader', False):
        return redirect(url_for('group_leader_dashboard'))
    else:
        return redirect(url_for('student_dashboard'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('logged_in', False) or not session.get('is_admin', False):
        return redirect(url_for('login'))
    
    total_students = User.query.filter_by(is_admin=False, is_group_leader=False).count()
    total_groups = Group.query.count()
    total_tests = Test.query.count()
    total_subjects = Subject.query.count()
    total_group_leaders = User.query.filter_by(is_group_leader=True).count()
    
    # Get weekly test schedule
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    weekly_tests = Test.query.filter(
        Test.test_date >= week_start,
        Test.test_date <= week_end
    ).order_by(Test.test_date).all()
    
    # Get recent test results
    recent_results = TestResult.query.order_by(TestResult.taken_at.desc()).limit(5).all()
    
    return render_template('admin_dashboard.html',
                         total_students=total_students,
                         total_groups=total_groups,
                         total_tests=total_tests,
                         total_subjects=total_subjects,
                         total_group_leaders=total_group_leaders,
                         weekly_tests=weekly_tests,
                         recent_results=recent_results)

@app.route('/students')
def students():
    if not session.get('logged_in', False) or not session.get('is_admin', False):
        return redirect(url_for('login'))
    return redirect(url_for('admin_students'))

@app.route('/admin/students')
def admin_students():
    if not session.get('logged_in', False) or not session.get('is_admin', False):
        return redirect(url_for('login'))
    students = User.query.filter_by(is_admin=False, is_group_leader=False).all()
    groups = Group.query.all()
    return render_template('admin_students.html', students=students, groups=groups)

@app.route('/admin/add_student', methods=['POST'])
def admin_add_student():
    if not session.get('logged_in', False) or not session.get('is_admin', False):
        return redirect(url_for('login'))
    
    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    group_id = request.form.get('group_id', type=int)
    password = request.form.get('password', '').strip()
    
    group = Group.query.get(group_id)
    if not group:
        flash("Guruh topilmadi!", 'error')
        return redirect(url_for('admin_students'))
    
    # Generate automatic username
    username = generate_username(first_name, last_name, group.name)
    
    # Create new student
    new_student = User(
        username=username,
        password_hash=generate_password_hash(password),
        first_name=first_name,
        last_name=last_name,
        group_id=group_id,
        is_admin=False,
        is_group_leader=False
    )
    db.session.add(new_student)
    db.session.commit()
    
    flash(f"O'quvchi muvaffaqiyatli qo'shildi! Login: {username}, Parol: {password}", 'success')
    return redirect(url_for('admin_students'))

@app.route('/admin/reset_password/<int:student_id>', methods=['POST'])
def admin_reset_password(student_id):
    if not session.get('logged_in', False) or not session.get('is_admin', False):
        return redirect(url_for('login'))
    
    student = User.query.get_or_404(student_id)
    new_password = generate_password()
    student.password_hash = generate_password_hash(new_password)
    student.needs_password_change = True
    db.session.commit()
    
    flash(f"{student.first_name} {student.last_name} uchun yangi parol: {new_password}", 'success')
    return redirect(url_for('admin_students'))

@app.route('/admin/edit_student/<int:student_id>', methods=['GET', 'POST'])
def admin_edit_student(student_id):
    if not session.get('logged_in', False) or not session.get('is_admin', False):
        return redirect(url_for('login'))
    
    student = User.query.get_or_404(student_id)
    groups = Group.query.all()
    
    if request.method == 'POST':
        student.first_name = request.form.get('first_name', '').strip()
        student.last_name = request.form.get('last_name', '').strip()
        student.group_id = request.form.get('group_id', type=int)
        
        db.session.commit()
        flash("O'quvchi ma'lumotlari yangilandi!", 'success')
        return redirect(url_for('admin_students'))
    
    return render_template('edit_student.html', student=student, groups=groups)

@app.route('/admin/delete_student/<int:student_id>', methods=['POST'])
def admin_delete_student(student_id):
    if not session.get('logged_in', False) or not session.get('is_admin', False):
        return redirect(url_for('login'))
    
    student = User.query.get_or_404(student_id)
    
    try:
        # Delete ALL related records in correct order to avoid foreign key constraints
        # 1. Delete test registrations first
        TestRegistration.query.filter_by(user_id=student_id).delete()
        
        # 2. Delete test results
        TestResult.query.filter_by(user_id=student_id).delete()
        
        # 3. Delete certificates
        Certificate.query.filter_by(user_id=student_id).delete()
        
        # 4. Delete difficult topics
        DifficultTopic.query.filter_by(user_id=student_id).delete()
        
        # 5. Check if user is group leader and update group
        if student.is_group_leader and student.group:
            student.group.leader = None
            student.group.leader_id = None
        
        # 6. Delete the user
        db.session.delete(student)
        
        # 7. Commit all changes
        db.session.commit()
        
        # 8. Clear any cached data
        from flask import current_app
        if hasattr(current_app, '_cached_user_data'):
            if str(student_id) in current_app._cached_user_data:
                del current_app._cached_user_data[str(student_id)]
        
        # 9. Mark student as deleted in persistent data
        try:
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from restore_persistent_state import mark_student_deleted
            mark_student_deleted(student_id, student.username, student.first_name, student.last_name)
        except Exception as e:
            app.logger.error(f"Failed to mark student as deleted in persistent data: {e}")
        
        flash("O'quvchi ma'lumotlari to'liq o'chirildi!", 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f"O'chirishda xatolik: {str(e)}", 'error')
        current_app.logger.error(f"Error deleting student {student_id}: {str(e)}")
    
    return redirect(url_for('admin_students'))


@app.route('/admin/certificates')
def admin_certificates():
    if not session.get('logged_in', False) or not session.get('is_admin', False):
        return redirect(url_for('login'))
    
    certificates = Certificate.query.all()
    students = User.query.filter_by(is_admin=False, is_group_leader=False).all()
    
    return render_template('admin_certificates.html', certificates=certificates, students=students)


@app.route('/admin/upload_certificate', methods=['POST'])
def admin_upload_certificate():
    if not session.get('logged_in', False) or not session.get('is_admin', False):
        return redirect(url_for('login'))
    
    try:
        user_id = request.form.get('user_id')
        certificate_number = request.form.get('certificate_number')
        title = request.form.get('title')
        description = request.form.get('description')
        issue_date_str = request.form.get('issue_date')
        expiry_date_str = request.form.get('expiry_date')
        
        # Handle file upload
        file = request.files.get('certificate_file')
        file_path = None
        
        if file and file.filename:
            # Create secure filename
            filename = secure_filename(file.filename)
            # Add timestamp to make it unique
            import time
            timestamp = int(time.time())
            filename = f"{timestamp}_{filename}"
            
            # Save file
            upload_folder = os.path.join(app.root_path, 'uploads', 'certificates')
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join('uploads', 'certificates', filename)
            file.save(os.path.join(app.root_path, file_path))
        
        # Parse dates
        issue_date = datetime.strptime(issue_date_str, '%Y-%m-%d') if issue_date_str else datetime.now()
        expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d') if expiry_date_str else None
        
        # Create certificate
        certificate = Certificate(
            user_id=user_id,
            certificate_number=certificate_number,
            title=title,
            description=description,
            issue_date=issue_date,
            expiry_date=expiry_date,
            file_path=file_path,
            created_at=datetime.now()
        )
        
        db.session.add(certificate)
        db.session.commit()
        
        flash('Sertifikat muvaffaqiyatli yuklandi!', 'success')
        return redirect(url_for('admin_certificates'))
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Certificate upload error: {str(e)}')
        flash('Sertifikat yuklashda xatolik yuz berdi!', 'error')
        return redirect(url_for('admin_certificates'))


@app.route('/admin/delete_certificate/<int:certificate_id>', methods=['POST'])
def admin_delete_certificate(certificate_id):
    if not session.get('logged_in', False) or not session.get('is_admin', False):
        return redirect(url_for('login'))
    
    try:
        certificate = Certificate.query.get_or_404(certificate_id)
        
        # Delete file if exists
        if certificate.file_path:
            file_full_path = os.path.join(app.root_path, certificate.file_path)
            if os.path.exists(file_full_path):
                os.remove(file_full_path)
        
        # Delete certificate
        db.session.delete(certificate)
        db.session.commit()
        
        flash('Sertifikat muvaffaqiyatli o\'chirildi!', 'success')
        return redirect(url_for('admin_certificates'))
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Certificate deletion error: {str(e)}')
        flash('Sertifikat o\'chirishda xatolik yuz berdi!', 'error')
        return redirect(url_for('admin_certificates'))


@app.route('/admin/groups')
def admin_groups():
    if not session.get('logged_in', False) or not session.get('is_admin', False):
        return redirect(url_for('login'))
    groups = Group.query.all()
    return render_template('admin_groups.html', groups=groups)

@app.route('/admin/add_group', methods=['POST'])
def admin_add_group():
    if not session.get('logged_in', False) or not session.get('is_admin', False):
        return redirect(url_for('login'))
    
    name = request.form.get('name', '').strip()
    
    # Check if group already exists
    existing_group = Group.query.filter_by(name=name).first()
    if existing_group:
        flash("Bu guruh nomi allaqachon mavjud!", 'error')
        return redirect(url_for('admin_groups'))
    
    # Create new group
    new_group = Group(name=name, total_score=0)
    db.session.add(new_group)
    db.session.commit()
    
    flash("Guruh muvaffaqiyatli qo'shildi!", 'success')
    return redirect(url_for('admin_groups'))

@app.route('/admin/group_leaders')
def admin_group_leaders():
    if not session.get('logged_in', False) or not session.get('is_admin', False):
        return redirect(url_for('login'))
    group_leaders = User.query.filter_by(is_group_leader=True).all()
    groups = Group.query.all()
    return render_template('admin_group_leaders.html', group_leaders=group_leaders, groups=groups)

@app.route('/admin/add_group_leader', methods=['POST'])
def admin_add_group_leader():
    if not session.get('logged_in', False) or not session.get('is_admin', False):
        return redirect(url_for('login'))
    
    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    group_id = request.form.get('group_id', type=int)
    
    group = Group.query.get(group_id)
    if not group:
        flash("Guruh topilmadi!", 'error')
        return redirect(url_for('admin_group_leaders'))
    
    # Generate automatic username
    username = generate_username(first_name, last_name, group.name)
    temp_password = generate_password()
    
    # Create new group leader
    new_leader = User(
        username=username,
        password_hash=generate_password_hash(temp_password),
        first_name=first_name,
        last_name=last_name,
        group_id=group_id,
        is_admin=False,
        is_group_leader=True,
        needs_password_change=True
    )
    db.session.add(new_leader)
    db.session.commit()
    
    flash(f"Guruh rahbari muvaffaqiyatli qo'shildi! Login: {username}, Bir martalik parol: {temp_password}", 'success')
    return redirect(url_for('admin_groups'))

@app.route('/admin/edit_group/<int:group_id>', methods=['GET', 'POST'])
def admin_edit_group(group_id):
    if not session.get('logged_in', False) or not session.get('is_admin', False):
        return redirect(url_for('login'))
    
    group = Group.query.get_or_404(group_id)
    
    if request.method == 'POST':
        group.name = request.form.get('name', '').strip()
        group.description = request.form.get('description', '').strip()
        db.session.commit()
        flash("Guruh ma'lumotlari yangilandi!", 'success')
        return redirect(url_for('admin_groups'))
    
    return render_template('edit_group.html', group=group)

@app.route('/admin/delete_group/<int:group_id>', methods=['POST'])
def admin_delete_group(group_id):
    if not session.get('logged_in', False) or not session.get('is_admin', False):
        return redirect(url_for('login'))
    
    group = Group.query.get_or_404(group_id)
    
    # Check if group has students
    students = User.query.filter_by(group_id=group_id).all()
    if students:
        flash("Bu guruhda o'quvchilar mavjud! Avval ularni o'chiring yoki boshqa guruhga ko'chiring.", 'error')
        return redirect(url_for('admin_groups'))
    
    db.session.delete(group)
    db.session.commit()
    
    flash("Guruh o'chirildi!", 'success')
    return redirect(url_for('admin_groups'))

@app.route('/admin/subjects')
def admin_subjects():
    if not session.get('logged_in', False):
        return redirect(url_for('login'))
    
    # Allow only admin and group leaders
    user = User.query.get(session['user_id'])
    if not (user.is_admin or user.is_group_leader):
        flash("Bu sahifaga faqat admin va guruh rahbarlari kirishi mumkin!", 'error')
        return redirect(url_for('student_dashboard'))
    
    subjects = Subject.query.all()
    return render_template('admin_subjects.html', subjects=subjects)

@app.route('/admin/add_subject', methods=['POST'])
def admin_add_subject():
    if not session.get('logged_in', False) or not session.get('is_admin', False):
        return redirect(url_for('login'))
    
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    
    # Handle PDF file upload
    pdf_file = request.files.get('pdf_file')
    pdf_file_path = None
    pdf_filename = None
    
    if pdf_file and pdf_file.filename != '':
        if allowed_file(pdf_file.filename):
            filename = secure_filename(pdf_file.filename)
            # Add timestamp to make filename unique
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"
            
            upload_dir = ensure_upload_directory()
            file_path = os.path.join(upload_dir, filename)
            pdf_file.save(file_path)
            
            pdf_file_path = file_path
            pdf_filename = filename
        else:
            flash("Faqat PDF fayllariga ruxsat beriladi!", 'error')
            return redirect(url_for('admin_subjects'))
    
    # Create new subject
    new_subject = Subject(
        name=name, 
        description=description,
        pdf_file_path=pdf_file_path,
        pdf_filename=pdf_filename
    )
    db.session.add(new_subject)
    db.session.commit()
    
    flash("Fan muvaffaqiyatli qo'shildi!", 'success')
    return redirect(url_for('admin_subjects'))

@app.route('/admin/edit_subject/<int:subject_id>', methods=['GET', 'POST'])
def admin_edit_subject(subject_id):
    if not session.get('logged_in', False) or not session.get('is_admin', False):
        return redirect(url_for('login'))
    
    subject = Subject.query.get_or_404(subject_id)
    
    if request.method == 'POST':
        subject.name = request.form.get('name', '').strip()
        subject.description = request.form.get('description', '').strip()
        
        # Handle PDF file upload
        pdf_file = request.files.get('pdf_file')
        if pdf_file and pdf_file.filename != '':
            if allowed_file(pdf_file.filename):
                # Delete old PDF if exists
                if subject.pdf_file_path and os.path.exists(subject.pdf_file_path):
                    os.remove(subject.pdf_file_path)
                
                filename = secure_filename(pdf_file.filename)
                # Add timestamp to make filename unique
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{filename}"
                
                upload_dir = ensure_upload_directory()
                file_path = os.path.join(upload_dir, filename)
                pdf_file.save(file_path)
                
                subject.pdf_file_path = file_path
                subject.pdf_filename = filename
            else:
                flash("Faqat PDF fayllariga ruxsat beriladi!", 'error')
                return redirect(url_for('admin_subjects'))
        
        db.session.commit()
        flash("Fan ma'lumotlari yangilandi!", 'success')
        return redirect(url_for('admin_subjects'))
    
    return render_template('edit_subject.html', subject=subject)

@app.route('/uploads/pdfs/<filename>')
def download_pdf(filename):
    """Serve PDF files for download/viewing"""
    if not session.get('logged_in', False):
        return redirect(url_for('login'))
    
    upload_dir = ensure_upload_directory()
    file_path = os.path.join(upload_dir, filename)
    
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=False, mimetype='application/pdf')
    else:
        flash("PDF fayl topilmadi!", 'error')
        return redirect(url_for('student_dashboard'))

@app.route('/admin/parse_pdf/<int:subject_id>', methods=['GET', 'POST'])
def admin_parse_pdf(subject_id):
    """Parse PDF and extract questions for test generation"""
    if not session.get('logged_in', False) or not session.get('is_admin', False):
        return redirect(url_for('login'))
    
    subject = Subject.query.get_or_404(subject_id)
    
    if not subject.pdf_file_path or not os.path.exists(subject.pdf_file_path):
        flash("Bu fanga PDF fayl biriktirilmagan!", 'error')
        return redirect(url_for('admin_subjects'))
    
    if request.method == 'POST':
        # Import PDF parser with error handling
        try:
            from pdf_parser import PDFQuestionExtractor
            extractor = PDFQuestionExtractor()
            questions = extractor.parse_pdf_file(subject.pdf_file_path)
        except ImportError:
            flash("PDF parser mavjud emas! Iltimos, administrator bilan bog'laning.", 'error')
            return redirect(url_for('admin_subjects'))
        except Exception as e:
            flash(f"PDF ni parse qilishda xatolik: {str(e)}", 'error')
            return redirect(url_for('admin_subjects'))
        
        if not questions:
            flash("PDF dan savollarni ajratib bo'lmadi!", 'error')
            return redirect(url_for('admin_subjects'))
        
        # Store questions in session for review
        session['parsed_questions'] = questions
        session['subject_id'] = subject_id
        
        return render_template('review_parsed_questions.html', 
                             subject=subject, 
                             questions=questions)
    
    return render_template('parse_pdf_confirm.html', subject=subject)

@app.route('/admin/save_parsed_questions', methods=['POST'])
def admin_save_parsed_questions():
    """Save parsed questions as tests"""
    if not session.get('logged_in', False) or not session.get('is_admin', False):
        return redirect(url_for('login'))
    
    questions = session.get('parsed_questions', [])
    subject_id = session.get('subject_id')
    
    if not questions or not subject_id:
        flash("Savollar ma'lumotlari topilmadi!", 'error')
        return redirect(url_for('admin_subjects'))
    
    try:
        saved_count = 0
        for i, q_data in enumerate(questions):
            # Get correct answer from form
            correct_key = request.form.get(f'correct_answer_{i}')
            
            if correct_key and q_data['options']:
                # Create test with required fields
                new_test = Test(
                    title=f"Savol {i+1}",
                    subject_id=subject_id,
                    test_type='daily',
                    test_date=date.today(),
                    start_time=datetime.now().time(),
                    end_time=(datetime.now() + timedelta(hours=1)).time(),
                    duration_minutes=60,
                    is_active=True
                )
                db.session.add(new_test)
                db.session.flush()  # Get the test ID
                
                # Create question with options in existing structure
                # Map options to A, B, C, D format
                option_map = {}
                for opt_data in q_data['options']:
                    key = opt_data['key'].upper()
                    if key in ['A', 'B', 'C', 'D']:
                        option_map[key] = opt_data['text']
                
                # Ensure we have all 4 options
                option_a = option_map.get('A', '')
                option_b = option_map.get('B', '')
                option_c = option_map.get('C', '')
                option_d = option_map.get('D', '')
                
                if option_a and option_b and option_c and option_d:
                    question = Question(
                        text=q_data['question'],
                        option_a=option_a,
                        option_b=option_b,
                        option_c=option_c,
                        option_d=option_d,
                        correct_answer=correct_key.upper(),
                        test_id=new_test.id
                    )
                    db.session.add(question)
                    saved_count += 1
        
        db.session.commit()
        
        # Clear session
        session.pop('parsed_questions', None)
        session.pop('subject_id', None)
        
        flash(f"{saved_count} ta test muvaffaqiyatli saqlandi!", 'success')
        return redirect(url_for('admin_subjects'))
        
    except Exception as e:
        db.session.rollback()
        flash(f"Testlarni saqlashda xatolik: {str(e)}", 'error')
        return redirect(url_for('admin_subjects'))

@app.route('/admin/delete_subject/<int:subject_id>', methods=['POST'])
def admin_delete_subject(subject_id):
    if not session.get('logged_in', False) or not session.get('is_admin', False):
        return redirect(url_for('login'))
    
    subject = Subject.query.get_or_404(subject_id)
    
    # Check if subject has tests or topics
    if subject.tests or subject.topics:
        flash("Bu fanga testlar yoki mavzular bog'langan! Avval ularni o'chiring.", 'error')
        return redirect(url_for('admin_subjects'))
    
    db.session.delete(subject)
    db.session.commit()
    
    flash("Fan o'chirildi!", 'success')
    return redirect(url_for('admin_subjects'))

@app.route('/admin/topics')
def admin_topics():
    if not session.get('logged_in', False) or not session.get('is_admin', False):
        return redirect(url_for('login'))
    topics = Topic.query.all()
    subjects = Subject.query.all()
    return render_template('admin_topics.html', topics=topics, subjects=subjects)

@app.route('/admin/add_topic', methods=['POST'])
def admin_add_topic():
    if not session.get('logged_in', False) or not session.get('is_admin', False):
        return redirect(url_for('login'))
    
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()
    video_url = request.form.get('video_url', '').strip()
    subject_id = request.form.get('subject_id', type=int)
    
    # Create new topic
    new_topic = Topic(
        title=title,
        content=content,
        video_url=video_url,
        subject_id=subject_id
    )
    db.session.add(new_topic)
    db.session.commit()
    
    flash("Mavzu muvaffaqiyatli qo'shildi!", 'success')
    return redirect(url_for('admin_topics'))

@app.route('/admin/schedule')
def admin_schedule():
    if not session.get('logged_in', False) or not session.get('is_admin', False):
        return redirect(url_for('login'))
    schedules = Schedule.query.all()
    groups = Group.query.all()
    subjects = Subject.query.all()
    return render_template('admin_schedule.html', schedules=schedules, groups=groups, subjects=subjects)

@app.route('/admin/add_schedule', methods=['POST'])
def admin_add_schedule():
    if not session.get('logged_in', False) or not session.get('is_admin', False):
        return redirect(url_for('login'))
    
    day_of_week = request.form.get('day_of_week', '').strip()
    subject_id = request.form.get('subject_id', type=int)
    group_id = request.form.get('group_id', type=int)
    start_time_str = request.form.get('start_time', '').strip()
    end_time_str = request.form.get('end_time', '').strip()
    
    # Validate time strings
    if not start_time_str or not end_time_str:
        flash("Boshlanish va tugash vaqtini kiriting!", 'error')
        return redirect(url_for('admin_schedule'))
    
    # Parse time - handle different formats
    try:
        if 'T' in start_time_str:  # ISO format like '2026-02-22T07:00'
            start_time = datetime.fromisoformat(start_time_str).time()
        else:
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
    except ValueError:
        flash("Boshlanish vaqti noto'g'ri formatda! HH:MM formatida kiriting.", 'error')
        return redirect(url_for('admin_schedule'))
    
    try:
        if 'T' in end_time_str:  # ISO format like '2026-02-22T08:00'
            end_time = datetime.fromisoformat(end_time_str).time()
        else:
            end_time = datetime.strptime(end_time_str, '%H:%M').time()
    except ValueError:
        flash("Tugash vaqti noto'g'ri formatda! HH:MM formatida kiriting.", 'error')
        return redirect(url_for('admin_schedule'))
    
    # Create new schedule
    new_schedule = Schedule(
        day_of_week=day_of_week,
        subject_id=subject_id,
        group_id=group_id,
        start_time=start_time,
        end_time=end_time
    )
    db.session.add(new_schedule)
    db.session.commit()
    
    flash("Dars jadvali muvaffaqiyatli qo'shildi!", 'success')
    return redirect(url_for('admin_schedule'))

@app.route('/admin/backup')
def admin_backup():
    if not session.get('logged_in', False) or not session.get('is_admin', False):
        return redirect(url_for('login'))
    
    if backup_database():
        flash("Ma'lumotlar muvaffaqiyatlandi!", 'success')
    else:
        flash("Ma'lumotlarni saqlashda xatolik yuz berdi!", 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/restore')
def admin_restore():
    if not session.get('logged_in', False) or not session.get('is_admin', False):
        return redirect(url_for('login'))
    
    if restore_database():
        flash("Ma'lumotlar muvaffaqiyatlandi!", 'success')
    else:
        flash("Ma'lumotlarni tiklashda xatolik yuz berdi!", 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/tests')
def admin_tests():
    if not session.get('logged_in', False) or not session.get('is_admin', False):
        return redirect(url_for('login'))
    tests = Test.query.order_by(Test.test_date.desc()).all()
    subjects = Subject.query.all()
    return render_template('admin_tests.html', tests=tests, subjects=subjects)

@app.route('/admin/add_test', methods=['POST'])
def admin_add_test():
    if not session.get('logged_in', False) or not session.get('is_admin', False):
        return redirect(url_for('login'))
    
    title = request.form.get('title', '').strip()
    subject_id = request.form.get('subject_id', type=int)
    test_type = request.form.get('test_type', '').strip()
    test_date_str = request.form.get('test_date', '').strip()
    start_time_str = request.form.get('start_time', '').strip()
    end_time_str = request.form.get('end_time', '').strip()
    
    # Set duration based on test type
    if test_type == 'daily':
        duration_minutes = 60  # 1 hour for daily tests
    elif test_type == 'dtm':
        duration_minutes = 120  # 2 hours for DTM tests
    else:
        duration_minutes = request.form.get('duration_minutes', type=int, default=60)
    
    # Validate date and time strings
    if not test_date_str or not start_time_str or not end_time_str:
        flash("Sana, boshlanish va tugash vaqtini kiriting!", 'error')
        return redirect(url_for('admin_tests'))
    
    # Parse date
    try:
        test_date = datetime.strptime(test_date_str, '%Y-%m-%d').date()
    except ValueError:
        flash("Sana noto'g'ri formatda! YYYY-MM-DD formatida kiriting.", 'error')
        return redirect(url_for('admin_tests'))
    
    # Parse time - handle different formats
    try:
        if 'T' in start_time_str:  # ISO format like '2026-02-22T07:00'
            start_time = datetime.fromisoformat(start_time_str).time()
        else:
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
    except ValueError:
        flash("Boshlanish vaqti noto'g'ri formatda! HH:MM formatida kiriting.", 'error')
        return redirect(url_for('admin_tests'))
    
    try:
        if 'T' in end_time_str:  # ISO format like '2026-02-22T08:00'
            end_time = datetime.fromisoformat(end_time_str).time()
        else:
            end_time = datetime.strptime(end_time_str, '%H:%M').time()
    except ValueError:
        flash("Tugash vaqti noto'g'ri formatda! HH:MM formatida kiriting.", 'error')
        return redirect(url_for('admin_tests'))
    
    # Handle PDF file upload
    pdf_file = request.files.get('pdf_file')
    pdf_file_path = None
    pdf_filename = None
    
    if pdf_file and pdf_file.filename != '':
        if allowed_file(pdf_file.filename):
            filename = secure_filename(pdf_file.filename)
            # Add timestamp to make filename unique
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"
            
            upload_dir = ensure_upload_directory()
            file_path = os.path.join(upload_dir, filename)
            pdf_file.save(file_path)
            
            pdf_file_path = file_path
            pdf_filename = filename
        else:
            flash("Faqat PDF fayllariga ruxsat beriladi!", 'error')
            return redirect(url_for('admin_tests'))
    
    # Create new test
    new_test = Test(
        title=title,
        subject_id=subject_id,
        test_type=test_type,
        test_date=test_date,
        start_time=start_time,
        end_time=end_time,
        duration_minutes=duration_minutes,
        pdf_file_path=pdf_file_path,
        pdf_filename=pdf_filename
    )
    db.session.add(new_test)
    db.session.commit()
    
    if test_type == 'daily':
        flash("Test muvaffaqiyatli qo'shildi! (30 savol)", 'success')
    elif test_type == 'dtm':
        flash("Test muvaffaqiyatli qo'shildi! (90 savol)", 'success')
    else:
        flash(f"Test muvaffaqiyatli qo'shildi! ({duration_minutes} daqiqa)", 'success')
    return redirect(url_for('admin_tests'))

@app.route('/admin/edit_test/<int:test_id>', methods=['GET', 'POST'])
def admin_edit_test(test_id):
    if not session.get('logged_in', False) or not session.get('is_admin', False):
        return redirect(url_for('login'))
    
    test = Test.query.get_or_404(test_id)
    subjects = Subject.query.all()
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        subject_id = request.form.get('subject_id', type=int)
        test_type = request.form.get('test_type', '').strip()
        test_date_str = request.form.get('test_date', '').strip()
        start_time_str = request.form.get('start_time', '').strip()
        end_time_str = request.form.get('end_time', '').strip()
        
        # Validate required fields
        if not title or not test_type or not test_date_str or not start_time_str or not end_time_str:
            flash("Barcha maydonlarni to'ldiring!", 'error')
            return render_template('edit_test.html', test=test, subjects=subjects)
        
        # Set duration based on test type
        if test_type == 'daily':
            duration_minutes = 60  # 1 hour for daily tests
        elif test_type == 'dtm':
            duration_minutes = 120  # 2 hours for DTM tests
        else:
            duration_minutes = request.form.get('duration_minutes', type=int, default=60)
        
        # Parse date and time
        try:
            test_date = datetime.strptime(test_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash("Sana noto'g'ri formatda! YYYY-MM-DD formatida kiriting.", 'error')
            return render_template('edit_test.html', test=test, subjects=subjects)
        
        # Parse time - handle different formats
        try:
            if 'T' in start_time_str:  # ISO format
                start_time = datetime.fromisoformat(start_time_str).time()
            else:
                start_time = datetime.strptime(start_time_str, '%H:%M').time()
        except ValueError:
            flash("Boshlanish vaqti noto'g'ri formatda! HH:MM formatida kiriting.", 'error')
            return render_template('edit_test.html', test=test, subjects=subjects)
        
        try:
            if 'T' in end_time_str:  # ISO format
                end_time = datetime.fromisoformat(end_time_str).time()
            else:
                end_time = datetime.strptime(end_time_str, '%H:%M').time()
        except ValueError:
            flash("Tugash vaqti noto'g'ri formatda! HH:MM formatida kiriting.", 'error')
            return render_template('edit_test.html', test=test, subjects=subjects)
        
        # Update test
        test.title = title
        test.subject_id = subject_id
        test.test_type = test_type
        test.test_date = test_date
        test.start_time = start_time
        test.end_time = end_time
        test.duration_minutes = duration_minutes
        
        db.session.commit()
        flash("Test ma'lumotlari muvaffaqiyatli yangilandi!", 'success')
        return redirect(url_for('admin_tests'))
    
    return render_template('edit_test.html', test=test, subjects=subjects)

@app.route('/admin/delete_test/<int:test_id>', methods=['POST'])
def admin_delete_test(test_id):
    if not session.get('logged_in', False) or not session.get('is_admin', False):
        return redirect(url_for('login'))
    
    test = Test.query.get_or_404(test_id)
    
    # Delete related questions and results
    Question.query.filter_by(test_id=test_id).delete()
    TestResult.query.filter_by(test_id=test_id).delete()
    TestRegistration.query.filter_by(test_id=test_id).delete()
    
    db.session.delete(test)
    db.session.commit()
    
    flash("Test o'chirildi!", 'success')
    return redirect(url_for('admin_tests'))

@app.route('/admin/test_questions/<int:test_id>')
def admin_test_questions(test_id):
    if not session.get('logged_in', False) or not session.get('is_admin', False):
        return redirect(url_for('login'))
    
    test = Test.query.get_or_404(test_id)
    questions = Question.query.filter_by(test_id=test_id).all()
    
    return render_template('admin_test_questions.html', test=test, questions=questions)

@app.route('/admin/edit_question/<int:question_id>', methods=['GET', 'POST'])
def admin_edit_question(question_id):
    if not session.get('logged_in', False) or not session.get('is_admin', False):
        return redirect(url_for('login'))
    
    question = Question.query.get_or_404(question_id)
    test = question.test
    
    if request.method == 'POST':
        text = request.form.get('text', '').strip()
        option_a = request.form.get('option_a', '').strip()
        option_b = request.form.get('option_b', '').strip()
        option_c = request.form.get('option_c', '').strip()
        option_d = request.form.get('option_d', '').strip()
        correct_answer = request.form.get('correct_answer', '').strip()
        
        # Validate required fields
        if not text or not option_a or not option_b or not option_c or not option_d or not correct_answer:
            flash("Barcha maydonlarni to'ldiring!", 'error')
            return render_template('edit_question.html', question=question, test=test)
        
        # Validate correct answer
        if correct_answer not in ['A', 'B', 'C', 'D']:
            flash("To'g'ri javob A, B, C, yoki D bo'lishi kerak!", 'error')
            return render_template('edit_question.html', question=question, test=test)
        
        # Update question
        question.text = text
        question.option_a = option_a
        question.option_b = option_b
        question.option_c = option_c
        question.option_d = option_d
        question.correct_answer = correct_answer
        
        db.session.commit()
        flash("Savol muvaffaqiyatli yangilandi!", 'success')
        return redirect(url_for('admin_test_questions', test_id=test.id))
    
    return render_template('edit_question.html', question=question, test=test)

@app.route('/admin/delete_question/<int:question_id>', methods=['POST'])
def admin_delete_question(question_id):
    if not session.get('logged_in', False) or not session.get('is_admin', False):
        return redirect(url_for('login'))
    
    question = Question.query.get_or_404(question_id)
    test_id = question.test_id
    
    # Delete the question
    db.session.delete(question)
    db.session.commit()
    
    flash("Savol o'chirildi!", 'success')
    return redirect(url_for('admin_test_questions', test_id=test_id))

@app.route('/admin/add_question/<int:test_id>', methods=['POST'])
def admin_add_question(test_id):
    if not session.get('logged_in', False) or not session.get('is_admin', False):
        return redirect(url_for('login'))
    
    test = Test.query.get_or_404(test_id)
    
    text = request.form.get('text', '').strip()
    option_a = request.form.get('option_a', '').strip()
    option_b = request.form.get('option_b', '').strip()
    option_c = request.form.get('option_c', '').strip()
    option_d = request.form.get('option_d', '').strip()
    correct_answer = request.form.get('correct_answer', '').strip()
    
    # Create new question
    new_question = Question(
        text=text,
        option_a=option_a,
        option_b=option_b,
        option_c=option_c,
        option_d=option_d,
        correct_answer=correct_answer,
        test_id=test_id
    )
    db.session.add(new_question)
    db.session.commit()
    
    flash("Savol muvaffaqiyatli qo'shildi!", 'success')
    return redirect(url_for('admin_test_questions', test_id=test_id))

@app.route('/admin/test_registrations/<int:test_id>')
def admin_test_registrations(test_id):
    if not session.get('logged_in', False) or not session.get('is_admin', False):
        return redirect(url_for('login'))
    
    test = Test.query.get_or_404(test_id)
    registrations = TestRegistration.query.filter_by(test_id=test_id).all()
    
    return render_template('admin_test_registrations.html', test=test, registrations=registrations)

@app.route('/admin/test_results/<int:test_id>')
def admin_test_results(test_id):
    if not session.get('logged_in', False) or not session.get('is_admin', False):
        return redirect(url_for('login'))
    
    test = Test.query.get_or_404(test_id)
    results = TestResult.query.filter_by(test_id=test_id).order_by(TestResult.percentage.desc()).all()
    
    # Calculate statistics
    total_attempts = len(results)
    avg_score = 0
    pass_count = 0
    
    if total_attempts > 0:
        total_score = sum(r.score for r in results)
        avg_score = total_score / total_attempts
        pass_count = len([r for r in results if r.percentage >= 60])  # 60% passing
    
    return render_template('admin_test_results.html', 
                         test=test, 
                         results=results, 
                         total_attempts=total_attempts,
                         avg_score=avg_score,
                         pass_count=pass_count)

@app.route('/student/dashboard')
def student_dashboard():
    if not session.get('logged_in', False):
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    recent_results = TestResult.query.filter_by(user_id=user.id).order_by(TestResult.taken_at.desc()).limit(5).all()
    certificates = Certificate.query.filter_by(user_id=user.id).all()
    difficult_topics = DifficultTopic.query.filter_by(user_id=user.id).all()
    
    # Calculate average percentage
    all_results = TestResult.query.filter_by(user_id=user.id).all()
    avg_percentage = 0
    if all_results:
        avg_percentage = sum(r.percentage for r in all_results) / len(all_results)
    
    # Get group student rankings
    group_student_rankings = []
    if user.group_id:
        # Get all students in the same group (excluding admins and group leaders)
        group_students = User.query.filter_by(group_id=user.group_id, is_admin=False, is_group_leader=False).all()
        
        for student in group_students:
            results = TestResult.query.filter_by(user_id=student.id).all()
            avg_percentage = 0
            if results:
                avg_percentage = sum(r.percentage for r in results) / len(results)
            
            total_points = sum(r.points_earned for r in results)
            
            group_student_rankings.append({
                'student': student,
                'avg_percentage': avg_percentage,
                'total_points': total_points,
                'total_tests': len(results)
            })
        
        # Sort by average percentage and assign ranks
        group_student_rankings.sort(key=lambda x: x['avg_percentage'], reverse=True)
        for i, ranking in enumerate(group_student_rankings, 1):
            ranking['rank'] = i
    
    return render_template('student_dashboard.html',
                         user=user,
                         recent_results=recent_results,
                         certificates=certificates,
                         difficult_topics=difficult_topics,
                         avg_percentage=avg_percentage,
                         group_student_rankings=group_student_rankings)

@app.route('/subjects')
def subjects():
    if not session.get('logged_in', False):
        return redirect(url_for('login'))
    
    subjects = Subject.query.all()
    return render_template('subjects_enhanced.html', subjects=subjects)

@app.route('/subject/<int:subject_id>')
def subject_detail(subject_id):
    if not session.get('logged_in', False):
        return redirect(url_for('login'))
    subject = Subject.query.get_or_404(subject_id)
    topics = Topic.query.filter_by(subject_id=subject_id).all()
    user = User.query.get(session['user_id'])
    
    # Get difficult topics for this user
    difficult_topic_ids = [dt.topic_id for dt in DifficultTopic.query.filter_by(user_id=user.id).all()]
    
    return render_template('subject_detail_enhanced.html',
                         subject=subject,
                         topics=topics,
                         difficult_topic_ids=difficult_topic_ids)

@app.route('/tests')
def tests():
    if not session.get('logged_in', False):
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    # Get current week dates
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())  # Monday
    week_days = []
    
    day_names = ['Dushanba', 'Seshanba', 'Chorshanba', 'Payshanba', 'Juma', 'Shanba', 'Yakshanba']
    
    for i in range(7):
        current_date = week_start + timedelta(days=i)
        week_days.append({
            'day_number': i + 1,
            'day_name': day_names[i],
            'date': current_date,
            'date_str': current_date.strftime('%d.%m.%Y')
        })
    
    # Create weekly schedule if needed
    create_weekly_schedule_for_group(user.group_id, week_start)
    
    # Get weekly test schedules for user's group
    weekly_schedules = WeeklyTestSchedule.query.filter_by(
        group_id=user.group_id,
        week_start_date=week_start
    ).order_by(WeeklyTestSchedule.day_number).all()
    
    # Check user results
    user_results = {result.test_id: result for result in TestResult.query.filter_by(user_id=user.id).all()}
    
    # Create schedule data for template
    schedule_data = []
    for day_data in week_days:
        day_schedule = {
            'day_number': day_data['day_number'],
            'day_name': day_data['day_name'],
            'date': day_data['date'],
            'date_str': day_data['date_str'],
            'test': None,
            'status': 'Bajarilmagan',
            'result': None,
            'is_available': False
        }
        
        # Find test for this day
        day_schedule_item = next((ws for ws in weekly_schedules if ws.day_number == day_data['day_number']), None)
        
        if day_schedule_item:
            test = day_schedule_item.test
            day_schedule['test'] = test
            
            # Check if test is available (today and within time)
            if day_data['date'] == today:
                now = datetime.now()
                test_start = datetime.combine(test.test_date, test.start_time)
                test_end = datetime.combine(test.test_date, test.end_time)
                day_schedule['is_available'] = test_start <= now <= test_end
            
            # Check completion status
            if test.id in user_results:
                result = user_results[test.id]
                day_schedule['result'] = result
                day_schedule['status'] = f'Bajarilgan ({result.percentage}%)'
            elif day_schedule_item.is_completed:
                day_schedule['status'] = 'Bajarilgan'
            elif day_data['date'] < today:
                day_schedule['status'] = 'O\'tkazib yuborilgan'
        
        schedule_data.append(day_schedule)
    
    return render_template('weekly_tests.html', schedule_data=schedule_data, week_start=week_start, timedelta=timedelta, today=today)

@app.route('/register_for_test/<int:test_id>', methods=['POST'])
def register_for_test(test_id):
    if not session.get('logged_in', False):
        if request.headers.get('Content-Type') == 'application/x-www-form-urlencoded':
            return jsonify({'error': 'Unauthorized'}), 401
        return redirect(url_for('login'))
    
    test = Test.query.get_or_404(test_id)
    user = User.query.get(session['user_id'])
    
    # Check if already registered
    existing = TestRegistration.query.filter_by(user_id=user.id, test_id=test_id).first()
    if existing:
        if request.headers.get('Content-Type') == 'application/x-www-form-urlencoded':
            return jsonify({'error': 'Siz bu testga allaqachon ro\'yxatdan o\'tgansiz!'}), 400
        flash("Siz bu testga allaqachon ro'yxatdan o'tgansiz!", 'info')
        return redirect(url_for('tests'))
    
    # Check if test is still open for registration
    now = datetime.now()
    test_datetime = datetime.combine(test.test_date, test.start_time)
    
    if now > test_datetime:
        if request.headers.get('Content-Type') == 'application/x-www-form-urlencoded':
            return jsonify({'error': 'Testga ro\'yxatdan o\'tish vaqti tugagan!'}), 400
        flash("Testga ro'yxatdan o'tish vaqti tugagan!", 'error')
        return redirect(url_for('tests'))
    
    # Register for test
    registration = TestRegistration(user_id=user.id, test_id=test_id)
    db.session.add(registration)
    db.session.commit()
    
    # Return JSON for AJAX requests
    if request.headers.get('Content-Type') == 'application/x-www-form-urlencoded':
        return jsonify({'success': True, 'message': 'Testga muvaffaqiyatli ro\'yxatdan o\'tdingiz!'})
    
    flash("Testga muvaffaqiyatli ro'yxatdan o'tdingiz!", 'success')
    return redirect(url_for('tests'))

@app.route('/take_test/<int:test_id>')
def take_test(test_id):
    if not session.get('logged_in', False):
        return redirect(url_for('login'))
    
    test = Test.query.get_or_404(test_id)
    user = User.query.get(session['user_id'])
    
    # Check if user is registered
    registration = TestRegistration.query.filter_by(user_id=user.id, test_id=test_id).first()
    if not registration:
        flash("Siz bu testga ro'yxatdan o'tmagansiz!", 'error')
        return redirect(url_for('tests'))
    
    # Check if test is available now
    now = datetime.now()
    test_start = datetime.combine(test.test_date, test.start_time)
    test_end = datetime.combine(test.test_date, test.end_time)
    
    if now < test_start:
        flash("Test hali boshlanmagan!", 'error')
        return redirect(url_for('tests'))
    elif now > test_end:
        flash("Test tugagan!", 'error')
        return redirect(url_for('tests'))
    
    # Check if already taken
    existing_result = TestResult.query.filter_by(user_id=user.id, test_id=test_id).first()
    if existing_result:
        flash("Siz bu testni allaqachon topshirgansiz!", 'info')
        return redirect(url_for('tests'))
    
    questions = Question.query.filter_by(test_id=test_id).all()
    
    return render_template('take_test.html', test=test, questions=questions)

@app.route('/submit_test/<int:test_id>', methods=['POST'])
def submit_test(test_id):
    if not session.get('logged_in', False):
        return redirect(url_for('login'))
    
    test = Test.query.get_or_404(test_id)
    user = User.query.get(session['user_id'])
    questions = Question.query.filter_by(test_id=test_id).all()
    
    # Check if test is still available
    now = datetime.now()
    test_end = datetime.combine(test.test_date, test.end_time)
    
    if now > test_end:
        flash("Test tugagan! Javoblar qabul qilinmadi.", 'error')
        return redirect(url_for('tests'))
    
    score = 0
    for question in questions:
        user_answer = request.form.get(f'question_{question.id}')
        if user_answer == question.correct_answer:
            score += 1
    
    percentage = (score / len(questions)) * 100
    
    # Calculate points based on test type
    points_earned = 0
    if test.test_type == 'dtm':
        # For DTM tests, we'll calculate points later based on ranking
        points_earned = 0
    elif test.test_type == 'daily':
        points_earned = calculate_daily_points(percentage)
    
    # Save result
    result = TestResult(
        score=score,
        total_questions=len(questions),
        percentage=percentage,
        points_earned=points_earned,
        user_id=user.id,
        test_id=test_id
    )
    db.session.add(result)
    db.session.commit()
    
    # Update group score
    if points_earned > 0:
        user.group.total_score += points_earned
        db.session.commit()
    
    # For DTM tests, recalculate points for all participants
    if test.test_type == 'dtm':
        update_dtm_points(test_id)
    
    flash(f"Test muvaffaqiyatli topshirildi! Natijangiz: {score}/{len(questions)} ({percentage:.1f}%)", 'success')
    return redirect(url_for('test_result', result_id=result.id))

@app.route('/test_results')
def test_results():
    if not session.get('logged_in', False):
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    user_results = TestResult.query.filter_by(user_id=user.id).order_by(TestResult.taken_at.desc()).all()
    
    return render_template('test_results.html', user_results=user_results)

@app.route('/all_test_results')
def all_test_results():
    if not session.get('logged_in', False):
        return redirect(url_for('login'))
    
    # Get all test results with user and test information
    all_results = db.session.query(
        TestResult, User, Test, Subject
    ).join(User, TestResult.user_id == User.id)\
     .join(Test, TestResult.test_id == Test.id)\
     .outerjoin(Subject, Test.subject_id == Subject.id)\
     .order_by(TestResult.taken_at.desc()).all()
    
    # Calculate total points for each student
    student_totals = {}
    for result, user, test, subject in all_results:
        if user.id not in student_totals:
            student_totals[user.id] = {
                'user': user,
                'total_points': 0,
                'total_tests': 0,
                'total_questions': 0,
                'total_correct': 0
            }
        student_totals[user.id]['total_points'] += result.points_earned
        student_totals[user.id]['total_tests'] += 1
        student_totals[user.id]['total_questions'] += result.total_questions
        student_totals[user.id]['total_correct'] += result.score
    
    return render_template('all_test_results.html', 
                         all_results=all_results,
                         student_totals=student_totals)

def update_dtm_points(test_id):
    """Update DTM test points based on rankings"""
    results = TestResult.query.filter_by(test_id=test_id).order_by(TestResult.percentage.desc()).all()
    
    for i, result in enumerate(results, 1):
        result.points_earned = calculate_dtm_points(i, len(results))
    
    # Update group scores
    for result in results:
        if result.points_earned > 0:
            result.student.group.total_score += result.points_earned
    
    db.session.commit()

@app.route('/test_result/<int:result_id>')
def test_result(result_id):
    if not session.get('logged_in', False):
        return redirect(url_for('login'))
    result = TestResult.query.get_or_404(result_id)
    return render_template('test_result.html', result=result)

@app.route('/mark_difficult/<int:topic_id>')
def mark_difficult(topic_id):
    if not session.get('logged_in', False):
        return redirect(url_for('login'))
    user_id = session['user_id']
    
    # Check if already marked
    existing = DifficultTopic.query.filter_by(user_id=user_id, topic_id=topic_id).first()
    
    if existing:
        db.session.delete(existing)
        flash('Mavzu qiyinlar ro\'yxatidan olib tashlandi', 'info')
    else:
        difficult = DifficultTopic(user_id=user_id, topic_id=topic_id)
        db.session.add(difficult)
        flash('Mavzu qiyinlar ro\'yxatiga qo\'shildi', 'success')
    
    db.session.commit()
    return redirect(request.referrer)

@app.route('/create_difficult_topic_test/<int:topic_id>')
def create_difficult_topic_test(topic_id):
    if not session.get('logged_in', False):
        return redirect(url_for('login'))
    
    topic = Topic.query.get_or_404(topic_id)
    user = User.query.get(session['user_id'])
    
    # Create a practice test for this difficult topic
    test_title = f"{topic.title} - Qiyin mavzu bo'yicha mashq testi"
    
    # Check if a similar test already exists for this user
    existing_test = Test.query.filter_by(
        title=test_title,
        test_type='practice',
        subject_id=topic.subject_id
    ).first()
    
    if existing_test:
        flash('Bu mavzu uchun allaqachon test yaratilgan', 'info')
        return redirect(url_for('subject_detail', subject_id=topic.subject_id))
    
    # Create new practice test
    practice_test = Test(
        title=test_title,
        subject_id=topic.subject_id,
        test_type='practice',
        test_date=datetime.now().date(),
        start_time=datetime.now().time(),
        end_time=(datetime.now() + timedelta(hours=2)).time(),
        duration_minutes=120
    )
    db.session.add(practice_test)
    db.session.flush()
    
    # Create 10 practice questions for this topic
    questions = generate_topic_questions(topic, 10)
    
    for q_data in questions:
        question = Question(
            text=q_data['text'],
            option_a=q_data['options'][0],
            option_b=q_data['options'][1],
            option_c=q_data['options'][2],
            option_d=q_data['options'][3],
            correct_answer=q_data['correct'],
            test_id=practice_test.id
        )
        db.session.add(question)
    
    db.session.commit()
    
    flash(f"{topic.title} mavzusi uchun mashq testi yaratildi! Testlar bo'limida topshirishingiz mumkin.", 'success')
    return redirect(url_for('tests'))

def generate_topic_questions(topic, count):
    """Generate practice questions based on topic content"""
    subject_name = topic.subject.name if topic.subject else 'General'
    base_questions = get_subject_questions(subject_name, min(count * 2, 20))
    
    # Customize questions based on topic content
    topic_questions = []
    for i in range(min(count, len(base_questions))):
        q = base_questions[i].copy()
        q['text'] = f"[{topic.title}] {q['text']}"
        topic_questions.append(q)
    
    return topic_questions[:count]

@app.route('/schedule')
def schedule():
    if not session.get('logged_in', False):
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    
    # Check if user can edit (admin or group leader)
    can_edit = user.is_admin or user.is_group_leader
    
    # Show school timetable instead of test schedule
    return render_template('school_timetable.html', user=user, can_edit=can_edit)

@app.route('/admin/update_schedule', methods=['POST'])
def admin_update_schedule():
    if not session.get('logged_in', False) or not session.get('is_admin', False):
        return jsonify({'success': False, 'message': 'Ruxsat yo\'q'})
    
    try:
        # Delete all existing tests
        Test.query.delete()
        Question.query.delete()
        TestRegistration.query.delete()
        TestResult.query.delete()
        
        # Create new schedule
        create_test_schedule()
        
        return jsonify({'success': True, 'message': 'Jadval muvaffaqiyatli yangilandi'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

def update_weekly_schedule():
    """Auto-update weekly test schedule"""
    # Check if we need to update (start of new week)
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday())  # Monday
    
    # Check if we have tests for this week
    existing_tests = Test.query.filter(
        Test.test_date >= start_of_week,
        Test.test_date < start_of_week + timedelta(days=7)
    ).first()
    
    if not existing_tests:
        # Create new weekly schedule
        create_test_schedule()
        print("New weekly test schedule created")

@app.route('/upload_certificate', methods=['GET', 'POST'])
def upload_certificate():
    if not session.get('logged_in', False):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        level = request.form.get('level', '').strip()
        
        # Create new certificate
        new_certificate = Certificate(
            title=title,
            description=description,
            level=level,
            user_id=session['user_id']
        )
        db.session.add(new_certificate)
        db.session.commit()
        
        # Update group score
        user = User.query.get(session['user_id'])
        user.group.total_score += 10
        db.session.commit()
        
        flash("Sertifikat muvaffaqiyatli qo'shildi!", 'success')
        return redirect(url_for('student_dashboard'))
    
    return render_template('upload_certificate.html')

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if not session.get('logged_in', False):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        current_password = request.form.get('current_password', '').strip()
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        user = User.query.get(session['user_id'])
        
        if not check_password_hash(user.password_hash, current_password):
            flash("Joriy parol noto'g'ri!", 'error')
            return redirect(url_for('change_password'))
        
        if new_password != confirm_password:
            flash("Yangi parollar mos kelmadi!", 'error')
            return redirect(url_for('change_password'))
        
        user.password_hash = generate_password_hash(new_password)
        user.needs_password_change = False
        db.session.commit()
        
        flash("Parol muvaffaqiyatli o'zgartirildi!", 'success')
        return redirect(url_for('student_dashboard'))
    
    return render_template('change_password.html')

@app.route('/group_leader/dashboard')
def group_leader_dashboard():
    if not session.get('logged_in', False) or not session.get('is_group_leader', False):
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    # Get group members (excluding group leaders)
    group_members = User.query.filter_by(group_id=user.group_id, is_admin=False, is_group_leader=False).all()
    
    # Calculate group statistics
    total_members = len(group_members)
    
    # Get recent test results for group
    group_student_ids = [s.id for s in group_members]
    recent_group_results = TestResult.query.filter(TestResult.user_id.in_(group_student_ids)).order_by(TestResult.taken_at.desc()).limit(10).all()
    
    # Calculate group average
    all_group_results = TestResult.query.filter(TestResult.user_id.in_(group_student_ids)).all()
    avg_percentage = 0
    if all_group_results:
        avg_percentage = sum(r.percentage for r in all_group_results) / len(all_group_results)
    
    return render_template('group_leader_dashboard.html',
                         user=user,
                         group_members=group_members,
                         total_members=total_members,
                         avg_percentage=avg_percentage,
                         recent_group_results=recent_group_results)

@app.route('/group_rating')
def group_rating():
    if not session.get('logged_in', False):
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    # Get all groups
    groups = Group.query.all()
    group_data = []
    
    for group in groups:
        # Get group leader
        group_leader = User.query.filter_by(group_id=group.id, is_group_leader=True).first()
        
        # Get regular students in group
        regular_students = User.query.filter_by(group_id=group.id, is_admin=False, is_group_leader=False).all()
        total_students = len(regular_students)
        
        # Calculate student rankings within group
        student_rankings = []
        for student in regular_students:
            results = TestResult.query.filter_by(user_id=student.id).all()
            avg_percentage = 0
            if results:
                avg_percentage = sum(r.percentage for r in results) / len(results)
            
            total_points = sum(r.points_earned for r in results)
            
            student_rankings.append({
                'student': student,
                'avg_percentage': avg_percentage,
                'total_points': total_points,
                'total_tests': len(results)
            })
        
        # Sort students within group by average percentage
        student_rankings.sort(key=lambda x: x['avg_percentage'], reverse=True)
        for i, ranking in enumerate(student_rankings, 1):
            ranking['rank'] = i
        
        # Calculate group average
        student_ids = [s.id for s in regular_students]
        test_results = TestResult.query.filter(TestResult.user_id.in_(student_ids)).all()
        
        avg_percentage = 0
        if test_results:
            avg_percentage = sum(r.percentage for r in test_results) / len(test_results)
        
        group_data.append({
            'group': group,
            'group_leader': group_leader,
            'total_students': total_students,
            'avg_percentage': avg_percentage,
            'total_tests': len(test_results),
            'student_rankings': student_rankings
        })
    
    group_data.sort(key=lambda x: x['avg_percentage'], reverse=True)
    
    return render_template('group_rating.html', group_data=group_data)

@app.route('/groups_rating')
def groups_rating():
    return group_rating()

@app.route('/overall_rating')
def overall_rating():
    if not session.get('logged_in', False):
        return redirect(url_for('login'))
    
    # Get all regular students
    students = User.query.filter_by(is_admin=False, is_group_leader=False).all()
    student_data = []
    
    for student in students:
        # Calculate average percentage
        results = TestResult.query.filter_by(user_id=student.id).all()
        avg_percentage = 0
        if results:
            avg_percentage = sum(r.percentage for r in results) / len(results)
        
        total_points = sum(r.points_earned for r in results)
        
        # Get best test result
        best_result = None
        if results:
            best_result = max(results, key=lambda x: x.percentage)
        
        student_data.append({
            'student': student,
            'avg_percentage': avg_percentage,
            'total_points': total_points,
            'total_tests': len(results),
            'best_result': best_result,
            'rank': 0  # Will be set after sorting
        })
    
    # Sort by average percentage and assign ranks
    student_data.sort(key=lambda x: x['avg_percentage'], reverse=True)
    for i, data in enumerate(student_data, 1):
        data['rank'] = i
    
    return render_template('overall_rating.html', student_data=student_data)

    if not session.get('logged_in', False):
        return redirect(url_for('login'))
    
    if session.get('is_admin', False):
        return redirect(url_for('admin_dashboard'))
    
    try:
        # Get recent test results
        recent_results = TestResult.query.filter_by(user_id=session['user_id'])\
            .order_by(TestResult.taken_at.desc())\
            .limit(5).all()
        
        # Get certificates
        certificates = Certificate.query.filter_by(user_id=session['user_id']).all()
        
        # Get difficult topics
        difficult_topics = DifficultTopic.query.filter_by(user_id=session['user_id']).all()
        
        # Get user's group and group ranking
        user = User.query.get(session['user_id'])
        group_students = User.query.filter_by(group_id=user.group_id, is_admin=False, is_group_leader=False).all()
        
        # Calculate user's rank in group
        user_scores = {}
        for student in group_students:
            total_score = TestResult.query.filter_by(user_id=student.id)\
                .with_entities(db.func.sum(TestResult.points_earned)).scalar() or 0
            user_scores[student.id] = total_score
        
        sorted_users = sorted(user_scores.items(), key=lambda x: x[1], reverse=True)
        user_rank = next((i+1 for i, (uid, score) in enumerate(sorted_users) if uid == user.id), 0)
        
        return render_template('student_dashboard.html',
                             recent_results=recent_results,
                             certificates=certificates,
                             difficult_topics=difficult_topics,
                             user=user,
                             group_rank=user_rank,
                             total_group_students=len(group_students))
                             
    except Exception as e:
        app.logger.error(f"Student dashboard error: {str(e)}")
        return render_template('student_dashboard.html', error="Dashboard yuklashda xatolik")


@app.route('/logout')
def logout():
    session.clear()
    flash('Siz tizimdan chiqdingiz', 'info')
    return redirect(url_for('login'))

# Student Test Routes
@app.route('/student/tests', methods=['GET'])
def student_tests():
    """Student tests page"""
    if not session.get('logged_in', False) or session.get('is_admin', False):
        flash('Bu sahifa faqat o\'quvchilar uchun', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    tests = Test.query.all()
    results = TestResult.query.filter_by(user_id=session.get('user_id')).all()
    
    return render_template('student_tests.html', tests=tests, results=results)

@app.route('/student/take_test/<int:test_id>', methods=['GET', 'POST'])
def student_take_test(test_id):
    """Take a test"""
    if not session.get('logged_in', False) or session.get('is_admin', False):
        flash('Bu sahifa faqat o\'quvchilar uchun', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    test = Test.query.get_or_404(test_id)
    user_id = session.get('user_id')
    
    # Check if user already took this test
    existing_result = TestResult.query.filter_by(user_id=user_id, test_id=test_id).first()
    if existing_result:
        flash('Siz bu testni allaqachon topshirgansiz', 'info')
        return redirect(url_for('student_test_result', result_id=existing_result.id))
    
    if request.method == 'POST':
        # Process test submission
        score = 0
        total_questions = len(test.questions)
        
        for question in test.questions:
            selected_answer = request.form.get(f'question_{question.id}')
            if selected_answer == question.correct_answer:
                score += 1
        
        # Create test result
        result = TestResult(
            user_id=user_id,
            test_id=test_id,
            score=score,
            total_questions=total_questions,
            percentage=(score / total_questions) * 100,
            points_earned=calculate_daily_points((score / total_questions) * 100),
            taken_at=datetime.utcnow()
        )
        db.session.add(result)
        db.session.commit()
        
        flash(f'Test muvaffaqiyatli yakunlandi! To\'g\'ri javoblar: {score}/{total_questions}', 'success')
        return redirect(url_for('student_test_result', result_id=result.id))
    
    return render_template('take_test.html', test=test)

@app.route('/student/test_result/<int:result_id>', methods=['GET'])
def student_test_result(result_id):
    """View test result"""
    if not session.get('logged_in', False) or session.get('is_admin', False):
        flash('Bu sahifa faqat o\'quvchilar uchun', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    result = TestResult.query.get_or_404(result_id)
    
    # Check if result belongs to current user
    if result.user_id != session.get('user_id'):
        flash('Bu natijani ko\'rishga huquqingiz yo\'q', 'danger')
        return redirect(url_for('student_tests'))
    
    return render_template('test_result.html', result=result)


@app.route('/ai_section')
def ai_section():
    if not session.get('logged_in', False):
        return redirect(url_for('login'))
    
    return render_template('ai_section.html', 
                         topics=Topic.query.all(),
                         chat_history=get_chat_history())

@app.route('/ai_assistant')
def ai_assistant():
    if not session.get('logged_in', False):
        return redirect(url_for('login'))
    
    return render_template('ai_assistant.html', 
                         subjects=Subject.query.all(),
                         topics=Topic.query.all(),
                         chat_history=get_chat_history(),
                         CHATGPT_AVAILABLE=CHATGPT_AVAILABLE)

@app.route('/ai_assistant_enhanced')
def ai_assistant_enhanced():
    if not session.get('logged_in', False):
        return redirect(url_for('login'))
    
    return render_template('ai_assistant_enhanced.html', 
                         CHATGPT_AVAILABLE=CHATGPT_AVAILABLE)

@app.route('/api/subjects')
def api_subjects():
    """API endpoint to get all subjects"""
    if not session.get('logged_in', False):
        return jsonify({'error': 'Unauthorized'}), 401
    
    subjects = Subject.query.all()
    return jsonify({
        'success': True,
        'subjects': [{'id': s.id, 'name': s.name, 'description': s.description} for s in subjects]
    })

@app.route('/api/topics/<int:subject_id>')
def api_topics(subject_id):
    """API endpoint to get topics for a specific subject"""
    if not session.get('logged_in', False):
        return jsonify({'error': 'Unauthorized'}), 401
    
    topics = Topic.query.filter_by(subject_id=subject_id).all()
    return jsonify({
        'success': True,
        'topics': [{'id': t.id, 'title': t.title, 'content': t.content} for t in topics]
    })

@app.route('/api/all_topics')
def api_all_topics():
    """API endpoint to get all topics with subject names"""
    if not session.get('logged_in', False):
        return jsonify({'error': 'Unauthorized'}), 401
    
    topics = db.session.query(Topic, Subject).join(Subject).all()
    return jsonify({
        'success': True,
        'topics': [{'id': t.id, 'title': t.title, 'subject_name': s.name} for t, s in topics]
    })

@app.route('/api/add_subject', methods=['POST'])
def api_add_subject():
    """API endpoint to add a new subject"""
    if not session.get('logged_in', False):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        name = request.form.get('subject_name', '').strip()
        description = request.form.get('subject_description', '').strip()
        
        if not name:
            return jsonify({'error': 'Fan nomi kiritilishi shart'}), 400
        
        # Check if subject already exists
        if Subject.query.filter_by(name=name).first():
            return jsonify({'error': 'Bu fan allaqachon mavjud'}), 400
        
        # Create new subject
        subject = Subject(name=name, description=description)
        db.session.add(subject)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'subject': {'id': subject.id, 'name': subject.name, 'description': subject.description}
        })
        
    except Exception as e:
        app.logger.error(f"Error adding subject: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/add_topic', methods=['POST'])
def api_add_topic():
    """API endpoint to add a new topic"""
    if not session.get('logged_in', False):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        subject_id = request.form.get('subject_id', type=int)
        title = request.form.get('topic_title', '').strip()
        content = request.form.get('topic_content', '').strip()
        video_url = request.form.get('topic_video_url', '').strip()
        
        if not subject_id or not title:
            return jsonify({'error': 'Fan ID va mavzu nomi kiritilishi shart'}), 400
        
        # Check if subject exists
        subject = Subject.query.get(subject_id)
        if not subject:
            return jsonify({'error': 'Fan topilmadi'}), 404
        
        # Handle PDF file upload
        pdf_file = request.files.get('pdf_file')
        pdf_file_path = None
        pdf_filename = None
        
        if pdf_file and pdf_file.filename != '':
            if allowed_file(pdf_file.filename):
                filename = secure_filename(pdf_file.filename)
                # Add timestamp to make filename unique
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{filename}"
                
                upload_dir = ensure_upload_directory()
                file_path = os.path.join(upload_dir, filename)
                pdf_file.save(file_path)
                
                pdf_file_path = file_path
                pdf_filename = filename
            else:
                return jsonify({'error': 'Faqat PDF fayllariga ruxsat beriladi!'}), 400
        
        # Create new topic
        topic = Topic(
            title=title,
            content=content,
            video_url=video_url if video_url else None,
            subject_id=subject_id,
            pdf_file_path=pdf_file_path,
            pdf_filename=pdf_filename
        )
        db.session.add(topic)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'topic': {'id': topic.id, 'title': topic.title, 'content': topic.content}
        })
        
    except Exception as e:
        app.logger.error(f"Error adding topic: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/test_result/<int:result_id>')
def api_test_result(result_id):
    """API endpoint to get detailed test result"""
    if not session.get('logged_in', False):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        result = TestResult.query.get_or_404(result_id)
        
        # Check if result belongs to current user
        if result.user_id != session['user_id']:
            return jsonify({'error': 'Unauthorized'}), 401
        
        # Get test details
        test = result.test
        subject_name = test.subject.name if test.subject else 'Fan yo\'q'
        
        return jsonify({
            'success': True,
            'result': {
                'score': result.score,
                'total_questions': result.total_questions,
                'percentage': result.percentage,
                'points_earned': result.points_earned,
                'taken_at': result.taken_at.strftime('%d.%m.%Y %H:%M')
            },
            'test_title': test.title,
            'subject_name': subject_name
        })
        
    except Exception as e:
        app.logger.error(f"Error getting test result: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/test_status/<int:test_id>')
def api_test_status(test_id):
    """API endpoint to get real-time test status"""
    if not session.get('logged_in', False):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        test = Test.query.get_or_404(test_id)
        user_id = session['user_id']
        
        # Check user registration and result
        registration = TestRegistration.query.filter_by(user_id=user_id, test_id=test_id).first()
        result = TestResult.query.filter_by(user_id=user_id, test_id=test_id).first()
        
        # Check availability
        now = datetime.now()
        test_start = datetime.combine(test.test_date, test.start_time)
        test_end = datetime.combine(test.test_date, test.end_time)
        
        is_available = test_start <= now <= test_end
        is_expired = now > test_end
        
        return jsonify({
            'success': True,
            'is_available': is_available,
            'is_expired': is_expired,
            'is_registered': registration is not None,
            'has_result': result is not None,
            'result': {
                'score': result.score,
                'total_questions': result.total_questions,
                'percentage': result.percentage
            } if result else None
        })
        
    except Exception as e:
        app.logger.error(f"Error getting test status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/test_stats')
def api_test_stats():
    """API endpoint to get test statistics"""
    if not session.get('logged_in', False):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        user_id = session['user_id']
        now = datetime.now()
        
        # Get all tests
        all_tests = Test.query.all()
        
        # Get user registrations and results
        user_registrations = TestRegistration.query.filter_by(user_id=user_id).all()
        user_results = TestResult.query.filter_by(user_id=user_id).all()
        
        # Calculate stats
        available_count = 0
        registered_count = len(user_registrations)
        completed_count = len(user_results)
        
        for test in all_tests:
            test_start = datetime.combine(test.test_date, test.start_time)
            test_end = datetime.combine(test.test_date, test.end_time)
            
            if test_start <= now <= test_end:
                # Check if not already registered or completed
                is_registered = any(reg.test_id == test.id for reg in user_registrations)
                has_result = any(res.test_id == test.id for res in user_results)
                
                if not is_registered and not has_result:
                    available_count += 1
        
        # Calculate average score
        if user_results:
            average_score = sum(result.percentage for result in user_results) / len(user_results)
        else:
            average_score = 0
        
        return jsonify({
            'success': True,
            'available_count': available_count,
            'registered_count': registered_count,
            'completed_count': completed_count,
            'average_score': round(average_score, 1)
        })
        
    except Exception as e:
        app.logger.error(f"Error getting test stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/topic/<int:topic_id>')
def api_get_topic(topic_id):
    """API endpoint to get topic details"""
    if not session.get('logged_in', False):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        topic = Topic.query.get_or_404(topic_id)
        
        return jsonify({
            'success': True,
            'topic': {
                'id': topic.id,
                'title': topic.title,
                'content': topic.content,
                'video_url': topic.video_url,
                'pdf_file': topic.pdf_file
            }
        })
        
    except Exception as e:
        app.logger.error(f"Error getting topic: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/edit_topic', methods=['POST'])
def api_edit_topic():
    """API endpoint to edit a topic"""
    if not session.get('logged_in', False):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        topic_id = request.form.get('topic_id', type=int)
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        video_url = request.form.get('video_url', '').strip()
        pdf_file = request.files.get('pdf_file')
        remove_pdf = request.form.get('remove_pdf_file') == 'on'
        
        if not topic_id or not title:
            return jsonify({'error': 'Mavzu ID va nomi kiritilishi shart'}), 400
        
        topic = Topic.query.get_or_404(topic_id)
        
        # Update topic
        topic.title = title
        topic.content = content
        topic.video_url = video_url if video_url else None
        
        # Handle PDF file
        if remove_pdf:
            # Remove existing PDF
            if topic.pdf_file_path and os.path.exists(topic.pdf_file_path):
                try:
                    os.remove(topic.pdf_file_path)
                except:
                    pass
            topic.pdf_file_path = None
            topic.pdf_filename = None
        elif pdf_file and pdf_file.filename != '':
            # Upload new PDF
            if allowed_file(pdf_file.filename):
                # Delete old PDF if exists
                if topic.pdf_file_path and os.path.exists(topic.pdf_file_path):
                    os.remove(topic.pdf_file_path)
                
                filename = secure_filename(pdf_file.filename)
                # Add timestamp to make filename unique
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{filename}"
                
                upload_dir = ensure_upload_directory()
                file_path = os.path.join(upload_dir, filename)
                pdf_file.save(file_path)
                
                topic.pdf_file_path = file_path
                topic.pdf_filename = filename
                    
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Mavzu muvaffaqiyatli tahrirlandi'
        })
        
    except Exception as e:
        app.logger.error(f"Error editing topic: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/topic/<int:topic_id>', methods=['DELETE'])
def api_delete_topic(topic_id):
    """API endpoint to delete a topic"""
    if not session.get('logged_in', False):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        topic = Topic.query.get_or_404(topic_id)
        
        # Remove PDF file if exists
        if topic.pdf_file:
            try:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], topic.pdf_file))
            except:
                pass
        
        # Delete topic
        db.session.delete(topic)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Mavzu muvaffaqiyatli o\'chirildi'
        })
        
    except Exception as e:
        app.logger.error(f"Error deleting topic: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/toggle_difficult/<int:topic_id>', methods=['POST'])
def api_toggle_difficult(topic_id):
    """API endpoint to toggle difficult status"""
    if not session.get('logged_in', False):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        topic = Topic.query.get_or_404(topic_id)
        user_id = session['user_id']
        
        # Check if already marked as difficult
        existing = DifficultTopic.query.filter_by(user_id=user_id, topic_id=topic_id).first()
        
        if existing:
            # Remove from difficult
            db.session.delete(existing)
            message = 'Mavzu qiyinlikdan olindi'
        else:
            # Mark as difficult
            difficult = DifficultTopic(user_id=user_id, topic_id=topic_id)
            db.session.add(difficult)
            message = 'Mavzu qiyin deb belgilandi'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': message
        })
        
    except Exception as e:
        app.logger.error(f"Error toggling difficult: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/uploads/<filename>')
def serve_pdf(filename):
    """Serve PDF files"""
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except:
        abort(404)

@app.route('/api/subject/<int:subject_id>')
def api_get_subject(subject_id):
    """API endpoint to get subject details"""
    if not session.get('logged_in', False):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        subject = Subject.query.get_or_404(subject_id)
        
        return jsonify({
            'success': True,
            'subject': {
                'id': subject.id,
                'name': subject.name,
                'description': subject.description
            }
        })
        
    except Exception as e:
        app.logger.error(f"Error getting subject: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/edit_subject', methods=['POST'])
def api_edit_subject():
    """API endpoint to edit a subject"""
    if not session.get('logged_in', False):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        subject_id = request.form.get('subject_id', type=int)
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        
        if not subject_id or not name:
            return jsonify({'error': 'Fan ID va nomi kiritilishi shart'}), 400
        
        subject = Subject.query.get_or_404(subject_id)
        
        # Update subject
        subject.name = name
        subject.description = description if description else None
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Fan muvaffaqiyatli tahrirlandi'
        })
        
    except Exception as e:
        app.logger.error(f"Error editing subject: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/subject/<int:subject_id>', methods=['DELETE'])
def api_delete_subject(subject_id):
    """API endpoint to delete a subject"""
    if not session.get('logged_in', False):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        subject = Subject.query.get_or_404(subject_id)
        
        # Delete all topics and their PDF files
        for topic in subject.topics:
            if topic.pdf_file:
                try:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], topic.pdf_file))
                except:
                    pass
            db.session.delete(topic)
        
        # Delete subject
        db.session.delete(subject)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Fan muvaffaqiyatli o\'chirildi'
        })
        
    except Exception as e:
        app.logger.error(f"Error deleting subject: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/ai_general_chat', methods=['GET', 'POST'])
def ai_general_chat():
    if not session.get('logged_in', False):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        user_question = request.form.get('question', '').strip()
        
        if not user_question:
            return jsonify({'error': 'Iltimos, savol kiriting!'})
        
        try:
            # Generate comprehensive AI response for any question
            ai_response = generate_comprehensive_response(user_question)
            
            # Save chat
            chat = AIChat(
                user_id=session['user_id'],
                question=user_question,
                answer=ai_response,
                topic_id=None,
                test_generated=False
            )
            db.session.add(chat)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'ai_response': ai_response
            })
            
        except Exception as e:
            app.logger.error(f"AI general chat error: {str(e)}")
            return jsonify({'error': str(e)})
    
    return redirect(url_for('ai_assistant'))

@app.route('/ai_subjects_chat', methods=['GET', 'POST'])
def ai_subjects_chat():
    if not session.get('logged_in', False):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        user_question = request.form.get('question', '').strip()
        subject_id = request.form.get('subject_id', type=int)
        topic_id = request.form.get('topic_id', type=int)
        
        if not user_question:
            return jsonify({'error': 'Iltimos, savol kiriting!'})
        
        try:
            # Generate comprehensive subject response and 15 test questions
            ai_response, test_questions = generate_subject_comprehensive_response(user_question, subject_id, topic_id)
            
            # Save chat
            chat = AIChat(
                user_id=session['user_id'],
                question=user_question,
                answer=ai_response,
                topic_id=topic_id,
                test_generated=True
            )
            db.session.add(chat)
            db.session.commit()
            
            # Create test with 15 questions
            test_id = create_comprehensive_test(user_question, test_questions, subject_id, topic_id)
            
            return jsonify({
                'success': True,
                'ai_response': ai_response,
                'test_questions': test_questions,
                'test_id': test_id,
                'total_questions': len(test_questions)
            })
            
        except Exception as e:
            app.logger.error(f"AI subjects chat error: {str(e)}")
            return jsonify({'error': str(e)})
    
    return redirect(url_for('ai_assistant'))

@app.route('/ai_chat_gpt', methods=['GET', 'POST'])
def ai_chat_gpt():
    if not session.get('logged_in', False):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        user_question = request.form.get('question', '').strip()
        topic_id = request.form.get('topic_id', type=int)
        generate_test = request.form.get('generate_test') == 'on'
        
        if not user_question:
            return render_template('ai_chat_gpt.html', 
                                 topics=Topic.query.all(),
                                 chat_history=get_chat_history(),
                                 error="Iltimos, savol kiriting!")
        
        try:
            # Generate AI response and test questions
            ai_response, test_questions = generate_ai_response_and_test(user_question)
            
            # Save chat
            chat = AIChat(
                user_id=session['user_id'],
                question=user_question,
                answer=ai_response,
                topic_id=topic_id,
                test_generated=generate_test
            )
            db.session.add(chat)
            db.session.commit()
            
            # If test generation requested, create test
            test_id = None
            if generate_test and test_questions:
                test_id = create_ai_test(user_question, test_questions, topic_id)
            
            return render_template('ai_chat_gpt.html', 
                                 topics=Topic.query.all(),
                                 chat_history=get_chat_history(),
                                 last_question=user_question,
                                 last_answer=ai_response,
                                 test_questions=test_questions if generate_test else None,
                                 test_id=test_id)
            
        except Exception as e:
            app.logger.error(f"AI chat error: {str(e)}")
            return render_template('ai_chat_gpt.html', 
                                 topics=Topic.query.all(),
                                 chat_history=get_chat_history(),
                                 error="Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")
    
    return render_template('ai_chat_gpt.html', 
                         topics=Topic.query.all(),
                         chat_history=get_chat_history())

@app.route('/ai_chat', methods=['GET', 'POST'])
def ai_chat():
    if not session.get('logged_in', False):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        user_question = request.form.get('question', '').strip()
        topic_id = request.form.get('topic_id', type=int)
        generate_test = request.form.get('generate_test') == 'on'
        
        if not user_question:
            return render_template('ai_chat.html', 
                                 topics=Topic.query.all(),
                                 chat_history=get_chat_history(),
                                 error="Iltimos, savol kiriting!")
        
        try:
            # Generate AI response and test questions
            ai_response, test_questions = generate_ai_response_and_test(user_question)
            
            # Save chat
            chat = AIChat(
                user_id=session['user_id'],
                question=user_question,
                answer=ai_response,
                topic_id=topic_id,
                test_generated=generate_test
            )
            db.session.add(chat)
            db.session.commit()
            
            # If test generation requested, create test
            test_id = None
            if generate_test and test_questions:
                test_id = create_ai_test(user_question, test_questions, topic_id)
            
            return render_template('ai_chat.html', 
                                 topics=Topic.query.all(),
                                 chat_history=get_chat_history(),
                                 last_question=user_question,
                                 last_answer=ai_response,
                                 test_questions=test_questions if generate_test else None,
                                 test_id=test_id)
            
        except Exception as e:
            app.logger.error(f"AI chat error: {str(e)}")
            return render_template('ai_chat.html', 
                                 topics=Topic.query.all(),
                                 chat_history=get_chat_history(),
                                 error="Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")
    
    return render_template('ai_chat.html', 
                         topics=Topic.query.all(),
                         chat_history=get_chat_history())

@app.route('/api/ai_response', methods=['POST'])
def api_ai_response():
    """API endpoint for AI responses and test generation"""
    if not session.get('logged_in', False):
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    user_question = data.get('question', '').strip()
    
    if not user_question:
        return jsonify({'error': 'Savol kiritilmagan'}), 400
    
    try:
        # Generate AI response and test questions
        ai_response, test_questions = generate_ai_response_and_test(user_question)
        
        # Save chat
        chat = AIChat(
            user_id=session['user_id'],
            question=user_question,
            answer=ai_response,
            test_generated=True
        )
        db.session.add(chat)
        db.session.commit()
        
        # Return JSON response
        return jsonify({
            'ai_response': ai_response,
            'test_questions': test_questions,
            'success': True
        })
        
    except Exception as e:
        app.logger.error(f"AI API error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# End of application



# Helper Functions
def calculate_daily_points(percentage):
    """Calculate daily points based on percentage"""
    if percentage >= 95:
        return 10
    elif percentage >= 85:
        return 8
    elif percentage >= 75:
        return 6
    elif percentage >= 60:
        return 4
    elif percentage >= 50:
        return 2
    else:
        return 0

def calculate_dtm_points(rank, total_participants):
    """Calculate DTM test points"""
    if rank == 1:
        return 100
    elif rank == 2:
        return 80
    elif rank == 3:
        return 60
    elif rank == 4:
        return 40
    elif rank == 5:
        return 20
    else:
        return 10

def generate_username(first_name, last_name, group_name):
    """Generate username from name and group"""
    base_name = f"{first_name.lower()}.{last_name.lower()}"
    username = f"{base_name}.{group_name.lower()}"
    
    # Check if username exists and add number if needed
    counter = 1
    original_username = username
    while User.query.filter_by(username=username).first():
        username = f"{original_username}{counter}"
        counter += 1
    
    return username

def generate_password(length=8):
    """Generate random password"""
    import random
    import string
    
    characters = string.ascii_letters + string.digits
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

def generate_comprehensive_response(question):
    """Generate comprehensive AI response using ChatGPT API or fallback"""
    if CHATGPT_AVAILABLE:
        try:
            return chatgpt.generate_response(question)
        except Exception as e:
            app.logger.error(f"ChatGPT API error: {e}")
            return _fallback_response(question)
    else:
        return _fallback_response(question)

def _fallback_response(question):
    """Fallback response when ChatGPT API is not available"""
    import random
    
    # Enhanced AI responses for various topics
    responses = {
        'matematika': """Matematika - bu sonlar, miqdorlar, strukturalar va o'zgarishlarni o'rganadigan fundamental fan. 

Asosiy tushunchalar:
- Sonlar va ularning xossalari
- Algebraik ifodalar va tenglamalar
- Geometriya va fazoiy munosabatlar
- Analiz va limitlar
- Ehtimollik va statistika

Matematika kundalik hayotda:
- Moliyaviy hisob-kitoblar
- Muhandislik va qurilish
- Dasturlash va kompyuter fanlari
- Tadqiqot va ma'lumot tahlili

Matematikani o'rganish mantiqiy fikrlash, muammoni yechish qobiliyatini va analitik fikrlashni rivojlantiradi.""",
        
        'fizika': """Fizika - bu tabiatning asosiy qonunlarini, materiya, energiya, vaqt va fazo o'rtasidagi munosabatlarni o'rganadigan fan.

Asosiy bo'limlar:
- Mexanika (harakat, kuch, energiya)
- Termodinamika (issiqlik va temperatura)
- Elektromagnetizm (elektr va magnit maydonlari)
- Optika (yorug'lik va uning xossalari)
- Kvant fizikasi (atom va subatomik dunyo)

Fizikaning amaliy ahamiyati:
- Texnologiyalar rivoji
- Energetika va kommunikatsiya
- Tibbiyot asboblar
- Kosmik tadqiqotlar

Fizika tabiatni tushunishga va zamonaviy texnologiyalarni yaratishga asos bo'ladigan ilmiy fan.""",
        
        'kimyo': """Kimyo - bu moddalarning tarkibi, tuzilishi, xossalari va o'zgarishlarini o'rganadigan fan.

Asosiy tushunchalar:
- Atomlar va molekulalar
- Kimyoviy bog'lanishlar
- Elementlar davriy jadvali
- Kimyoviy reaktsiyalar
- Organik va noorganik birikmalar

Kimyoning hayotdagi o'rni:
- Tibbiyot va dori-darmonlar
- Oziq-ovqat va o'simliklar
- Materiallar va plastmassalar
- Atrof-muhit va ekologiya

Kimyo moddalarning asosiy xususiyatlarini tushunishga va yangi materiallar yaratishga imkon beradi.""",
        
        'biologiya': """Biologiya - bu tirik organizmlarni, ularning tuzilishi, funksiyalari, o'sishi, evolyutsiyasi va tarqalishini o'rganadigan fan.

Asosiy sohalar:
- Sitologiya (hujayralar)
- Genetika (irsiyat)
- Ekologiya (organizmlar va atrof-muhit)
- Fiziologiya (organizmlar funksiyalari)
- Taksonomiya (organizmlar tasnifi)

Biologiyaning ahamiyati:
- Sog'liqni saqlash va tibbiyot
- Qishloq xo'jaligi va oziq-ovqat
- Atrof-muhitni muhofaza qilish
- Biologik xilma-xillikni saqlash

Biologiya hayotning asosiy sirlarini ochishga insoniyatga yordam beradi.""",
        
        'tarix': """Tarix - bu o'tmishdagi voqealarni, insoniyatning rivojlanish yo'nalishini, jamiyatlar, madaniyatlar va tarixiy shaxslarni o'rganadigan fan.

Tarixning ahamiyati:
- O'tmishdan sabok olish
- Hozirgi zamonni tushunish
- Kelajakni rejalashtirish
- Milliy identifikatsiya

Asosiy tarixiy davrlar:
- Qadimgi davrlar
- O'rta asrlar
- Uyg'onish davri
- Zamonaviy davr
- Mustaqillik davri

Tarix insoniyat tajribasini o'rganish va tarixiy xotirani saqlash uchun muhimdir.""",
        
        'geografiya': """Geografiya - bu Yer yuzi, tabiiy resurslar, aholi, iqtisodiyot va ularning o'zaro munosabatlarini o'rganadigan fan.

Geografiya bo'limlari:
- Fizik geografiya (tabiiy ob'ektlar)
- Iqtisodiy geografiya (iqtisodiyot)
- Aholi geografiyasi (demografiya)
- Siyosiy geografiya (davlatlar)

Geografiyaning roli:
- Joylashuvni tushunish
- Resurslardan foydalanish
- Iqlim o'zgarishlari
- Global jarayonlar

Geografiya dunyo xaritasini tushunishga va global muammolarni yechishga yordam beradi.""",
        
        'informatika': """Informatika - bu kompyuterlar, dasturiy ta'minot, axborot texnologiyalari va ma'lumotlarni qayta ishlashni o'rganadigan zamonaviy fan.

Asosiy sohalar:
- Dasturlash tillari
- Algoritmlar va ma'lumotlar tuzilmasi
- Sun'iy intellekt
- Kompyuter tarmoqlari
- Ma'lumotlar bazalari

Informatikaning ahamiyati:
- Avtomatlashtirish
- Kommunikatsiya
- Ma'lumot tahlili
- Raqamli iqtisodiyot

Informatika 21-asrning eng muhim fanlaridan bo'lib, texnologik rivojlanishning asosidir.""",
        
        'adabiyot': """Adabiyot - bu yozma asarlarni, ularning tili, uslubi, mazmuni va badiiy qimmatini o'rganadigan fan.

Adabiyot turlari:
- Nasriy (roman, hikoya)
- She'riy (she'r, doston)
- Dramatik (pyesa, drama)

Adabiyotning ahamiyati:
- Madaniy merosni saqlash
- Tilni rivojlantirish
- Estetik tarbiya
- Insoniyatni tushunish

Adabiyot milliy madaniyatning eng muhim qismi va insoniyat ruhiy boyligidir."""
    }
    
    # Default comprehensive response
    default_response = f"""Siz yozgansiz: "{question}". Bu juda qiziqarli mavzu! 

ChatGPT API ulanmaganligi uchun mahalliy javob beraman. Bu soha zamonaviy dunyoda katta ahamiyatga ega. U insoniyatning bilim doirasini kengaytiradi va hayotni yaxshiroq tushunishga yordam beradi.

Agar siz ushbu mavzu bo'yicha aniqroq savol bermoqchi bo'lsangiz, men qo'shimcha ma'lumot berishdan mamnun bo'laman. Shuningdek, test savollarini ham tayyorlashim mumkin.

ChatGPT API ni ulash uchun OPENAI_API_KEY environment variable ni o'rnatishingiz kerak."""
    
    # Enhanced keyword matching
    question_lower = question.lower()
    ai_response = default_response
    
    for key, response in responses.items():
        if key in question_lower:
            ai_response = response
            break
    
    return ai_response

def generate_subject_comprehensive_response(question, subject_id, topic_id):
    """Generate comprehensive subject response with 15 test questions using ChatGPT API"""
    # Get subject and topic information
    subject = Subject.query.get(subject_id) if subject_id else None
    topic = Topic.query.get(topic_id) if topic_id else None
    
    subject_name = subject.name if subject else "Fan"
    topic_name = topic.title if topic else ""
    
    # Generate AI response
    if CHATGPT_AVAILABLE:
        try:
            ai_response = chatgpt.generate_subject_response(question, subject_name, topic_name)
            test_questions = chatgpt.generate_test_questions(subject_name, topic_name, 15)
            return ai_response, test_questions
        except Exception as e:
            app.logger.error(f"ChatGPT API error: {e}")
            return _fallback_subject_response(question, subject_name, topic_name)
    else:
        return _fallback_subject_response(question, subject_name, topic_name)

def _fallback_subject_response(question, subject_name, topic_name):
    """Fallback subject response when ChatGPT API is not available"""
    import random
    
    # Generate comprehensive response
    if topic_name:
        ai_response = f"""{topic_name} mavzusi bo'yicha to'liq ma'lumot:

Bu {subject_name} fanning muhim mavzularidan biri. Sizning so'rovingiz: "{question}"

Asosiy tushunchalar:
1. Mavzuning asosiy prinsiplari va qonunlari
2. Amaliy qo'llanilishi va misollar
3. Boshqa mavzular bilan bog'liqligi
4. Zamonaviy tadqiqotlar va rivojlanish yo'nalishlari

O'rganish usullari:
- Nazariy materialni chuqur o'rganish
- Amaliy mashqlar bajarish
- Qo'shimcha adabiyotlar o'qish
- Tajriba va kuzatishlar orqali tekshirish

ChatGPT API ulanmaganligi uchun mahalliy javob beraman. Real AI javoblari uchun API kalitini o'rnatishingiz kerak.

Ushbu mavzuni yaxshi o'rganib olishingiz uchun quyida 15 ta test savolini tayyorladim. Testni ishlab, o'z bilimingizni tekshiring."""
    else:
        ai_response = f"""{subject_name} bo'yicha to'liq ma'lumot:

Bu fan - bu bilimning asosiy sohasi bo'lib, u insoniyat rivojlanishida katta rol o'ynaydi. Sizning so'rovingiz: "{question}"

Asosiy yo'nalishlar:
- Nazariy asoslar va fundamental tushunchalar
- Amaliy qo'llanilish va zamonaviy texnologiyalar
- Tadqiqot metodlari va ilmiy yondashuv
- Kelajak istiqbollari va rivojlanish tendentsiyalari

O'rganishning ahamiyati:
- Mantiqiy fikrlashni rivojlantirish
- Analitik qobiliyatni shakllantirish
- Muammoni yechish ko'nikmalarini o'rganish
- Ilmiy dunyoqarashni shakllantirish

ChatGPT API ulanmaganligi uchun mahalliy javob beraman. Real AI javoblari uchun API kalitini o'rnatishingiz kerak.

Quyida ushbu fan bo'yicha 15 ta test savolini tayyorladim. Testni ishlab, bilimingizni tekshiring."""
    
    # Generate 15 comprehensive test questions
    test_questions = []
    for i in range(15):
        question_types = [
            "Bu mavzuning asosiy tushunchasi nimaga teng?",
            "Quyidagilardan qaysi biri to'g'ri javob beradi?",
            "Bu sohadagi eng muhim kashfiyot qaysi biri?",
            "Amaliyotda qanday qo'llaniladi?",
            "Zamonaviy tadqiqotlar qanday yo'nalishda olib borilmoqda?",
            "Bu mavzuning tarixiy rivojlanishi qanday bo'lgan?",
            "Asosiy metodologiya qanday?",
            "Qanday natijalarga erishilgan?",
            "Kelajakda qanday istiqbollar bor?",
            "Boshqa fanlar bilan qanday bog'liq?",
            "Eng muhim muammolar qanday?",
            "Qanday yechimlar taklif etilgan?",
            "Amaliy ahamiyati nimada?",
            "Nazariy ahamiyati qanday?",
            "Xulosa qanday bo'ladi?"
        ]
        
        question_text = f"{i+1}. {random.choice(question_types)}"
        
        # Generate realistic options
        topic_display = topic_name if topic_name else subject_name
            
        options = [
            f"A) {topic_display} bo'yicha to'g'ri javob varianti",
            f"B) Noto'g'ri javob varianti {i+1}",
            f"C) Noto'g'ri javob varianti {i+2}",
            f"D) Noto'g'ri javob varianti {i+3}"
        ]
        
        # Randomly assign correct answer
        correct_answer = random.choice(['A', 'B', 'C', 'D'])
        
        test_questions.append({
            'question': question_text,
            'options': options,
            'correct_answer': correct_answer
        })
    
    return ai_response, test_questions

def generate_ai_response_and_test(question):
    """Generate AI response and test questions based on user question"""
    import random
    
    # Simple AI response generation (in production, use real AI API)
    responses = {
        'matematika': "Matematika - bu sonlar, miqdorlar, strukturalar va o'zgarishlarni o'rganadigan fan. U mantiqiy fikrlashni rivojlantiradi va har kundalik hayotda muhim rol o'ynaydi.",
        'fizika': "Fizika - bu tabiatning asosiy qonunlarini o'rganadigan fan. U energiya, materiya, vaqt va fazo kabi tushunchalarni o'z ichiga oladi.",
        'kimyo': "Kimyo - bu moddalarning tarkibi, tuzilishi, xossalari va o'zgarishlarini o'rganadigan fan. U hayotning barcha sohalarida qo'llaniladi.",
        'biologiya': "Biologiya - bu tirik organizmlarni va ularning hayot faoliyatini o'rganadigan fan. U odam, hayvonlar, o'simliklar va mikroorganizmlarni o'z ichiga oladi.",
        'tarix': "Tarix - bu o'tmishdagi voqealarni, insoniyatning rivojlanish yo'nalishini va tarixiy shaxslarni o'rganadigan fan.",
        'geografiya': "Geografiya - bu Yer yuzi, tabiiy resurslar, aholi va iqtisodiyotni o'rganadigan fan. U dunyo xaritalarini va joylashuvni tushunishga yordam beradi.",
        'informatika': "Informatika - bu kompyuterlar, dasturiy ta'minot va axborot texnologiyalarini o'rganadigan fan. U zamonaviy dunyoda juda muhim ahamiyatga ega.",
        'adabiyot': "Adabiyot - bu yozma asarlarni, ularning tili, uslubi va mazmunini o'rganadigan fan. U madaniyat va san'atning muhim qismidir."
    }
    
    # Simple keyword matching for response
    question_lower = question.lower()
    ai_response = "Bu savolga to'liq javob berish uchun qo'shimcha ma'lumot kerak. Iltimos, savolingizni aniqroq bayon qiling."
    
    for key, response in responses.items():
        if key in question_lower:
            ai_response = response
            break
    
    # Generate test questions
    test_questions = []
    for i in range(5):
        question_text = f"Savol {i+1}: {question} haqida test savoli"
        
        options = [
            f"A) {question} bo'yicha to'g'ri javob",
            f"B) Noto'g'ri javob varianti {i+1}",
            f"C) Noto'g'ri javob varianti {i+2}",
            f"D) Noto'g'ri javob varianti {i+3}"
        ]
        
        correct_answer = "A"
        
        test_questions.append({
            'question': question_text,
            'options': options,
            'correct_answer': correct_answer
        })
    
    return ai_response, test_questions

def create_ai_test(question, test_questions, topic_id=None):
    """Create a test from AI-generated questions"""
    try:
        # Create test
        test = Test(
            title=f"AI Test: {question[:50]}...",
            subject_id=topic_id or 1,
            test_type='ai_generated',
            test_date=datetime.now().date(),
            start_time=datetime.now().time(),
            end_time=(datetime.now() + timedelta(hours=1)).time(),
            duration_minutes=60
        )
        db.session.add(test)
        db.session.flush()
        
        # Add questions
        for i, q_data in enumerate(test_questions):
            question = Question(
                test_id=test.id,
                text=q_data['question'],
                option_a=q_data['options'][0],
                option_b=q_data['options'][1],
                option_c=q_data['options'][2],
                option_d=q_data['options'][3],
                correct_answer=q_data['correct_answer']
            )
            db.session.add(question)
        
        db.session.commit()
        return test.id
        
    except Exception as e:
        app.logger.error(f"Error creating AI test: {e}")
        db.session.rollback()
        return None

def create_comprehensive_test(question, test_questions, subject_id, topic_id):
    """Create a comprehensive test with 15 questions"""
    try:
        # Create test
        test = Test(
            title=f"Comprehensive Test: {question[:50]}...",
            subject_id=subject_id or 1,
            test_type='comprehensive_ai',
            test_date=datetime.now().date(),
            start_time=datetime.now().time(),
            end_time=(datetime.now() + timedelta(hours=2)).time(),
            duration_minutes=120
        )
        db.session.add(test)
        db.session.flush()
        
        # Add questions
        for i, q_data in enumerate(test_questions):
            question = Question(
                test_id=test.id,
                text=q_data['question'],
                option_a=q_data['options'][0],
                option_b=q_data['options'][1],
                option_c=q_data['options'][2],
                option_d=q_data['options'][3],
                correct_answer=q_data['correct_answer']
            )
            db.session.add(question)
        
        db.session.commit()
        return test.id
        
    except Exception as e:
        app.logger.error(f"Error creating comprehensive test: {e}")
        db.session.rollback()
        return None

def get_chat_history():
    """Get user's chat history"""
    return AIChat.query.filter_by(user_id=session.get('user_id'))\
                     .order_by(AIChat.created_at.desc())\
                     .limit(10).all()

def create_test_schedule():
    """Create test schedule if needed"""
    try:
        # Check if we need to create new tests
        from datetime import datetime, timedelta
        
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        
        # Check if we already have tests for this week
        existing_tests = Test.query.filter(
            Test.test_date >= week_start,
            Test.test_date <= week_start + timedelta(days=6)
        ).count()
        
        if existing_tests == 0:
            # Create tests for each subject
            subjects = Subject.query.all()
            for subject in subjects:
                # Create a daily test
                test = Test(
                    title=f"{subject.name} - Daily Test",
                    description=f"Daily test for {subject.name}",
                    test_type='daily',
                    test_date=today,
                    start_time='09:00',
                    end_time='10:00',
                    duration_minutes=60,
                    subject_id=subject.id
                )
                db.session.add(test)
            
            db.session.commit()
            app.logger.info("Test schedule created successfully")
            
    except Exception as e:
        app.logger.error(f"Error creating test schedule: {e}")
        db.session.rollback()

def ensure_database_integrity():
    """Ensure database integrity"""
    try:
        with app.app_context():
            from sqlalchemy import text
            
            # Clean up orphaned records
            db.session.execute(text("DELETE FROM test_registration WHERE user_id NOT IN (SELECT id FROM user)"))
            db.session.execute(text("DELETE FROM test_result WHERE user_id NOT IN (SELECT id FROM user)"))
            db.session.execute(text("DELETE FROM certificate WHERE user_id NOT IN (SELECT id FROM user)"))
            db.session.commit()
            
    except Exception as e:
        app.logger.error(f"Database integrity error: {e}")
        db.session.rollback()

def clear_all_caches():
    """Clear all caches"""
    try:
        # Clear any application-level caches
        if hasattr(app, '_cached_user_data'):
            app._cached_user_data.clear()
        
        # Clear session data if in request context
        try:
            from flask import session
            session.clear()
        except RuntimeError:
            pass
        
    except Exception as e:
        app.logger.error(f"Cache clearing error: {e}")

if __name__ == '__main__':
    app.run(debug=True)
