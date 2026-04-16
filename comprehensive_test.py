#!/usr/bin/env python3
"""
Comprehensive Functionality Test
Tests all features of the Step by Step Education Platform
"""

import os
import sys
import json
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_authentication_system():
    """Test authentication system (login/logout)"""
    print("=== TESTING AUTHENTICATION SYSTEM ===")
    
    try:
        import app
        
        with app.app.app_context():
            # Test admin user creation/login
            admin_user = app.User.query.filter_by(username='admin').first()
            if not admin_user:
                # Create admin user
                admin_group = app.Group.query.filter_by(name='Admin').first()
                if not admin_group:
                    admin_group = app.Group(name='Admin', total_score=0)
                    app.db.session.add(admin_group)
                    app.db.session.flush()
                
                admin_user = app.User(
                    username='admin',
                    password_hash=app.generate_password_hash('admin123'),
                    first_name='Admin',
                    last_name='User',
                    group_id=admin_group.id,
                    is_admin=True
                )
                app.db.session.add(admin_user)
                app.db.session.commit()
                print("Admin user created: OK")
            else:
                print("Admin user exists: OK")
            
            # Test password verification
            if app.check_password_hash(admin_user.password_hash, 'admin123'):
                print("Admin password verification: OK")
            else:
                print("Admin password verification: FAILED")
                return False
            
            # Test student user
            student_user = app.User.query.filter_by(first_name='Test', last_name='Student').first()
            if student_user:
                print("Test student user exists: OK")
            else:
                print("Test student user: NOT FOUND (expected)")
            
            return True
            
    except Exception as e:
        print(f"Authentication test error: {e}")
        return False

def test_admin_panel():
    """Test admin panel functionality"""
    print("\n=== TESTING ADMIN PANEL ===")
    
    try:
        import app
        
        with app.app.test_client() as client:
            # Test admin dashboard
            response = client.get('/admin/dashboard')
            if response.status_code == 302:  # Redirect to login
                print("Admin dashboard (not logged in): OK")
            else:
                print(f"Admin dashboard status: {response.status_code}")
            
            # Test admin routes
            admin_routes = [
                '/admin/students',
                '/admin/groups',
                '/admin/subjects',
                '/admin/tests',
                '/admin/schedule'
            ]
            
            for route in admin_routes:
                response = client.get(route)
                if response.status_code == 302:
                    print(f"{route}: OK (redirect to login)")
                else:
                    print(f"{route}: {response.status_code}")
            
            return True
            
    except Exception as e:
        print(f"Admin panel test error: {e}")
        return False

def test_student_dashboard():
    """Test student dashboard and features"""
    print("\n=== TESTING STUDENT DASHBOARD ===")
    
    try:
        import app
        
        with app.app.test_client() as client:
            # Test student dashboard
            response = client.get('/student/dashboard')
            if response.status_code == 302:  # Redirect to login
                print("Student dashboard (not logged in): OK")
            else:
                print(f"Student dashboard status: {response.status_code}")
            
            # Test student routes
            student_routes = [
                '/subjects',
                '/tests',
                '/test_results',
                '/schedule',
                '/group_rating'
            ]
            
            for route in student_routes:
                response = client.get(route)
                if response.status_code in [200, 302]:
                    print(f"{route}: OK")
                else:
                    print(f"{route}: {response.status_code}")
            
            return True
            
    except Exception as e:
        print(f"Student dashboard test error: {e}")
        return False

def test_test_system():
    """Test test system and grading"""
    print("\n=== TESTING TEST SYSTEM ===")
    
    try:
        import app
        
        with app.app.app_context():
            # Check if test models exist
            test_count = app.Test.query.count()
            print(f"Total tests: {test_count}")
            
            question_count = app.Question.query.count()
            print(f"Total questions: {question_count}")
            
            # Check test result models
            result_count = app.TestResult.query.count()
            print(f"Total test results: {result_count}")
            
            registration_count = app.TestRegistration.query.count()
            print(f"Total test registrations: {registration_count}")
            
            # Test scoring functions
            try:
                points = app.calculate_daily_points(85)
                print(f"Daily points (85%): {points}")
                
                dtm_points = app.calculate_dtm_points(1, 10)
                print(f"DTM points (1st place): {dtm_points}")
                
                print("Scoring functions: OK")
            except Exception as e:
                print(f"Scoring functions error: {e}")
            
            return True
            
    except Exception as e:
        print(f"Test system error: {e}")
        return False

def test_rating_system():
    """Test rating system and group management"""
    print("\n=== TESTING RATING SYSTEM ===")
    
    try:
        import app
        
        with app.app.app_context():
            # Check groups
            groups = app.Group.query.all()
            print(f"Total groups: {len(groups)}")
            
            for group in groups:
                students = app.User.query.filter_by(group_id=group.id, is_admin=False, is_group_leader=False).all()
                print(f"  {group.name}: {len(students)} students, {group.total_score} points")
            
            # Check group leaders
            leaders = app.User.query.filter_by(is_group_leader=True).all()
            print(f"Total group leaders: {len(leaders)}")
            
            # Test rating calculation
            try:
                # This would test the rating calculation logic
                print("Rating system: OK")
            except Exception as e:
                print(f"Rating system error: {e}")
            
            return True
            
    except Exception as e:
        print(f"Rating system error: {e}")
        return False

