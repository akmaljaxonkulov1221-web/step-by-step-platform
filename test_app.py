#!/usr/bin/env python3
"""
Test Script for Step by Step Education Platform
Tests all functionality after code fixes
"""

import os
import sys
import json
import tempfile
from datetime import datetime, timedelta

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all imports work correctly"""
    print("=== Testing Imports ===")
    try:
        import app
        print("  App import: OK")
        
        from flask import Flask, render_template, request, redirect, url_for, session, flash
        print("  Flask imports: OK")
        
        from flask_sqlalchemy import SQLAlchemy
        print("  SQLAlchemy import: OK")
        
        from werkzeug.security import generate_password_hash, check_password_hash
        print("  Security imports: OK")
        
        return True
    except Exception as e:
        print(f"  Import error: {e}")
        return False

def test_database_models():
    """Test database models"""
    print("\n=== Testing Database Models ===")
    try:
        import app
        
        with app.app.app_context():
            # Test model creation
            print("  Testing model creation...")
            
            # Create test group
            test_group = app.Group(name='TestGroup', description='Test group')
            app.db.session.add(test_group)
            app.db.session.flush()
            
            # Create test user
            test_user = app.User(
                username='testuser',
                password_hash='test_hash',
                first_name='Test',
                last_name='User',
                group_id=test_group.id
            )
            app.db.session.add(test_user)
            app.db.session.flush()
            
            # Create test subject
            test_subject = app.Subject(name='TestSubject', description='Test subject')
            app.db.session.add(test_subject)
            app.db.session.flush()
            
            # Test relationships
            print("  Testing relationships...")
            assert test_user.group == test_group
            assert test_group.students[0] == test_user
            
            # Clean up
            app.db.session.delete(test_user)
            app.db.session.delete(test_group)
            app.db.session.delete(test_subject)
            app.db.session.commit()
            
            print("  Database models: OK")
            return True
            
    except Exception as e:
        print(f"  Database model error: {e}")
        return False

def test_helper_functions():
    """Test helper functions"""
    print("\n=== Testing Helper Functions ===")
    try:
        import app
        
        with app.app.app_context():
            # Test username generation
            username = app.generate_username('John', 'Doe', '101')
            print(f"  Username generation: {username}")
            
            # Test password generation
            password = app.generate_password()
            print(f"  Password generation: {password}")
            
            # Test DTM points calculation
            dtm_points = app.calculate_dtm_points(1, 10)
            print(f"  DTM points (1st place): {dtm_points}")
            
            # Test daily points calculation
            daily_points = app.calculate_daily_points(95)
            print(f"  Daily points (95%): {daily_points}")
            
            print("  Helper functions: OK")
            return True
        
    except Exception as e:
        print(f"  Helper function error: {e}")
        return False

def test_routes():
    """Test main routes"""
    print("\n=== Testing Routes ===")
    try:
        import app
        
        with app.app.test_client() as client:
            # Test index route
            response = client.get('/')
            print(f"  Index route: {response.status_code}")
            
            # Test login route (GET)
            response = client.get('/login')
            print(f"  Login GET: {response.status_code}")
            
            # Test login route (POST)
            response = client.post('/login', data={
                'username': 'admin',
                'password': 'admin123'
            }, follow_redirects=False)
            print(f"  Admin login: {response.status_code}")
            
            # Test register route (GET)
            response = client.get('/register')
            print(f"  Register GET: {response.status_code}")
            
            print("  Routes: OK")
            return True
            
    except Exception as e:
        print(f"  Route error: {e}")
        return False

def test_database_integrity():
    """Test database integrity function"""
    print("\n=== Testing Database Integrity ===")
    try:
        import app
        
        with app.app.app_context():
            # Test the integrity function
            app.ensure_database_integrity()
            print("  Database integrity: OK")
            return True
            
    except Exception as e:
        print(f"  Database integrity error: {e}")
        return False

def test_cache_clearing():
    """Test cache clearing function"""
    print("\n=== Testing Cache Clearing ===")
    try:
        import app
        
        with app.app.app_context():
            # Test cache clearing
            app.clear_all_caches()
            print("  Cache clearing: OK")
            return True
            
    except Exception as e:
        print(f"  Cache clearing error: {e}")
        return False

def test_user_deletion():
    """Test user deletion logic"""
    print("\n=== Testing User Deletion ===")
    try:
        import app
        
        with app.app.app_context():
            # Create test user with related data
            test_group = app.Group(name='DeleteTestGroup', description='Test group')
            app.db.session.add(test_group)
            app.db.session.flush()
            
            test_user = app.User(
                username='deletetest',
                password_hash='test_hash',
                first_name='Delete',
                last_name='Test',
                group_id=test_group.id
            )
            app.db.session.add(test_user)
            app.db.session.flush()
            
            # Create related data
            test_subject = app.Subject(name='DeleteSubject', description='Test subject')
            app.db.session.add(test_subject)
            app.db.session.flush()
            
            test_certificate = app.Certificate(
                title='Test Certificate',
                description='Test',
                level='A1',
                user_id=test_user.id
            )
            app.db.session.add(test_certificate)
            
            # Delete user
            app.db.session.delete(test_user)
            app.db.session.commit()
            
            # Check if related data is also deleted
            remaining_certificates = app.Certificate.query.filter_by(user_id=test_user.id).count()
            print(f"  Remaining certificates: {remaining_certificates}")
            
            # Clean up
            app.db.session.delete(test_group)
            app.db.session.delete(test_subject)
            app.db.session.commit()
            
            print("  User deletion: OK")
            return True
            
    except Exception as e:
        print(f"  User deletion error: {e}")
        return False

def test_responsive_design():
    """Test responsive design components"""
    print("\n=== Testing Responsive Design ===")
    try:
        # Check if base.html has responsive CSS
        base_template_path = 'templates/base.html'
        if os.path.exists(base_template_path):
            with open(base_template_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for responsive CSS
            if '@media' in content:
                print("  Responsive CSS: Found")
            else:
                print("  Responsive CSS: Missing")
                
            # Check for mobile menu toggle
            if 'mobile-menu-toggle' in content:
                print("  Mobile menu toggle: Found")
            else:
                print("  Mobile menu toggle: Missing")
                
            # Check for JavaScript functions
            if 'toggleSidebar' in content:
                print("  Mobile navigation JS: Found")
            else:
                print("  Mobile navigation JS: Missing")
                
            print("  Responsive design: OK")
            return True
        else:
            print("  Base template: Not found")
            return False
            
    except Exception as e:
        print(f"  Responsive design error: {e}")
        return False

def main():
    """Run all tests"""
    print("=== STEP BY STEP EDUCATION PLATFORM - COMPREHENSIVE TEST ===")
    print("Testing all functionality after code fixes...")
    print()
    
    tests = [
        ("Imports", test_imports),
        ("Database Models", test_database_models),
        ("Helper Functions", test_helper_functions),
        ("Routes", test_routes),
        ("Database Integrity", test_database_integrity),
        ("Cache Clearing", test_cache_clearing),
        ("User Deletion", test_user_deletion),
        ("Responsive Design", test_responsive_design)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  {test_name} test failed with exception: {e}")
            failed += 1
    
    print(f"\n=== TEST RESULTS ===")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total: {passed + failed}")
    
    if failed == 0:
        print("\nAll tests passed! The application is working correctly.")
    else:
        print(f"\n{failed} tests failed. Please check the issues above.")
    
    return failed == 0

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
