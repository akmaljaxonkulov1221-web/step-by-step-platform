#!/usr/bin/env python3
"""
Production Fix Script for Render.com Deployment
This script fixes common issues that cause Internal Server Error on Render.com
"""

import os
import sys
import sqlite3
from flask import Flask
from werkzeug.security import generate_password_hash

def fix_database_path():
    """Fix database path for production deployment"""
    print("=== Database Path Fix ===")
    
    # Check if database exists in instance directory
    instance_db_path = 'instance/education_complete.db'
    root_db_path = 'education_complete.db'
    
    if os.path.exists(instance_db_path):
        print(f"Database found in instance directory: {instance_db_path}")
        
        # Copy database to root directory for Render.com
        if not os.path.exists(root_db_path):
            import shutil
            shutil.copy2(instance_db_path, root_db_path)
            print(f"Copied database to root directory: {root_db_path}")
        else:
            print(f"Database already exists in root directory: {root_db_path}")
            
        return True
    else:
        print(f"Database not found in instance directory: {instance_db_path}")
        return False

def create_database_if_missing():
    """Create database if it doesn't exist"""
    print("\n=== Database Creation ===")
    
    db_path = 'education_complete.db'
    
    if not os.path.exists(db_path):
        print("Creating new database...")
        
        # Create database connection
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                is_admin BOOLEAN DEFAULT FALSE,
                is_group_leader BOOLEAN DEFAULT FALSE,
                needs_password_change BOOLEAN DEFAULT FALSE,
                group_id INTEGER
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS "group" (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                total_score INTEGER DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subject (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                subject_id INTEGER,
                test_type TEXT,
                test_date DATE,
                start_time TIME,
                end_time TIME,
                duration_minutes INTEGER
            )
        ''')
        
        # Insert default admin user
        admin_group_id = 1
        cursor.execute('INSERT INTO "group" (name, description, total_score) VALUES (?, ?, ?)', 
                      ('Admin', 'Admin group', 0))
        
        admin_password_hash = generate_password_hash('admin123')
        cursor.execute('INSERT INTO user (username, password_hash, first_name, last_name, is_admin, is_group_leader, needs_password_change, group_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', 
                      ('admin', admin_password_hash, 'Admin', 'User', True, False, False, admin_group_id))
        
        # Insert default subjects
        subjects = [
            ('Matematika', 'Matematika fani'),
            ('Fizika', 'Fizika fani'),
            ('Kimyo', 'Kimyo fani'),
            ('Biologiya', 'Biologiya fani'),
            ('Ingliz tili', 'Ingliz tili fani')
        ]
        
        for subject_name, subject_desc in subjects:
            cursor.execute('INSERT INTO subject (name, description) VALUES (?, ?)', 
                          (subject_name, subject_desc))
        
        conn.commit()
        conn.close()
        
        print("Database created successfully!")
        return True
    else:
        print("Database already exists!")
        return True

def check_app_configuration():
    """Check Flask app configuration"""
    print("\n=== App Configuration Check ===")
    
    try:
        # Import app
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import app
        
        with app.app.app_context():
            # Check database configuration
            db_uri = app.app.config.get('SQLALCHEMY_DATABASE_URI')
            print(f"Database URI: {db_uri}")
            
            # Test database connection
            try:
                app.db.create_all()
                print("Database connection: OK")
            except Exception as e:
                print(f"Database connection: ERROR - {e}")
                return False
                
            # Check if admin user exists
            try:
                admin_user = app.User.query.filter_by(username='admin').first()
                if admin_user:
                    print("Admin user: OK")
                else:
                    print("Admin user: MISSING")
                    return False
            except Exception as e:
                print(f"Admin user check: ERROR - {e}")
                return False
                
        return True
        
    except Exception as e:
        print(f"App configuration check: ERROR - {e}")
        return False

def test_admin_dashboard():
    """Test admin dashboard functionality"""
    print("\n=== Admin Dashboard Test ===")
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import app
        
        with app.app.app_context():
            with app.app.test_client() as client:
                # Test admin login
                response = client.post('/login', data={
                    'username': 'admin',
                    'password': 'admin123'
                }, follow_redirects=True)
                
                if response.status_code == 200:
                    print("Admin login: OK")
                    
                    # Test admin dashboard
                    response = client.get('/admin/dashboard')
                    if response.status_code == 200:
                        print("Admin dashboard: OK")
                        return True
                    else:
                        print(f"Admin dashboard: ERROR - {response.status_code}")
                        return False
                else:
                    print(f"Admin login: ERROR - {response.status_code}")
                    return False
                    
    except Exception as e:
        print(f"Admin dashboard test: ERROR - {e}")
        return False

def main():
    """Main function to fix production issues"""
    print("=== Production Fix Script for Render.com ===")
    print("This script fixes common issues that cause Internal Server Error")
    print()
    
    all_fixes_successful = True
    
    # Fix 1: Database path
    if not fix_database_path():
        all_fixes_successful = False
    
    # Fix 2: Create database if missing
    if not create_database_if_missing():
        all_fixes_successful = False
    
    # Fix 3: Check app configuration
    if not check_app_configuration():
        all_fixes_successful = False
    
    # Fix 4: Test admin dashboard
    if not test_admin_dashboard():
        all_fixes_successful = False
    
    print("\n=== Summary ===")
    if all_fixes_successful:
        print("All fixes applied successfully!")
        print("The application should work correctly on Render.com.")
        print("If you're still getting Internal Server Error, please:")
        print("1. Wait a few minutes for Render.com to redeploy")
        print("2. Check the Render.com logs for specific errors")
        print("3. Try accessing the application again")
    else:
        print("Some fixes failed. Please check the errors above.")
    
    return all_fixes_successful

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
