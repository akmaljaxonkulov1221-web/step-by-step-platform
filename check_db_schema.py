#!/usr/bin/env python3
"""
Check Database Schema Script
Checks actual database schema and compares with models
"""

import os
import sys
import sqlite3

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_database_schema():
    """Check actual database schema"""
    print("=== CHECKING DATABASE SCHEMA ===")
    
    db_path = 'education_complete.db'
    if not os.path.exists(db_path):
        print("Database file not found!")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check group table
        print("\n--- Group Table Schema ---")
        cursor.execute("PRAGMA table_info('group')")
        group_columns = cursor.fetchall()
        for col in group_columns:
            print(f"  {col[1]}: {col[2]} (nullable: {'YES' if col[3] == 0 else 'NO'})")
        
        # Check subject table
        print("\n--- Subject Table Schema ---")
        cursor.execute("PRAGMA table_info('subject')")
        subject_columns = cursor.fetchall()
        for col in subject_columns:
            print(f"  {col[1]}: {col[2]} (nullable: {'YES' if col[3] == 0 else 'NO'})")
        
        # Check user table
        print("\n--- User Table Schema ---")
        cursor.execute("PRAGMA table_info('user')")
        user_columns = cursor.fetchall()
        for col in user_columns:
            print(f"  {col[1]}: {col[2]} (nullable: {'YES' if col[3] == 0 else 'NO'})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Schema check error: {e}")
        return False

def fix_model_definitions():
    """Fix model definitions to match actual database schema"""
    print("\n=== FIXING MODEL DEFINITIONS ===")
    
    try:
        # Read current app.py
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove created_at and updated_at from Group model
        content = content.replace(
            '    created_at = db.Column(db.DateTime, nullable=True)\n    updated_at = db.Column(db.DateTime, nullable=True)',
            ''
        )
        
        # Remove created_at and updated_at from Subject model
        content = content.replace(
            '    created_at = db.Column(db.DateTime, nullable=True)\n    updated_at = db.Column(db.DateTime, nullable=True)',
            ''
        )
        
        # Remove created_at and updated_at from User model
        content = content.replace(
            '    created_at = db.Column(db.DateTime, nullable=True)\n    updated_at = db.Column(db.DateTime, nullable=True)',
            ''
        )
        
        # Remove created_at and updated_at from Topic model
        content = content.replace(
            '    created_at = db.Column(db.DateTime, nullable=True)\n    updated_at = db.Column(db.DateTime, nullable=True)',
            ''
        )
        
        # Remove created_at and updated_at from Test model
        content = content.replace(
            '    created_at = db.Column(db.DateTime, nullable=True)\n    updated_at = db.Column(db.DateTime, nullable=True)',
            ''
        )
        
        # Remove created_at and updated_at from Question model
        content = content.replace(
            '    created_at = db.Column(db.DateTime, nullable=True)\n    updated_at = db.Column(db.DateTime, nullable=True)',
            ''
        )
        
        # Remove created_at and updated_at from Schedule model
        content = content.replace(
            '    created_at = db.Column(db.DateTime, nullable=True)\n    updated_at = db.Column(db.DateTime, nullable=True)',
            ''
        )
        
        # Remove created_at and updated_at from Certificate model
        content = content.replace(
            '    created_at = db.Column(db.DateTime, nullable=True)\n    updated_at = db.Column(db.DateTime, nullable=True)',
            ''
        )
        
        # Write fixed content back
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("Model definitions fixed!")
        return True
        
    except Exception as e:
        print(f"Model fix error: {e}")
        return False

def test_fixed_models():
    """Test fixed models"""
    print("\n=== TESTING FIXED MODELS ===")
    
    try:
        import app
        
        with app.app.app_context():
            # Test group query
            groups = app.Group.query.limit(1).all()
            print("Group query: OK")
            
            # Test user query
            users = app.User.query.limit(1).all()
            print("User query: OK")
            
            # Test subject query
            subjects = app.Subject.query.limit(1).all()
            print("Subject query: OK")
            
            print("Fixed models test: OK")
            return True
            
    except Exception as e:
        print(f"Fixed models test error: {e}")
        return False

def main():
    """Main function"""
    print("STEP BY STEP EDUCATION PLATFORM - DATABASE SCHEMA CHECK")
    print("Checking and fixing database schema...")
    
    if check_database_schema():
        print("\nSchema check successful!")
        
        if fix_model_definitions():
            print("Model definitions fixed!")
            
            if test_fixed_models():
                print("All tests passed!")
                return True
            else:
                print("Fixed models test failed!")
                return False
        else:
            print("Model fix failed!")
            return False
    else:
        print("Schema check failed!")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
