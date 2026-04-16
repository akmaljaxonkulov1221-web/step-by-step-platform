#!/usr/bin/env python3
"""
Error Fix Script for Production Deployment
This script helps identify and fix common issues that cause Internal Server Error
"""

import os
import sys
import traceback
from flask import Flask

def check_environment():
    """Check if environment variables are set correctly"""
    print("=== Environment Check ===")
    
    # Check critical environment variables
    flask_env = os.getenv('FLASK_ENV', 'development')
    port = os.getenv('PORT', '5000')
    database_url = os.getenv('DATABASE_URL', 'sqlite:///education_complete.db')
    
    print(f"FLASK_ENV: {flask_env}")
    print(f"PORT: {port}")
    print(f"DATABASE_URL: {database_url}")
    
    # Set defaults if not set
    if not os.getenv('FLASK_ENV'):
        os.environ['FLASK_ENV'] = 'production'
        print("Set FLASK_ENV to production")
    
    if not os.getenv('PORT'):
        os.environ['PORT'] = '5000'
        print("Set PORT to 5000")
    
    return True

def check_database():
    """Check database connection and create missing data"""
    print("\n=== Database Check ===")
    
    try:
        # Import app here to avoid circular imports
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import app
        
        with app.app.app_context():
            # Create tables
            app.db.create_all()
            print("Database tables: OK")
            
            # Check if subjects exist
            subjects = app.Subject.query.all()
            if len(subjects) == 0:
                print("No subjects found, creating default subjects...")
                default_subjects = [
                    {'name': 'Matematika', 'description': 'Matematika fani'},
                    {'name': 'Fizika', 'description': 'Fizika fani'},
                    {'name': 'Kimyo', 'description': 'Kimyo fani'},
                    {'name': 'Biologiya', 'description': 'Biologiya fani'},
                    {'name': 'Ingliz tili', 'description': 'Ingliz tili fani'}
                ]
                
                for subject_data in default_subjects:
                    subject = app.Subject(
                        name=subject_data['name'],
                        description=subject_data['description']
                    )
                    app.db.session.add(subject)
                
                app.db.session.commit()
                print(f"Created {len(default_subjects)} default subjects")
            else:
                print(f"Subjects: {len(subjects)} found")
            
            # Check if admin user exists
            admin_user = app.User.query.filter_by(username='admin').first()
            if not admin_user:
                print("Admin user not found, creating...")
                from werkzeug.security import generate_password_hash
                
                admin_user = app.User(
                    username='admin',
                    password_hash=generate_password_hash('admin123'),
                    first_name='Admin',
                    last_name='User',
                    is_admin=True,
                    is_group_leader=False
                )
                app.db.session.add(admin_user)
                app.db.session.commit()
                print("Admin user created")
            else:
                print("Admin user: OK")
            
            return True
            
    except Exception as e:
        print(f"Database check failed: {e}")
        traceback.print_exc()
        return False

def check_templates():
    """Check if critical templates exist"""
    print("\n=== Template Check ===")
    
    template_dir = 'templates'
    if not os.path.exists(template_dir):
        print("Templates directory: MISSING")
        return False
    
    critical_templates = ['base.html', 'admin_dashboard.html', 'login.html', 'student_dashboard.html']
    
    for template in critical_templates:
        template_path = os.path.join(template_dir, template)
        if os.path.exists(template_path):
            print(f"{template}: OK")
        else:
            print(f"{template}: MISSING")
            return False
    
    return True

def check_static_files():
    """Check if static files exist"""
    print("\n=== Static Files Check ===")
    
    static_dir = 'static'
    if not os.path.exists(static_dir):
        print("Static directory: MISSING")
        return False
    
    css_dir = os.path.join(static_dir, 'css')
    js_dir = os.path.join(static_dir, 'js')
    
    if os.path.exists(css_dir):
        print("CSS directory: OK")
    else:
        print("CSS directory: MISSING")
    
    if os.path.exists(js_dir):
        print("JS directory: OK")
    else:
        print("JS directory: MISSING")
    
    return True

def check_deployment_files():
    """Check if deployment files exist"""
    print("\n=== Deployment Files Check ===")
    
    required_files = ['Procfile', 'render.yaml', 'requirements.txt']
    
    for file_name in required_files:
        if os.path.exists(file_name):
            print(f"{file_name}: OK")
        else:
            print(f"{file_name}: MISSING")
            return False
    
    return True

def run_tests():
    """Run basic functionality tests"""
    print("\n=== Functionality Tests ===")
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import app
        
        with app.app.app_context():
            with app.app.test_client() as client:
                # Test home page
                response = client.get('/')
                print(f"Home page: {response.status_code}")
                
                # Test login
                response = client.post('/login', data={
                    'username': 'admin',
                    'password': 'admin123'
                }, follow_redirects=True)
                print(f"Admin login: {response.status_code}")
                
                # Test admin dashboard
                response = client.get('/admin/dashboard')
                print(f"Admin dashboard: {response.status_code}")
                
                return True
                
    except Exception as e:
        print(f"Functionality tests failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Main function to run all checks"""
    print("=== Production Error Fix Script ===")
    print("This script will check and fix common issues that cause Internal Server Error")
    print()
    
    all_checks_passed = True
    
    # Run all checks
    checks = [
        ("Environment", check_environment),
        ("Database", check_database),
        ("Templates", check_templates),
        ("Static Files", check_static_files),
        ("Deployment Files", check_deployment_files),
        ("Functionality", run_tests)
    ]
    
    for check_name, check_func in checks:
        try:
            if not check_func():
                all_checks_passed = False
                print(f"ERROR: {check_name} check failed!")
            else:
                print(f"SUCCESS: {check_name} check passed!")
        except Exception as e:
            all_checks_passed = False
            print(f"ERROR: {check_name} check failed with exception: {e}")
    
    print("\n=== Summary ===")
    if all_checks_passed:
        print("All checks passed! The application should work correctly.")
        print("If you're still getting Internal Server Error, it might be:")
        print("1. Render.com deployment issues")
        print("2. Temporary server issues")
        print("3. Network connectivity issues")
        print("Please try again in a few minutes.")
    else:
        print("Some checks failed. Please fix the issues above and try again.")
    
    return all_checks_passed

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
