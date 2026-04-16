#!/usr/bin/env python3
"""
Database Migration Script for Step by Step Education Platform
Updates database schema to match new models
"""

import os
import sys
import sqlite3
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def migrate_database():
    """Migrate database to new schema"""
    print("=== DATABASE MIGRATION ===")
    
    db_path = 'education_complete.db'
    if not os.path.exists(db_path):
        print("Database file not found!")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get current schema
        cursor.execute("PRAGMA table_info('group')")
        group_columns = [row[1] for row in cursor.fetchall()]
        print(f"Current group columns: {group_columns}")
        
        # Add missing columns to group table
        if 'created_at' not in group_columns:
            print("Adding created_at column to group table...")
            cursor.execute("ALTER TABLE 'group' ADD COLUMN created_at DATETIME")
            # Set default values for existing rows
            cursor.execute("UPDATE 'group' SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")
        
        if 'updated_at' not in group_columns:
            print("Adding updated_at column to group table...")
            cursor.execute("ALTER TABLE 'group' ADD COLUMN updated_at DATETIME")
            # Set default values for existing rows
            cursor.execute("UPDATE 'group' SET updated_at = CURRENT_TIMESTAMP WHERE updated_at IS NULL")
        
        # Check subject table
        cursor.execute("PRAGMA table_info(subject)")
        subject_columns = [row[1] for row in cursor.fetchall()]
        print(f"Current subject columns: {subject_columns}")
        
        if 'created_at' not in subject_columns:
            print("Adding created_at column to subject table...")
            cursor.execute("ALTER TABLE subject ADD COLUMN created_at DATETIME")
            cursor.execute("UPDATE subject SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")
        
        if 'updated_at' not in subject_columns:
            print("Adding updated_at column to subject table...")
            cursor.execute("ALTER TABLE subject ADD COLUMN updated_at DATETIME")
            cursor.execute("UPDATE subject SET updated_at = CURRENT_TIMESTAMP WHERE updated_at IS NULL")
        
        # Check topic table
        cursor.execute("PRAGMA table_info(topic)")
        topic_columns = [row[1] for row in cursor.fetchall()]
        print(f"Current topic columns: {topic_columns}")
        
        if 'created_at' not in topic_columns:
            print("Adding created_at column to topic table...")
            cursor.execute("ALTER TABLE topic ADD COLUMN created_at DATETIME")
            cursor.execute("UPDATE topic SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")
        
        if 'updated_at' not in topic_columns:
            print("Adding updated_at column to topic table...")
            cursor.execute("ALTER TABLE topic ADD COLUMN updated_at DATETIME")
            cursor.execute("UPDATE topic SET updated_at = CURRENT_TIMESTAMP WHERE updated_at IS NULL")
        
        # Check test table
        cursor.execute("PRAGMA table_info(test)")
        test_columns = [row[1] for row in cursor.fetchall()]
        print(f"Current test columns: {test_columns}")
        
        if 'created_at' not in test_columns:
            print("Adding created_at column to test table...")
            cursor.execute("ALTER TABLE test ADD COLUMN created_at DATETIME")
            cursor.execute("UPDATE test SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")
        
        if 'updated_at' not in test_columns:
            print("Adding updated_at column to test table...")
            cursor.execute("ALTER TABLE test ADD COLUMN updated_at DATETIME")
            cursor.execute("UPDATE test SET updated_at = CURRENT_TIMESTAMP WHERE updated_at IS NULL")
        
        # Check question table
        cursor.execute("PRAGMA table_info(question)")
        question_columns = [row[1] for row in cursor.fetchall()]
        print(f"Current question columns: {question_columns}")
        
        if 'created_at' not in question_columns:
            print("Adding created_at column to question table...")
            cursor.execute("ALTER TABLE question ADD COLUMN created_at DATETIME")
            cursor.execute("UPDATE question SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")
        
        if 'updated_at' not in question_columns:
            print("Adding updated_at column to question table...")
            cursor.execute("ALTER TABLE question ADD COLUMN updated_at DATETIME")
            cursor.execute("UPDATE question SET updated_at = CURRENT_TIMESTAMP WHERE updated_at IS NULL")
        
        # Check schedule table
        cursor.execute("PRAGMA table_info(schedule)")
        schedule_columns = [row[1] for row in cursor.fetchall()]
        print(f"Current schedule columns: {schedule_columns}")
        
        if 'created_at' not in schedule_columns:
            print("Adding created_at column to schedule table...")
            cursor.execute("ALTER TABLE schedule ADD COLUMN created_at DATETIME")
            cursor.execute("UPDATE schedule SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")
        
        if 'updated_at' not in schedule_columns:
            print("Adding updated_at column to schedule table...")
            cursor.execute("ALTER TABLE schedule ADD COLUMN updated_at DATETIME")
            cursor.execute("UPDATE schedule SET updated_at = CURRENT_TIMESTAMP WHERE updated_at IS NULL")
        
        # Check certificate table
        cursor.execute("PRAGMA table_info(certificate)")
        certificate_columns = [row[1] for row in cursor.fetchall()]
        print(f"Current certificate columns: {certificate_columns}")
        
        if 'created_at' not in certificate_columns:
            print("Adding created_at column to certificate table...")
            cursor.execute("ALTER TABLE certificate ADD COLUMN created_at DATETIME")
            cursor.execute("UPDATE certificate SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")
        
        if 'updated_at' not in certificate_columns:
            print("Adding updated_at column to certificate table...")
            cursor.execute("ALTER TABLE certificate ADD COLUMN updated_at DATETIME")
            cursor.execute("UPDATE certificate SET updated_at = CURRENT_TIMESTAMP WHERE updated_at IS NULL")
        
        # Check user table
        cursor.execute("PRAGMA table_info(user)")
        user_columns = [row[1] for row in cursor.fetchall()]
        print(f"Current user columns: {user_columns}")
        
        if 'created_at' not in user_columns:
            print("Adding created_at column to user table...")
            cursor.execute("ALTER TABLE user ADD COLUMN created_at DATETIME")
            cursor.execute("UPDATE user SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")
        
        if 'updated_at' not in user_columns:
            print("Adding updated_at column to user table...")
            cursor.execute("ALTER TABLE user ADD COLUMN updated_at DATETIME")
            cursor.execute("UPDATE user SET updated_at = CURRENT_TIMESTAMP WHERE updated_at IS NULL")
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print("Database migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"Migration error: {e}")
        if conn:
            conn.close()
        return False

def test_migration():
    """Test if migration was successful"""
    print("\n=== TESTING MIGRATION ===")
    
    try:
        import app
        
        with app.app.app_context():
            # Test database operations
            print("Testing database operations...")
            
            # Test group creation
            test_group = app.Group(name='MigrationTest', description='Test group')
            app.db.session.add(test_group)
            app.db.session.flush()
            
            # Test user creation
            test_user = app.User(
                username='migrationtest',
                password_hash='test_hash',
                first_name='Migration',
                last_name='Test',
                group_id=test_group.id
            )
            app.db.session.add(test_user)
            app.db.session.flush()
            
            # Test relationships
            assert test_user.group == test_group
            assert test_group.students[0] == test_user
            
            # Clean up
            app.db.session.delete(test_user)
            app.db.session.delete(test_group)
            app.db.session.commit()
            
            print("Migration test: OK")
            return True
            
    except Exception as e:
        print(f"Migration test error: {e}")
        return False

def main():
    """Main migration function"""
    print("STEP BY STEP EDUCATION PLATFORM - DATABASE MIGRATION")
    print("Migrating database to new schema...")
    
    if migrate_database():
        print("\nMigration successful!")
        
        if test_migration():
            print("All tests passed!")
            return True
        else:
            print("Migration tests failed!")
            return False
    else:
        print("Migration failed!")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
