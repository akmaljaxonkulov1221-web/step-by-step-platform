#!/usr/bin/env python3
"""
Debug Login Error
Specifically investigate login functionality
"""

import os
import sys
import traceback

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_login_route():
    """Test login route specifically"""
    print("=== TESTING LOGIN ROUTE ===")
    
    try:
        import app
        
        with app.app.test_client() as client:
            # Test GET request to login page
            response = client.get('/login')
            print(f"GET /login status: {response.status_code}")
            
            if response.status_code == 200:
                print("Login page loads successfully")
            else:
                print(f"Login page failed: {response.status_code}")
                print(f"Response: {response.data.decode()}")
                return False
            
            # Test POST request with valid data
            login_data = {
                'username': 'admin',
                'password': 'admin123'
            }
            
            response = client.post('/login', data=login_data, follow_redirects=False)
            print(f"POST /login status: {response.status_code}")
            
            if response.status_code in [200, 302]:
                print("Login POST request processed")
                return True
            else:
                print(f"Login POST failed: {response.status_code}")
                print(f"Response: {response.data.decode()}")
                return False
                
    except Exception as e:
        print(f"Login route test error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_login_function():
    """Test login function directly"""
    print("\n=== TESTING LOGIN FUNCTION ===")
    
    try:
        import app
        
        with app.app.app_context():
            # Check if login function exists
            if hasattr(app, 'login'):
                print("Login function: EXISTS")
                
                # Check if admin user exists
                admin_user = app.User.query.filter_by(username='admin').first()
                if admin_user:
                    print("Admin user: EXISTS")
                    print(f"Admin user ID: {admin_user.id}")
                    
                    # Test password verification
                    if hasattr(app, 'check_password_hash'):
                        if app.check_password_hash(admin_user.password_hash, 'admin123'):
                            print("Admin password verification: OK")
                        else:
                            print("Admin password verification: FAILED")
                            return False
                    else:
                        print("check_password_hash function: MISSING")
                        return False
                else:
                    print("Admin user: MISSING")
                    return False
            else:
                print("Login function: MISSING")
                return False
            
            return True
            
    except Exception as e:
        print(f"Login function test error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_session_management():
    """Test session management"""
    print("\n=== TESTING SESSION MANAGEMENT ===")
    
    try:
        import app
        
        with app.app.test_client() as client:
            # Test login and session creation
            login_data = {
                'username': 'admin',
                'password': 'admin123'
            }
            
            response = client.post('/login', data=login_data)
            print(f"Login response status: {response.status_code}")
            
            # Check if session is created
            with client.session_transaction() as sess:
                if sess.get('logged_in'):
                    print("Session creation: OK")
                    print(f"User ID in session: {sess.get('user_id')}")
                    return True
                else:
                    print("Session creation: FAILED")
                    return False
                    
    except Exception as e:
        print(f"Session management test error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_database_connection_for_login():
    """Test database connection for login operations"""
    print("\n=== TESTING DATABASE FOR LOGIN ===")
    
    try:
        import app
        
        with app.app.app_context():
            from sqlalchemy import text
            
            # Test user table access
            result = app.db.session.execute(text('SELECT COUNT(*) FROM user')).fetchone()
            print(f"User table access: OK (Count: {result[0]})")
            
            # Test admin user query
            result = app.db.session.execute(text('SELECT id, username FROM user WHERE username = "admin"')).fetchone()
            if result:
                print(f"Admin user query: OK (ID: {result[0]}, Username: {result[1]})")
                return True
            else:
                print("Admin user query: NO RESULTS")
                return False
                
    except Exception as e:
        print(f"Database test error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_flask_app_creation():
    """Test Flask app creation"""
    print("\n=== TESTING FLASK APP CREATION ===")
    
    try:
        import app
        
        # Test app object
        if hasattr(app, 'app'):
            flask_app = app.app
            print(f"Flask app: OK ({flask_app})")
            
            # Test app configuration
            if hasattr(flask_app, 'config'):
                print("App config: OK")
                
                # Check secret key
                if flask_app.config.get('SECRET_KEY'):
                    print("Secret key: OK")
                else:
                    print("Secret key: MISSING")
                    return False
            else:
                print("App config: MISSING")
                return False
        else:
            print("Flask app: MISSING")
            return False
        
        return True
        
    except Exception as e:
        print(f"Flask app test error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

def create_minimal_working_app():
    """Create minimal working app if needed"""
    print("\n=== CREATING MINIMAL WORKING APP ===")
    
    try:
        minimal_app_code = '''
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Simple database setup
def get_db_connection():
    conn = sqlite3.connect('education_complete.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return "Hello World!"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM user WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            session['logged_in'] = True
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = user['is_admin']
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
'''
        
        with open('minimal_app.py', 'w', encoding='utf-8') as f:
            f.write(minimal_app_code)
        
        print("Minimal app created: minimal_app.py")
        return True
        
    except Exception as e:
        print(f"Error creating minimal app: {e}")
        return False

def main():
    """Main debug function"""
    print("STEP BY STEP EDUCATION PLATFORM - LOGIN ERROR DEBUG")
    print("Investigating login Internal Server Error...")
    
    tests = [
        ("Flask App Creation", test_flask_app_creation),
        ("Database Connection", test_database_connection_for_login),
        ("Login Function", test_login_function),
        ("Login Route", test_login_route),
        ("Session Management", test_session_management)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print('='*60)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"Test {test_name} failed: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*60}")
    print("LOGIN ERROR DEBUG SUMMARY")
    print('='*60)
    
    failed_tests = [name for name, result in results if not result]
    
    if failed_tests:
        print(f"Failed tests: {failed_tests}")
        
        # Suggest creating minimal app
        print("\nSuggestion: Creating minimal working app...")
        if create_minimal_working_app():
            print("Minimal app created successfully!")
            print("You can test with: python minimal_app.py")
        
        return False
    else:
        print("All login tests passed!")
        return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
