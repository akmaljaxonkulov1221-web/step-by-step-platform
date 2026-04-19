#!/usr/bin/env python3
"""
Database migration script for new features
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app, db
    from datetime import datetime
    from sqlalchemy import text as db_text
    APP_AVAILABLE = True
except ImportError as e:
    print(f"Error importing app: {e}")
    APP_AVAILABLE = False

def migrate_database():
    """Add new columns and tables for PDF upload and weekly schedule features"""
    print("Starting database migration...")
    
    with app.app_context():
        try:
            # Add PDF columns to subject table
            print("Adding PDF columns to subject table...")
            with db.engine.connect() as conn:
                conn.execute(db_text('ALTER TABLE subject ADD COLUMN pdf_file_path VARCHAR(500)'))
                print("  - Added pdf_file_path column")
                
                conn.execute(db_text('ALTER TABLE subject ADD COLUMN pdf_filename VARCHAR(255)'))
                print("  - Added pdf_filename column")
                conn.commit()
            
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("  - PDF columns already exist in subject table")
            else:
                print(f"  - Error adding PDF columns to subject: {e}")
        
        try:
            # Add PDF columns to topic table
            print("Adding PDF columns to topic table...")
            with db.engine.connect() as conn:
                from sqlalchemy import text
                conn.execute(text('ALTER TABLE topic ADD COLUMN pdf_file_path VARCHAR(500)'))
                print("  - Added pdf_file_path column")
                
                conn.execute(text('ALTER TABLE topic ADD COLUMN pdf_filename VARCHAR(255)'))
                print("  - Added pdf_filename column")
                conn.commit()
            
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("  - PDF columns already exist in topic table")
            else:
                print(f"  - Error adding PDF columns to topic: {e}")
        
        try:
            # Add PDF columns to test table
            print("Adding PDF columns to test table...")
            with db.engine.connect() as conn:
                from sqlalchemy import text
                conn.execute(text('ALTER TABLE test ADD COLUMN pdf_file_path VARCHAR(500)'))
                print("  - Added pdf_file_path column")
                
                conn.execute(text('ALTER TABLE test ADD COLUMN pdf_filename VARCHAR(255)'))
                print("  - Added pdf_filename column")
                conn.commit()
            
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("  - PDF columns already exist in test table")
            else:
                print(f"  - Error adding PDF columns to test: {e}")
        
        try:
            # Create weekly_test_schedule table
            print("Creating weekly_test_schedule table...")
            with db.engine.connect() as conn:
                conn.execute(db_text('''
                    CREATE TABLE IF NOT EXISTS weekly_test_schedule (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        group_id INTEGER NOT NULL,
                        subject_id INTEGER NOT NULL,
                        test_id INTEGER NOT NULL,
                        day_number INTEGER NOT NULL,
                        week_start_date DATE NOT NULL,
                        is_completed BOOLEAN DEFAULT 0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (group_id) REFERENCES "group" (id),
                        FOREIGN KEY (subject_id) REFERENCES subject (id),
                        FOREIGN KEY (test_id) REFERENCES test (id)
                    )
                '''))
                conn.commit()
            print("  - weekly_test_schedule table created")
            
        except Exception as e:
            print(f"  - Error creating weekly_test_schedule table: {e}")
        
        # Commit changes
        db.session.commit()
        print("Database migration completed successfully!")

def verify_migration():
    """Verify that the migration was successful"""
    print("\nVerifying migration...")
    
    with app.app_context():
        try:
            # Check if PDF columns exist
            with db.engine.connect() as conn:
                result = conn.execute(db_text("PRAGMA table_info(subject)"))
                columns = [row[1] for row in result]
                
                print(f"Subject table columns: {columns}")
                
                if 'pdf_file_path' in columns and 'pdf_filename' in columns:
                    print("  - PDF columns exist in subject table")
                else:
                    print("  - PDF columns missing from subject table")
                
                # Check if weekly_test_schedule table exists
                result = conn.execute(db_text("SELECT name FROM sqlite_master WHERE type='table' AND name='weekly_test_schedule'"))
                tables = [row[0] for row in result]
                
                if 'weekly_test_schedule' in tables:
                    print("  - weekly_test_schedule table exists")
                else:
                    print("  - weekly_test_schedule table missing")
                
        except Exception as e:
            print(f"Error verifying migration: {e}")

def main():
    """Run migration and verification"""
    if not APP_AVAILABLE:
        print("Cannot run migration - app not available")
        return False
    
    try:
        migrate_database()
        verify_migration()
        return True
    except Exception as e:
        print(f"Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
