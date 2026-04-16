#!/usr/bin/env python3
"""
Fix Database Schema
Add missing columns to test_result table
"""

import os
import sys
import sqlite3

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_database_schema():
    """Check current database schema"""
    print("=== CHECKING DATABASE SCHEMA ===")
    
    try:
        conn = sqlite3.connect('education_complete.db')
        cursor = conn.cursor()
        
        # Check test_result table columns
        cursor.execute("PRAGMA table_info(test_result)")
        columns = cursor.fetchall()
        current_columns = [col[1] for col in columns]
        
        print(f"Current test_result columns: {current_columns}")
        
        # Check what columns are missing
        required_columns = [
            'correct_answers',
            'incorrect_answers', 
            'total_time'
        ]
        
        missing_columns = [col for col in required_columns if col not in current_columns]
        
        print(f"Missing columns: {missing_columns}")
        
        conn.close()
        return missing_columns
        
    except Exception as e:
        print(f"Error checking schema: {e}")
        return []

def add_missing_columns():
    """Add missing columns to test_result table"""
    print("\n=== ADDING MISSING COLUMNS ===")
    
    try:
        conn = sqlite3.connect('education_complete.db')
        cursor = conn.cursor()
        
        # Add missing columns
        columns_to_add = [
            ('correct_answers', 'TEXT'),
            ('incorrect_answers', 'TEXT'),
            ('total_time', 'INTEGER DEFAULT 0')
        ]
        
        for column_name, column_type in columns_to_add:
            try:
                cursor.execute(f"ALTER TABLE test_result ADD COLUMN {column_name} {column_type}")
                print(f"Added column: {column_name}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print(f"Column {column_name} already exists")
                else:
                    print(f"Error adding column {column_name}: {e}")
        
        conn.commit()
        conn.close()
        
        print("Missing columns added successfully!")
        return True
        
    except Exception as e:
        print(f"Error adding columns: {e}")
        return False

def update_test_result_model():
    """Update TestResult model to be compatible with database"""
    print("\n=== UPDATING TESTRESULT MODEL ===")
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find TestResult model and make columns optional
        lines = content.split('\n')
        new_lines = []
        
        for i, line in enumerate(lines):
            # Make correct_answers and incorrect_answers optional
            if 'correct_answers = db.Column(db.Text)' in line:
                new_lines.append(line.replace('correct_answers = db.Column(db.Text)', 'correct_answers = db.Column(db.Text, nullable=True)'))
            elif 'incorrect_answers = db.Column(db.Text)' in line:
                new_lines.append(line.replace('incorrect_answers = db.Column(db.Text)', 'incorrect_answers = db.Column(db.Text, nullable=True)'))
            elif 'total_time = db.Column(db.Integer, default=0)' in line:
                new_lines.append(line.replace('total_time = db.Column(db.Integer, default=0)', 'total_time = db.Column(db.Integer, default=0, nullable=True)'))
            else:
                new_lines.append(line)
        
        # Write back
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        
        print("TestResult model updated!")
        return True
        
    except Exception as e:
        print(f"Error updating model: {e}")
        return False

def test_database_after_fix():
    """Test database after fixing schema"""
    print("\n=== TESTING DATABASE AFTER FIX ===")
    
    try:
        import app
        
        with app.app.app_context():
            # Test TestResult query
            try:
                results = app.TestResult.query.limit(5).all()
                print(f"TestResult query: OK (found {len(results)} results)")
                return True
            except Exception as e:
                print(f"TestResult query error: {e}")
                return False
                
    except Exception as e:
        print(f"Database test error: {e}")
        return False

def main():
    """Main function"""
    print("STEP BY STEP EDUCATION PLATFORM - FIX DATABASE SCHEMA")
    print("Fixing missing database columns...")
    
    # Check what's missing
    missing_columns = check_database_schema()
    
    if missing_columns:
        # Add missing columns
        if add_missing_columns():
            # Update model
            if update_test_result_model():
                # Test after fix
                if test_database_after_fix():
                    print("\n=== DATABASE SCHEMA FIXED ===")
                    return True
                else:
                    print("\nDatabase test failed!")
                    return False
            else:
                print("\nModel update failed!")
                return False
        else:
            print("\nColumn addition failed!")
            return False
    else:
        print("No missing columns found!")
        return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