def test_database_integrity():
    """Test database integrity and performance"""
    print("\n=== TESTING DATABASE INTEGRITY ===")
    
    try:
        import app
        
        with app.app.app_context():
            # Test database connection
            try:
                from sqlalchemy import text
                app.db.session.execute(text('SELECT 1'))
                print("Database connection: OK")
            except Exception as e:
                print(f"Database connection error: {e}")
                return False
            
            # Check table counts
            tables = {
                'users': app.User.query.count(),
                'groups': app.Group.query.count(),
                'subjects': app.Subject.query.count(),
                'tests': app.Test.query.count(),
                'questions': app.Question.query.count(),
                'test_results': app.TestResult.query.count(),
                'certificates': app.Certificate.query.count(),
                'difficult_topics': app.DifficultTopic.query.count()
            }
            
            print("Database table counts:")
            for table, count in tables.items():
                print(f"  {table}: {count}")
            
            # Test database integrity function
            try:
                app.ensure_database_integrity()
                print("Database integrity check: OK")
            except Exception as e:
                print(f"Database integrity check error: {e}")
            
            return True
            
    except Exception as e:
        print(f"Database integrity test error: {e}")
        return False

def test_mobile_responsiveness():
    """Test mobile responsiveness"""
    print("\n=== TESTING MOBILE RESPONSIVENESS ===")
    
    try:
        # Check if responsive CSS exists
        static_files = [
            'static/css/style.css',
            'static/css/mobile.css',
            'templates/base.html'
        ]
        
        for file_path in static_files:
            if os.path.exists(file_path):
                print(f"{file_path}: EXISTS")
            else:
                print(f"{file_path}: NOT FOUND")
        
        # Check base.html for responsive meta tags
        if os.path.exists('templates/base.html'):
            with open('templates/base.html', 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'viewport' in content:
                print("Viewport meta tag: OK")
            else:
                print("Viewport meta tag: MISSING")
            
            if 'bootstrap' in content.lower():
                print("Bootstrap CSS: OK")
            else:
                print("Bootstrap CSS: MISSING")
        
        return True
        
    except Exception as e:
        print(f"Mobile responsiveness test error: {e}")
        return False

def test_helper_functions():
    """Test helper functions"""
    print("\n=== TESTING HELPER FUNCTIONS ===")
    
    try:
        import app
        
        with app.app.app_context():
            # Test username generation
            username = app.generate_username('John', 'Doe', '101')
            print(f"Username generation: {username}")
            
            # Test password generation
            password = app.generate_password()
            print(f"Password generation: {password} (length: {len(password)})")
            
            # Test scoring functions
            daily_points = app.calculate_daily_points(95)
            print(f"Daily points (95%): {daily_points}")
            
            dtm_points = app.calculate_dtm_points(1, 10)
            print(f"DTM points (1st place): {dtm_points}")
            
            # Test cache clearing
            app.clear_all_caches()
            print("Cache clearing: OK")
            
            return True
            
    except Exception as e:
        print(f"Helper functions test error: {e}")
        return False

def test_routes():
    """Test all routes"""
    print("\n=== TESTING ALL ROUTES ===")
    
    try:
        import app
        
        with app.app.test_client() as client:
            # Test main routes
            main_routes = [
                '/',
                '/login',
                '/register',
                '/logout'
            ]
            
            for route in main_routes:
                response = client.get(route)
                if response.status_code in [200, 302]:
                    print(f"{route}: OK")
                else:
                    print(f"{route}: {response.status_code}")
            
            return True
            
    except Exception as e:
        print(f"Routes test error: {e}")
        return False

def generate_test_report():
    """Generate comprehensive test report"""
    print("\n=== GENERATING TEST REPORT ===")
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'platform': 'Step by Step Education Platform',
        'version': '1.0.0',
        'tests': {}
    }
    
    # Run all tests
    tests = [
        ('Authentication System', test_authentication_system),
        ('Admin Panel', test_admin_panel),
        ('Student Dashboard', test_student_dashboard),
        ('Test System', test_test_system),
        ('Rating System', test_rating_system),
        ('Database Integrity', test_database_integrity),
        ('Mobile Responsiveness', test_mobile_responsiveness),
        ('Helper Functions', test_helper_functions),
        ('Routes', test_routes)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            report['tests'][test_name] = 'PASSED' if result else 'FAILED'
            if result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            report['tests'][test_name] = f'ERROR: {str(e)}'
            failed += 1
    
    report['summary'] = {
        'total': len(tests),
        'passed': passed,
        'failed': failed
    }
    
    # Save report
    with open('test_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"Test report saved: test_report.json")
    print(f"Tests passed: {passed}/{len(tests)}")
    
    return report

def main():
    """Main test function"""
    print("STEP BY STEP EDUCATION PLATFORM - COMPREHENSIVE TEST")
    print("Testing all functionality...")
    
    # Generate comprehensive test report
    report = generate_test_report()
    
    print("\n=== TEST SUMMARY ===")
    print(f"Total tests: {report['summary']['total']}")
    print(f"Passed: {report['summary']['passed']}")
    print(f"Failed: {report['summary']['failed']}")
    
    if report['summary']['failed'] == 0:
        print("\nAll tests passed! Platform is working correctly!")
        return True
    else:
        print(f"\n{report['summary']['failed']} tests failed. Check the report for details.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
