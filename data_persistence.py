#!/usr/bin/env python3
"""
Data Persistence and Backup System
Ensures data is preserved and backed up
"""

import os
import sys
import sqlite3
import json
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_backup_system():
    """Create backup system for data persistence"""
    print("=== CREATING BACKUP SYSTEM ===")
    
    try:
        # Create backups directory
        os.makedirs('backups', exist_ok=True)
        
        # Create backup function
        backup_script = '''
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
'''
        
        with open('backup_system.py', 'w', encoding='utf-8') as f:
            f.write(backup_script)
        
        print("Backup system created!")
        return True
        
    except Exception as e:
        print(f"Error creating backup system: {e}")
        return False

def add_data_persistence_routes():
    """Add data persistence routes to app.py"""
    print("=== ADDING DATA PERSISTENCE ROUTES ===")
    
    try:
        # Read current app.py
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add backup and restore routes
        persistence_routes = '''
@app.route('/admin/backup')
def admin_backup():
    if not session.get('logged_in', False) or not session.get('is_admin', False):
        return redirect(url_for('login'))
    
    try:
        from backup_system import backup_database
        backup_file = backup_database()
        
        if backup_file:
            flash("Database backup created successfully!", 'success')
        else:
            flash("Failed to create backup!", 'danger')
        
        return redirect(url_for('admin_dashboard'))
        
    except Exception as e:
        app.logger.error(f"Backup error: {str(e)}")
        flash("Backup failed!", 'danger')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/restore', methods=['GET', 'POST'])
def admin_restore():
    if not session.get('logged_in', False) or not session.get('is_admin', False):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        backup_file = request.form.get('backup_file')
        
        if not backup_file:
            return render_template('admin_restore.html', error="Backup file tanlang!")
        
        try:
            from backup_system import restore_database
            if restore_database(backup_file):
                flash("Database restored successfully!", 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                return render_template('admin_restore.html', error="Restore failed!")
                
        except Exception as e:
            app.logger.error(f"Restore error: {str(e)}")
            return render_template('admin_restore.html', error="Restore failed!")
    
    # Get available backup files
    backup_files = []
    if os.path.exists('backups'):
        backup_files = [f for f in os.listdir('backups') if f.endswith('.json')]
        backup_files.sort(reverse=True)
    
    return render_template('admin_restore.html', backup_files=backup_files)

@app.route('/admin/export_data')
def admin_export_data():
    if not session.get('logged_in', False) or not session.get('is_admin', False):
        return redirect(url_for('login'))
    
    try:
        import app
        
        with app.app.app_context():
            # Export all data to JSON
            export_data = {
                'timestamp': datetime.now().isoformat(),
                'users': [],
                'groups': [],
                'subjects': [],
                'topics': [],
                'tests': [],
                'questions': [],
                'test_results': [],
                'certificates': []
            }
            
            # Users
            users = app.User.query.all()
            for user in users:
                export_data['users'].append({
                    'id': user.id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_admin': user.is_admin,
                    'is_group_leader': user.is_group_leader,
                    'group_id': user.group_id
                })
            
            # Groups
            groups = app.Group.query.all()
            for group in groups:
                export_data['groups'].append({
                    'id': group.id,
                    'name': group.name,
                    'description': group.description,
                    'total_score': group.total_score
                })
            
            # Subjects
            subjects = app.Subject.query.all()
            for subject in subjects:
                export_data['subjects'].append({
                    'id': subject.id,
                    'name': subject.name,
                    'description': subject.description
                })
            
            # Topics
            topics = app.Topic.query.all()
            for topic in topics:
                export_data['topics'].append({
                    'id': topic.id,
                    'name': topic.name,
                    'title': topic.title,
                    'description': topic.description,
                    'youtube_link': topic.youtube_link,
                    'pdf_file': topic.pdf_file,
                    'subject_id': topic.subject_id
                })
            
            # Tests
            tests = app.Test.query.all()
            for test in tests:
                export_data['tests'].append({
                    'id': test.id,
                    'title': test.title,
                    'test_type': test.test_type,
                    'test_date': test.test_date.isoformat() if test.test_date else None,
                    'subject_id': test.subject_id
                })
            
            # Questions
            questions = app.Question.query.all()
            for question in questions:
                export_data['questions'].append({
                    'id': question.id,
                    'test_id': question.test_id,
                    'question': question.question,
                    'option_a': question.option_a,
                    'option_b': question.option_b,
                    'option_c': question.option_c,
                    'option_d': question.option_d,
                    'correct_answer': question.correct_answer
                })
            
            # Test Results
            test_results = app.TestResult.query.all()
            for result in test_results:
                export_data['test_results'].append({
                    'id': result.id,
                    'user_id': result.user_id,
                    'test_id': result.test_id,
                    'score': result.score,
                    'total_questions': result.total_questions,
                    'percentage': result.percentage,
                    'correct_answers': result.correct_answers,
                    'incorrect_answers': result.incorrect_answers,
                    'total_time': result.total_time,
                    'taken_at': result.taken_at.isoformat() if result.taken_at else None
                })
            
            # Certificates
            certificates = app.Certificate.query.all()
            for cert in certificates:
                export_data['certificates'].append({
                    'id': cert.id,
                    'title': cert.title,
                    'description': cert.description,
                    'level': cert.level,
                    'subject_level': cert.subject_level,
                    'certificate_type': cert.certificate_type,
                    'points': cert.points,
                    'user_id': cert.user_id,
                    'issued_date': cert.issued_date.isoformat() if cert.issued_date else None
                })
            
            # Save export file
            export_filename = f"education_data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(export_filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            flash(f"Data exported to {export_filename}", 'success')
            return redirect(url_for('admin_dashboard'))
            
    except Exception as e:
        app.logger.error(f"Export error: {str(e)}")
        flash("Export failed!", 'danger')
        return redirect(url_for('admin_dashboard'))

'''
        
        # Add before last route
        last_route_pos = content.rfind('@app.route')
        if last_route_pos != -1:
            content = content[:last_route_pos] + persistence_routes + '\n' + content[last_route_pos:]
        
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("Data persistence routes added!")
        return True
        
    except Exception as e:
        print(f"Error adding persistence routes: {e}")
        return False

