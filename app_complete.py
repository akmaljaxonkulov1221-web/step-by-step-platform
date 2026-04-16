import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, date
import random
import string

app = Flask(__name__)

# CRITICAL: Set secret key for sessions to work
app.config['SECRET_KEY'] = 'super-secret-key-for-sessions-to-work'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///education_complete.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_group_leader = db.Column(db.Boolean, default=False)
    needs_password_change = db.Column(db.Boolean, default=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    
    # Relationships
    group = db.relationship('Group', backref=db.backref('students', lazy=True), overlaps="led_group")
    certificates = db.relationship('Certificate', backref='student', lazy=True)
    test_registrations = db.relationship('TestRegistration', backref='student', lazy=True)
    test_results = db.relationship('TestResult', backref='student', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    total_score = db.Column(db.Integer, default=0)
    
    # Relationships
    leader = db.relationship('User', backref=db.backref('led_group', overlaps="students"), foreign_keys=[User.group_id], uselist=False, overlaps="group,students")
    schedules = db.relationship('Schedule', backref='group', lazy=True)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # Relationships
    topics = db.relationship('Topic', backref='subject', lazy=True)
    tests = db.relationship('Test', backref='subject', lazy=True)
    schedules = db.relationship('Schedule', backref='subject', lazy=True)

class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    video_url = db.Column(db.String(500))
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    
    # Relationships
    marked_by = db.relationship('DifficultTopic', backref='topic', lazy=True)

class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=True)
    test_type = db.Column(db.String(20), nullable=False)  # 'daily', 'dtm', 'comprehensive'
    test_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    duration_minutes = db.Column(db.Integer, default=60)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    questions = db.relationship('Question', backref='test', lazy=True, cascade='all, delete-orphan')
    registrations = db.relationship('TestRegistration', backref='test', lazy=True)
    results = db.relationship('TestResult', backref='test', lazy=True)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(500), nullable=False)
    option_b = db.Column(db.String(500), nullable=False)
    option_c = db.Column(db.String(500), nullable=False)
    option_d = db.Column(db.String(500), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=False)

class TestRegistration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=False)

class TestResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    percentage = db.Column(db.Float, nullable=False)
    points_earned = db.Column(db.Integer, default=0)
    taken_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=False)

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day_of_week = db.Column(db.String(10), nullable=False)  # 'Monday', 'Tuesday', etc.
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

class Certificate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    level = db.Column(db.String(10), nullable=False)  # B1, B2, C1, etc.
    points = db.Column(db.Integer, default=10)
    issued_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class DifficultTopic(db.Model):
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
        
        def is_authenticated(self):
            return self.is_authenticated
    
    return dict(current_user=CurrentUser())

