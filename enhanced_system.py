#!/usr/bin/env python3
"""
Enhanced System Implementation
Adds new features and fixes existing issues
"""

import os
import sys
import sqlite3
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_enhanced_database_schema():
    """Create enhanced database schema for new features"""
    print("=== CREATING ENHANCED DATABASE SCHEMA ===")
    
    try:
        conn = sqlite3.connect('education_complete.db')
        cursor = conn.cursor()
        
        # 1. Enhanced Topics table with YouTube, PDF, description
        print("1. Enhancing Topics table...")
        try:
            cursor.execute('''
                ALTER TABLE topic ADD COLUMN youtube_link TEXT
            ''')
            print("   Added youtube_link column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("   youtube_link column already exists")
            else:
                print(f"   Error adding youtube_link: {e}")
        
        try:
            cursor.execute('''
                ALTER TABLE topic ADD COLUMN pdf_file TEXT
            ''')
            print("   Added pdf_file column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("   pdf_file column already exists")
            else:
                print(f"   Error adding pdf_file: {e}")
        
        try:
            cursor.execute('''
                ALTER TABLE topic ADD COLUMN description TEXT
            ''')
            print("   Added description column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("   description column already exists")
            else:
                print(f"   Error adding description: {e}")
        
        # 2. AI Chat table
        print("2. Creating AI Chat table...")
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ai_chat (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    topic_id INTEGER,
                    test_generated BOOLEAN DEFAULT FALSE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES user (id),
                    FOREIGN KEY (topic_id) REFERENCES topic (id)
                )
            ''')
            print("   AI Chat table created")
        except Exception as e:
            print(f"   Error creating AI Chat table: {e}")
        
        # 3. Enhanced Certificates table
        print("3. Enhancing Certificates table...")
        try:
            cursor.execute('''
                ALTER TABLE certificate ADD COLUMN subject_level TEXT
            ''')
            print("   Added subject_level column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("   subject_level column already exists")
            else:
                print(f"   Error adding subject_level: {e}")
        
        try:
            cursor.execute('''
                ALTER TABLE certificate ADD COLUMN certificate_type TEXT DEFAULT 'achievement'
            ''')
            print("   Added certificate_type column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("   certificate_type column already exists")
            else:
                print(f"   Error adding certificate_type: {e}")
        
        # 4. Test Results enhancement
        print("4. Enhancing Test Results table...")
        try:
            cursor.execute('''
                ALTER TABLE test_result ADD COLUMN correct_answers TEXT
            ''')
            print("   Added correct_answers column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("   correct_answers column already exists")
            else:
                print(f"   Error adding correct_answers: {e}")
        
        try:
            cursor.execute('''
                ALTER TABLE test_result ADD COLUMN incorrect_answers TEXT
            ''')
            print("   Added incorrect_answers column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("   incorrect_answers column already exists")
            else:
                print(f"   Error adding incorrect_answers: {e}")
        
        try:
            cursor.execute('''
                ALTER TABLE test_result ADD COLUMN total_time INTEGER DEFAULT 0
            ''')
            print("   Added total_time column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("   total_time column already exists")
            else:
                print(f"   Error adding total_time: {e}")
        
        conn.commit()
        conn.close()
        
        print("Enhanced database schema created successfully!")
        return True
        
    except Exception as e:
        print(f"Database schema error: {e}")
        return False

def update_app_models():
    """Update app.py models for new features"""
    print("\n=== UPDATING APP MODELS ===")
    
    try:
        # Read current app.py
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add AI Chat model
        if 'class AIChat' not in content:
            ai_chat_model = '''
class AIChat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'))
    test_generated = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, nullable=True)
    
    user = db.relationship('User', backref=db.backref('ai_chats', lazy=True, cascade='all, delete-orphan'))
    topic = db.relationship('Topic', backref=db.backref('ai_chats', lazy=True))

'''
            
            # Find where to insert the model (after Topic model)
            topic_end = content.find('class Test')
            if topic_end == -1:
                topic_end = content.find('@app.route')
            
            if topic_end != -1:
                content = content[:topic_end] + ai_chat_model + '\n' + content[topic_end:]
        
        # Update Topic model with new fields
        if 'youtube_link' not in content:
            # Find Topic model and add new fields
            topic_start = content.find('class Topic')
            if topic_start != -1:
                topic_end = content.find('class ', topic_start + 1)
                if topic_end == -1:
                    topic_end = content.find('@app.route', topic_start)
                
                if topic_end != -1:
                    topic_model = content[topic_start:topic_end]
                    
                    # Add new fields before the last relationship
                    if 'subject = db.relationship' in topic_model:
                        insert_pos = topic_model.find('subject = db.relationship')
                        new_fields = '''    youtube_link = db.Column(db.Text)
    pdf_file = db.Column(db.Text)
    description = db.Column(db.Text)
    
    '''
                        topic_model = topic_model[:insert_pos] + new_fields + topic_model[insert_pos:]
                        content = content[:topic_start] + topic_model + content[topic_end:]
        
        # Update Certificate model
        if 'subject_level' not in content:
            cert_start = content.find('class Certificate')
            if cert_start != -1:
                cert_end = content.find('class ', cert_start + 1)
                if cert_end == -1:
                    cert_end = content.find('@app.route', cert_start)
                
                if cert_end != -1:
                    cert_model = content[cert_start:cert_end]
                    
                    # Add new fields
                    if 'user_id = db.Column' in cert_model:
                        insert_pos = cert_model.find('user_id = db.Column')
                        new_fields = '''    subject_level = db.Column(db.String(50))
    certificate_type = db.Column(db.String(50), default='achievement')
    '''
                        cert_model = cert_model[:insert_pos] + new_fields + cert_model[insert_pos:]
                        content = content[:cert_start] + cert_model + content[cert_end:]
        
        # Update TestResult model
        if 'correct_answers' not in content:
            result_start = content.find('class TestResult')
            if result_start != -1:
                result_end = content.find('class ', result_start + 1)
                if result_end == -1:
                    result_end = content.find('@app.route', result_start)
                
                if result_end != -1:
                    result_model = content[result_start:result_end]
                    
                    # Add new fields
                    if 'percentage = db.Column' in result_model:
                        insert_pos = result_model.find('percentage = db.Column')
                        new_fields = '''    correct_answers = db.Column(db.Text)
    incorrect_answers = db.Column(db.Text)
    total_time = db.Column(db.Integer, default=0)
    '''
                        result_model = result_model[:insert_pos] + new_fields + result_model[insert_pos:]
                        content = content[:result_start] + result_model + content[result_end:]
        
        # Write updated content
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("App models updated successfully!")
        return True
        
    except Exception as e:
        print(f"Error updating app models: {e}")
        return False

def create_sample_data():
    """Create sample data for testing"""
    print("\n=== CREATING SAMPLE DATA ===")
    
    try:
        import app
        
        with app.app.app_context():
            # Create sample topics with enhanced features
            subjects = app.Subject.query.all()
            if subjects:
                sample_topics = [
                    {
                        'name': 'Ingliz tili grammatikasi',
                        'subject_id': subjects[0].id,
                        'youtube_link': 'https://www.youtube.com/watch?v=sample1',
                        'pdf_file': 'grammar_basics.pdf',
                        'description': 'Ingliz tili grammatikasining asosiy qoidalari'
                    },
                    {
                        'name': 'Matematik masalalar',
                        'subject_id': subjects[0].id,
                        'youtube_link': 'https://www.youtube.com/watch?v=sample2',
                        'pdf_file': 'math_problems.pdf',
                        'description': 'Matematik masalalarni yechish usullari'
                    }
                ]
                
                for topic_data in sample_topics:
                    existing_topic = app.Topic.query.filter_by(name=topic_data['name']).first()
                    if not existing_topic:
                        topic = app.Topic(**topic_data)
                        app.db.session.add(topic)
                
                app.db.session.commit()
                print("Sample topics created!")
            
            # Create sample test result
            users = app.User.query.filter_by(is_admin=False).all()
            tests = app.Test.query.limit(1).all()
            
            if users and tests:
                sample_result = app.TestResult(
                    user_id=users[0].id,
                    test_id=tests[0].id,
                    score=15,
                    total_questions=20,
                    percentage=75.0,
                    correct_answers='1,2,3,4,5,6,7,8,9,10,11,12,13,14,15',
                    incorrect_answers='16,17,18,19,20',
                    total_time=1200
                )
                app.db.session.add(sample_result)
                app.db.session.commit()
                print("Sample test result created!")
            
            return True
            
    except Exception as e:
        print(f"Error creating sample data: {e}")
        return False

def main():
    """Main enhancement function"""
    print("STEP BY STEP EDUCATION PLATFORM - SYSTEM ENHANCEMENT")
    print("Enhancing system with new features...")
    
    success_steps = []
    
    # Create enhanced database schema
    if create_enhanced_database_schema():
        success_steps.append("Database Schema")
    else:
        print("Failed to create enhanced database schema")
        return False
    
    # Update app models
    if update_app_models():
        success_steps.append("App Models")
    else:
        print("Failed to update app models")
        return False
    
    # Create sample data
    if create_sample_data():
        success_steps.append("Sample Data")
    else:
        print("Failed to create sample data")
        return False
    
    print(f"\n=== ENHANCEMENT COMPLETE ===")
    print(f"Successfully completed: {', '.join(success_steps)}")
    print("System enhanced with new features!")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