def create_restore_template():
    """Create restore template"""
    print("=== CREATING RESTORE TEMPLATE ===")
    
    template_content = '''{% extends "base.html" %}

{% block title %}Database Restore{% endblock %}

{% block page_title %}Database Restore{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="row justify-content-center">
        <div class="col-md-8">
            <div class="card">
                <div class="card-header bg-warning text-dark">
                    <h5 class="mb-0">
                        <i class="fas fa-database"></i> Database Restore
                    </h5>
                </div>
                <div class="card-body">
                    {% if error %}
                    <div class="alert alert-danger">
                        {{ error }}
                    </div>
                    {% endif %}
                    
                    <div class="alert alert-warning">
                        <i class="fas fa-exclamation-triangle"></i>
                        <strong>Diqqat!</strong> Database restore amalga oshirilganda, joriy ma'lumotlar o'chiriladi va backup ma'lumotlari qayta tiklanadi.
                    </div>
                    
                    <form method="POST">
                        <div class="mb-3">
                            <label for="backup_file" class="form-label">Backup faylini tanlang</label>
                            <select class="form-select" id="backup_file" name="backup_file" required>
                                <option value="">Backup faylini tanlang...</option>
                                {% for file in backup_files %}
                                <option value="{{ file }}">{{ file }}</option>
                                {% endfor %}
                            </select>
                        </div>
                        
                        <div class="d-grid gap-2">
                            <button type="submit" class="btn btn-warning" onclick="return confirm('Rostdan ham database ni restore qilmoqchimisiz? Barcha joriy ma\'lumotlar o\'chiriladi!')">
                                <i class="fas fa-database"></i> Database Restore
                            </button>
                        </div>
                    </form>
                    
                    <div class="mt-4">
                        <h6>Qo'shimcha imkoniyatlar:</h6>
                        <div class="list-group">
                            <a href="{{ url_for('admin_backup') }}" class="list-group-item list-group-item-action">
                                <i class="fas fa-download"></i> Yangi backup yaratish
                            </a>
                            <a href="{{ url_for('admin_export_data') }}" class="list-group-item list-group-item-action">
                                <i class="fas fa-file-export"></i> Ma'lumotlarni export qilish
                            </a>
                            <a href="{{ url_for('admin_dashboard') }}" class="list-group-item list-group-item-action">
                                <i class="fas fa-arrow-left"></i> Admin panelga qaytish
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''
    
    try:
        with open('templates/admin_restore.html', 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        print("Restore template created!")
        return True
        
    except Exception as e:
        print(f"Error creating restore template: {e}")
        return False

def main():
    """Main data persistence implementation"""
    print("STEP BY STEP EDUCATION PLATFORM - DATA PERSISTENCE")
    print("Implementing data persistence and backup system...")
    
    success_steps = []
    
    if create_backup_system():
        success_steps.append("Backup System")
    else:
        print("Failed to create backup system")
        return False
    
    if add_data_persistence_routes():
        success_steps.append("Persistence Routes")
    else:
        print("Failed to add persistence routes")
        return False
    
    if create_restore_template():
        success_steps.append("Restore Template")
    else:
        print("Failed to create restore template")
        return False
    
    print(f"\n=== DATA PERSISTENCE IMPLEMENTATION COMPLETE ===")
    print(f"Successfully implemented: {', '.join(success_steps)}")
    print("Data persistence and backup system added!")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
