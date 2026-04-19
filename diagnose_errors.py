#!/usr/bin/env python3
"""
Comprehensive error diagnostics for the education platform
"""

import sys
import os
import traceback
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test all imports"""
    print("=== Testing Imports ===")
    
    try:
        from app import app
        print("SUCCESS: App imported successfully")
        return True, app
    except Exception as e:
        print(f"ERROR: App import failed: {e}")
        traceback.print_exc()
        return False, None

def test_database(app):
    """Test database connection and schema"""
    print("\n=== Testing Database ===")
    
    try:
        with app.app_context():
            from app import db
            
            # Test database connection
            db.engine.execute("SELECT 1")
            print("SUCCESS: Database connection works")
            
            # Test table creation
            db.create_all()
            print("SUCCESS: Database tables created/verified")
            
            # Test admin user creation
            from app import User
            admin = User.query.filter_by(username='admin').first()
            if admin:
                print("SUCCESS: Admin user exists")
            else:
                print("INFO: Admin user will be created")
            
            return True
            
    except Exception as e:
        print(f"ERROR: Database test failed: {e}")
        traceback.print_exc()
        return False

def test_routes(app):
    """Test all main routes"""
    print("\n=== Testing Routes ===")
    
    try:
        with app.test_client() as client:
            routes_to_test = [
                ('/', 'Home page'),
                ('/login', 'Login page'),
                ('/health', 'Health check'),
                ('/admin/dashboard', 'Admin dashboard'),
                ('/admin/subjects', 'Admin subjects'),
                ('/admin/students', 'Admin students'),
                ('/admin/groups', 'Admin groups'),
                ('/admin/tests', 'Admin tests'),
                ('/student/dashboard', 'Student dashboard'),
                ('/tests', 'Tests page'),
            ]
            
            results = []
            for route, description in routes_to_test:
                try:
                    response = client.get(route)
                    status = response.status_code
                    if status == 200:
                        print(f"SUCCESS: {description} - {status}")
                    elif status == 302:
                        print(f"SUCCESS: {description} - {status} (redirect)")
                    elif status == 500:
                        print(f"ERROR: {description} - {status} (server error)")
                        # Print error details
                        if response.data:
                            print(f"  Error details: {response.data.decode()[:200]}")
                    else:
                        print(f"WARNING: {description} - {status}")
                    
                    results.append((route, status, response.data.decode() if response.data else None))
                    
                except Exception as e:
                    print(f"ERROR: {description} - Exception: {e}")
                    results.append((route, 'EXCEPTION', str(e)))
            
            return results
            
    except Exception as e:
        print(f"ERROR: Route testing failed: {e}")
        traceback.print_exc()
        return []

def test_models(app):
    """Test all models"""
    print("\n=== Testing Models ===")
    
    try:
        with app.app_context():
            from app import db, User, Group, Subject, Topic, Test, Question, TestRegistration, TestResult, WeeklyTestSchedule, DifficultTopic, AIChat
            
            models = [User, Group, Subject, Topic, Test, Question, TestRegistration, TestResult, WeeklyTestSchedule, DifficultTopic, AIChat]
            
            for model in models:
                try:
                    # Test model query
                    model.query.first()
                    print(f"SUCCESS: {model.__name__} model works")
                except Exception as e:
                    print(f"ERROR: {model.__name__} model failed: {e}")
                    if "no such column" in str(e).lower() or "no such table" in str(e).lower():
                        print(f"  SCHEMA ISSUE: {e}")
            
            return True
            
    except Exception as e:
        print(f"ERROR: Model testing failed: {e}")
        traceback.print_exc()
        return False

def test_templates(app):
    """Test template rendering"""
    print("\n=== Testing Templates ===")
    
    try:
        with app.test_client() as client:
            # Test login template (should work without login)
            response = client.get('/login')
            if response.status_code == 200:
                print("SUCCESS: Login template renders")
            else:
                print(f"ERROR: Login template failed: {response.status_code}")
                
    except Exception as e:
        print(f"ERROR: Template testing failed: {e}")
        traceback.print_exc()

def test_dependencies():
    """Test all dependencies"""
    print("\n=== Testing Dependencies ===")
    
    dependencies = [
        ('flask', 'Flask'),
        ('flask_sqlalchemy', 'Flask-SQLAlchemy'),
        ('flask_login', 'Flask-Login'),
        ('werkzeug', 'Werkzeug'),
        ('sqlalchemy', 'SQLAlchemy'),
        ('bcrypt', 'bcrypt'),
        ('jinja2', 'Jinja2'),
    ]
    
    for module, name in dependencies:
        try:
            __import__(module)
            print(f"SUCCESS: {name} imported")
        except ImportError as e:
            print(f"ERROR: {name} not available: {e}")
    
    # Test optional dependencies
    optional_deps = [
        ('PyPDF2', 'PyPDF2'),
        ('pdfplumber', 'pdfplumber'),
        ('chatgpt_integration', 'ChatGPT Integration'),
        ('pdf_parser', 'PDF Parser'),
    ]
    
    print("\n--- Optional Dependencies ---")
    for module, name in optional_deps:
        try:
            __import__(module)
            print(f"SUCCESS: {name} available")
        except ImportError:
            print(f"INFO: {name} not available (optional)")

def main():
    """Run all diagnostics"""
    print("Comprehensive Error Diagnostics")
    print("=" * 50)
    print(f"Time: {datetime.now()}")
    print()
    
    # Test dependencies first
    test_dependencies()
    
    # Test imports
    success, app = test_imports()
    if not success:
        print("\nFATAL: Cannot import app. Stopping diagnostics.")
        return False
    
    # Test database
    db_success = test_database(app)
    
    # Test models
    model_success = test_models(app)
    
    # Test routes
    route_results = test_routes(app)
    
    # Test templates
    test_templates(app)
    
    # Summary
    print("\n" + "=" * 50)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 50)
    
    # Find problematic routes
    problematic_routes = [r for r in route_results if r[1] == 500 or r[1] == 'EXCEPTION']
    
    if problematic_routes:
        print(f"FOUND {len(problematic_routes)} PROBLEMATIC ROUTES:")
        for route, status, error in problematic_routes:
            print(f"  - {route}: {status}")
            if error and len(error) < 200:
                print(f"    Error: {error}")
    
    if not db_success:
        print("DATABASE ISSUES FOUND")
    
    if not model_success:
        print("MODEL ISSUES FOUND")
    
    if not problematic_routes and db_success and model_success:
        print("ALL TESTS PASSED - App should work!")
        return True
    else:
        print("ISSUES FOUND - Need fixes")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
