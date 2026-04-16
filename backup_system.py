
import sqlite3
import json
import os
from datetime import datetime

def backup_database():
    """Backup database to JSON files"""
    try:
        conn = sqlite3.connect('education_complete.db')
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        backup_data = {}
        backup_timestamp = datetime.now().isoformat()
        
        for table in tables:
            cursor.execute(f"SELECT * FROM {table}")
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            
            backup_data[table] = {
                'columns': columns,
                'rows': rows
            }
        
        # Save backup
        backup_filename = f"backups/backup_{backup_timestamp.replace(':', '-')}.json"
        with open(backup_filename, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': backup_timestamp,
                'tables': backup_data
            }, f, indent=2, ensure_ascii=False)
        
        conn.close()
        print(f"Backup created: {backup_filename}")
        return backup_filename
        
    except Exception as e:
        print(f"Backup error: {e}")
        return None

def restore_database(backup_file):
    """Restore database from backup"""
    try:
        with open(backup_file, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        conn = sqlite3.connect('education_complete.db')
        cursor = conn.cursor()
        
        for table_name, table_data in backup_data['tables'].items():
            # Clear existing data
            cursor.execute(f"DELETE FROM {table_name}")
            
            # Insert backup data
            if table_data['rows']:
                placeholders = ', '.join(['?'] * len(table_data['columns']))
                insert_sql = f"INSERT INTO {table_name} ({', '.join(table_data['columns'])}) VALUES ({placeholders})"
                
                for row in table_data['rows']:
                    cursor.execute(insert_sql, row)
        
        conn.commit()
        conn.close()
        
        print(f"Database restored from: {backup_file}")
        return True
        
    except Exception as e:
        print(f"Restore error: {e}")
        return False

if __name__ == '__main__':
    backup_database()
