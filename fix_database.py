#!/usr/bin/env python3
"""
Fix Database Schema
Add missing columns to topic table
"""

import os
import sys
import sqlite3

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def fix_topic_table():
    """Fix topic table schema"""
    print("=== FIXING TOPIC TABLE SCHEMA ===")
    
    try:
        conn = sqlite3.connect('education_complete.db')
        cursor = conn.cursor()
        
        # Check current columns
        cursor.execute("PRAGMA table_info(topic)")
        columns = cursor.fetchall()
        current_columns = [col[1] for col in columns]
        
        print(f"Current columns: {current_columns}")
        
        # Add missing name column
        if 'name' not in current_columns:
            cursor.execute("ALTER TABLE topic ADD COLUMN name TEXT")
            print("Added name column")
        else:
            print("name column already exists")
        
        # Update existing topics to have name
        cursor.execute("UPDATE topic SET name = title WHERE name IS NULL")
        print("Updated existing topics with names")
        
        conn.commit()
        conn.close()
        
        print("Topic table fixed successfully!")
        return True
        
    except Exception as e:
        print(f"Error fixing topic table: {e}")
        return False

def main():
    """Main function"""
    print("STEP BY STEP EDUCATION PLATFORM - DATABASE FIX")
    print("Fixing database schema...")
    
    if fix_topic_table():
        print("Database fix completed!")
        return True
    else:
        print("Database fix failed!")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