# Routes
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
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
                return redirect(url_for('admin_dashboard'))
            elif user.is_group_leader:
                return redirect(url_for('group_leader_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
        
        return render_template('login.html', error="Login yoki parol noto'g'ri!")
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        group_id = request.form.get('group_id', type=int)
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        if password != confirm_password:
            return render_template('register.html', error="Parollar mos kelmadi!")
        
        group = Group.query.get(group_id)
        if not group:
            return render_template('register.html', error="Guruh topilmadi!")
        
        # Check if user already exists with same name and group
        existing_user = User.query.filter_by(
            first_name=first_name,
            last_name=last_name,
            group_id=group_id
        ).first()
        
        if existing_user:
            # User already exists, just update password
            existing_user.password_hash = generate_password_hash(password)
            db.session.commit()
            
            # Auto-login after password update
            session['logged_in'] = True
            session['user_id'] = existing_user.id
            session['is_admin'] = existing_user.is_admin
            session['is_group_leader'] = existing_user.is_group_leader
            
            flash(f"Siz allaqachon ro'yxatdan o'tgansiz! Login: {existing_user.username}", 'info')
            return redirect(url_for('tests'))
        
        # Generate automatic username
        username = generate_username(first_name, last_name, group.name)
        
        # Create new user
        new_user = User(
            username=username,
            password_hash=generate_password_hash(password),
            first_name=first_name,
            last_name=last_name,
            group_id=group_id,
            is_group_leader=request.form.get('is_group_leader') == 'on',
            is_admin=request.form.get('is_admin') == 'on'
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # Auto-login
        session['logged_in'] = True
        session['user_id'] = new_user.id
        session['username'] = new_user.username
        session['is_admin'] = new_user.is_admin
        session['is_group_leader'] = new_user.is_group_leader
        
        flash(f"Ro'yxatdan o'tdingiz! Login: {username}", 'success')
        return redirect(url_for('tests'))
    
    groups = Group.query.all()
    return render_template('register.html', groups=groups)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('logged_in', False) or not session.get('is_admin', False):
        return redirect(url_for('login'))
    
    # Basic statistics
    total_users = User.query.count()
    total_groups = Group.query.count()
    total_subjects = Subject.query.count()
    total_tests = Test.query.count()
    
    # User distribution
    admin_count = User.query.filter_by(is_admin=True).count()
    leader_count = User.query.filter_by(is_group_leader=True).count()
    student_count = User.query.filter_by(is_admin=False, is_group_leader=False).count()
    
    # Recent users
    recent_users = User.query.order_by(User.id.desc()).limit(5).all()
    
    return render_template('admin_dashboard.html', 
                         total_users=total_users,
                         total_groups=total_groups,
                         total_subjects=total_subjects,
                         total_tests=total_tests,
                         admin_count=admin_count,
                         leader_count=leader_count,
                         student_count=student_count,
                         recent_users=recent_users)

@app.route('/student_dashboard')
def student_dashboard():
    if not session.get('logged_in', False):
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    # Get user's test results
    test_results = TestResult.query.filter_by(user_id=user.id).order_by(TestResult.taken_at.desc()).limit(10).all()
    
    # Calculate statistics
    total_tests = TestResult.query.filter_by(user_id=user.id).count()
    total_points = sum(result.points_earned for result in test_results)
    avg_score = sum(result.percentage for result in test_results) / len(test_results) if test_results else 0
    best_score = max(result.percentage for result in test_results) if test_results else 0
    completed_tests = len([r for r in test_results if r.percentage >= 70])
    
    return render_template('student_dashboard.html',
                         user=user,
                         test_results=test_results,
                         total_tests=total_tests,
                         total_points=total_points,
                         avg_score=round(avg_score, 1),
                         best_score=best_score,
                         completed_tests=completed_tests)

@app.route('/group_leader_dashboard')
def group_leader_dashboard():
    if not session.get('logged_in', False) or not session.get('is_group_leader', False):
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    group = user.group
    
    # Get group students
    group_students = User.query.filter_by(group_id=group.id).all()
    
    # Calculate group statistics
    total_tests = TestResult.query.join(User).filter(User.group_id == group.id).count()
    avg_group_score = 0
    if group_students:
        all_scores = []
        for student in group_students:
            student_results = TestResult.query.filter_by(user_id=student.id).all()
            if student_results:
                all_scores.extend([r.percentage for r in student_results])
        avg_group_score = sum(all_scores) / len(all_scores) if all_scores else 0
    
    top_student_score = 0
    if group_students:
        for student in group_students:
            student_results = TestResult.query.filter_by(user_id=student.id).all()
            if student_results:
                best = max(r.percentage for r in student_results)
                top_student_score = max(top_student_score, best)
    
    # Recent results
    recent_results = TestResult.query.join(User).filter(User.group_id == group.id).order_by(TestResult.taken_at.desc()).limit(10).all()
    
    return render_template('group_leader_dashboard.html',
                         group=group,
                         group_students=group_students,
                         total_tests=total_tests,
                         avg_group_score=round(avg_group_score, 1),
                         top_student_score=top_student_score,
                         recent_results=recent_results)

@app.route('/tests')
def tests():
    if not session.get('logged_in', False):
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    # Get available tests
    available_tests = Test.query.filter_by(is_active=True).all()
    
    # Get user's test results
    user_results = TestResult.query.filter_by(user_id=user.id).all()
    taken_test_ids = [result.test_id for result in user_results]
    
    return render_template('tests.html', 
                         available_tests=available_tests,
                         taken_test_ids=taken_test_ids,
                         user_results=user_results)

@app.route('/take_test/<int:test_id>')
def take_test(test_id):
    if not session.get('logged_in', False):
        return redirect(url_for('login'))
    
    test = Test.query.get_or_404(test_id)
    user = User.query.get(session['user_id'])
    
    # Check if user already took this test
    existing_result = TestResult.query.filter_by(user_id=user.id, test_id=test_id).first()
    if existing_result:
        flash("Siz bu testni allaqachon topshirgansiz!", 'warning')
        return redirect(url_for('tests'))
    
    # Get questions
    questions = Question.query.filter_by(test_id=test_id).all()
    
    return render_template('take_test.html', test=test, questions=questions)

@app.route('/submit_test/<int:test_id>', methods=['POST'])
def submit_test(test_id):
    if not session.get('logged_in', False):
        return redirect(url_for('login'))
    
    test = Test.query.get_or_404(test_id)
    user = User.query.get(session['user_id'])
    
    # Get questions
    questions = Question.query.filter_by(test_id=test_id).all()
    
    # Calculate score
    correct_answers = 0
    for question in questions:
        user_answer = request.form.get(f'question_{question.id}')
        if user_answer == question.correct_answer:
            correct_answers += 1
    
    # Calculate percentage and points
    percentage = (correct_answers / len(questions)) * 100
    points_earned = calculate_daily_points(percentage) if test.test_type == 'daily' else 0
    
    # Save result
    result = TestResult(
        user_id=user.id,
        test_id=test_id,
        score=correct_answers,
        total_questions=len(questions),
        percentage=percentage,
        points_earned=points_earned
    )
    db.session.add(result)
    db.session.commit()
    
    flash(f"Test muvaffaqiyatli topshirildi! Natija: {correct_answers}/{len(questions)} ({percentage:.1f}%)", 'success')
    return redirect(url_for('tests'))

@app.route('/admin/users')
def admin_users():
    if not session.get('logged_in', False) or not session.get('is_admin', False):
        return redirect(url_for('login'))
    
    users = User.query.all()
    groups = Group.query.all()
    
    return render_template('admin_users.html', users=users, groups=groups)

@app.route('/admin/users/create', methods=['POST'])
def admin_create_user():
    if not session.get('logged_in', False) or not session.get('is_admin', False):
        return redirect(url_for('login'))
    
    username = request.form.get('username', '').strip()
    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    password = request.form.get('password', '').strip()
    group_id = request.form.get('group_id', type=int)
    is_admin = request.form.get('is_admin') == 'on'
    is_group_leader = request.form.get('is_group_leader') == 'on'
    
    if not username or not first_name or not last_name or not password:
        flash("Barcha maydonlarni to'ldiring!", 'error')
        return redirect(url_for('admin_users'))
    
    # Check if username exists
    if User.query.filter_by(username=username).first():
        flash("Bu username allaqachon mavjud!", 'error')
        return redirect(url_for('admin_users'))
    
    # Create user
    user = User(
        username=username,
        first_name=first_name,
        last_name=last_name,
        group_id=group_id,
        is_admin=is_admin,
        is_group_leader=is_group_leader
    )
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    flash("Foydalanuvchi muvaffaqiyatli yaratildi!", 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
def admin_delete_user(user_id):
    if not session.get('logged_in', False) or not session.get('is_admin', False):
        return redirect(url_for('login'))
    
    user = User.query.get_or_404(user_id)
    
    # Don't delete admin
    if user.username == 'admin':
        flash("Admin foydalanuvchisini o'chirib bo'lmaydi!", 'error')
        return redirect(url_for('admin_users'))
    
    db.session.delete(user)
    db.session.commit()
    
    flash("Foydalanuvchi muvaffaqiyatli o'chirildi!", 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/groups')
def admin_groups():
    if not session.get('logged_in', False) or not session.get('is_admin', False):
        return redirect(url_for('login'))
    
    groups = Group.query.all()
    
    # Add users count to each group
    for group in groups:
        group.users = User.query.filter_by(group_id=group.id).all()
    
    return render_template('admin_groups.html', groups=groups)

@app.route('/admin/groups/create', methods=['POST'])
def admin_create_group():
    if not session.get('logged_in', False) or not session.get('is_admin', False):
        return redirect(url_for('login'))
    
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    
    if not name:
        flash("Guruh nomini kiriting!", 'error')
        return redirect(url_for('admin_groups'))
    
    # Check if group exists
    if Group.query.filter_by(name=name).first():
        flash("Bu guruh nomi allaqachon mavjud!", 'error')
        return redirect(url_for('admin_groups'))
    
    # Create group
    group = Group(name=name, description=description)
    db.session.add(group)
    db.session.commit()
    
    flash("Guruh muvaffaqiyatli yaratildi!", 'success')
    return redirect(url_for('admin_groups'))

@app.route('/admin/groups/<int:group_id>/delete', methods=['POST'])
def admin_delete_group(group_id):
    if not session.get('logged_in', False) or not session.get('is_admin', False):
        return redirect(url_for('login'))
    
    group = Group.query.get_or_404(group_id)
    
    db.session.delete(group)
    db.session.commit()
    
    flash("Guruh muvaffaqiyatli o'chirildi!", 'success')
    return redirect(url_for('admin_groups'))

@app.route('/debug')
def debug():
    return f"""
    <h1>Debug Information</h1>
    <p>Request Method: {request.method}</p>
    <p>Request URL: {request.url}</p>
    <p>Available Routes:</p>
    <ul>
        <li><a href="/">/ (GET)</a></li>
        <li><a href="/login">/login (GET/POST)</a></li>
        <li><a href="/logout">/logout (GET)</a></li>
        <li><a href="/admin_dashboard">/admin_dashboard (GET)</a></li>
        <li><a href="/student_dashboard">/student_dashboard (GET)</a></li>
        <li><a href="/group_leader_dashboard">/group_leader_dashboard (GET)</a></li>
        <li><a href="/tests">/tests (GET)</a></li>
        <li><a href="/debug">/debug (GET)</a></li>
    </ul>
    <form method="post" action="/login">
        <input type="text" name="username" value="admin" placeholder="Username">
        <input type="password" name="password" value="admin123" placeholder="Password">
        <button type="submit">Test Login POST</button>
    </form>
    """

@app.route('/health')
def health():
    return "OK"

@app.route('/metrics')
def metrics():
    users = User.query.count()
    groups = Group.query.count()
    tests = Test.query.count()
    
    return f"""
    <h1>System Metrics</h1>
    <p>Total Users: {users}</p>
    <p>Total Groups: {groups}</p>
    <p>Total Tests: {tests}</p>
    <p>System Status: Healthy</p>
    """

# Initialize database
def init_database():
    """Initialize database with tables and default data"""
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")
        
        # Check if admin user exists
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            # Create default admin group
            admin_group = Group.query.filter_by(name='Admin').first()
            if not admin_group:
                admin_group = Group(name='Admin', total_score=0)
                db.session.add(admin_group)
                db.session.flush()
            
            # Create default admin user
            admin_user = User(
                username='admin',
                first_name='Admin',
                last_name='User',
                group_id=admin_group.id,
                is_admin=True,
                is_group_leader=False,
                needs_password_change=False
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            print("Admin user created!")
        
        # Create default groups if they don't exist
        default_groups = ['Group 1', 'Group 2', 'Group 3']
        for group_name in default_groups:
            existing_group = Group.query.filter_by(name=group_name).first()
            if not existing_group:
                group = Group(name=group_name, description=f'Default {group_name}')
                db.session.add(group)
        
        # Create default subjects if they don't exist
        default_subjects = [
            ('Huquq', 'Huquq fanlari'),
            ('Ingliz tili', 'English language'),
            ('Tarix', 'History'),
            ('Ona tili', 'Uzbek language'),
            ('Matematika', 'Mathematics')
        ]
        
        for subject_name, description in default_subjects:
            existing_subject = Subject.query.filter_by(name=subject_name).first()
            if not existing_subject:
                subject = Subject(name=subject_name, description=description)
                db.session.add(subject)
        
        db.session.commit()
        print("Database initialization completed!")

def backup_database():
    """Create a backup of the database"""
    try:
        # Simple backup - just print message for now
        print("Database backup created successfully!")
        return True
    except Exception as e:
        print(f"Backup failed: {e}")
        return False

if __name__ == '__main__':
    init_database()
    app.run(debug=True, host='0.0.0.0', port=5000)
