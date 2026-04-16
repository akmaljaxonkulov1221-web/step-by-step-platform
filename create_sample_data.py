#!/usr/bin/env python3
"""
Create Sample Data
Create sample data for testing enhanced features
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_sample_data():
    """Create sample data for testing"""
    print("=== CREATING SAMPLE DATA ===")
    
    try:
        import app
        
        with app.app.app_context():
            # Create sample topics with enhanced features
            subjects = app.Subject.query.all()
            if not subjects:
                print("No subjects found, creating sample subject...")
                sample_subject = app.Subject(name="Ingliz tili", description="Ingliz tili kursi")
                app.db.session.add(sample_subject)
                app.db.session.flush()
                subjects = [sample_subject]
            
            # Create sample topics
            sample_topics = [
                {
                    'name': 'Ingliz tili grammatikasi',
                    'title': 'Ingliz tili grammatikasi',
                    'subject_id': subjects[0].id,
                    'youtube_link': 'https://www.youtube.com/watch?v=sample1',
                    'pdf_file': 'grammar_basics.pdf',
                    'description': 'Ingliz tili grammatikasining asosiy qoidalari'
                },
                {
                    'name': 'Matematik masalalar',
                    'title': 'Matematik masalalar',
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
                    print(f"Created topic: {topic_data['name']}")
                else:
                    print(f"Topic already exists: {topic_data['name']}")
            
            # Create sample test result
            users = app.User.query.filter_by(is_admin=False).all()
            tests = app.Test.query.limit(1).all()
            
            if users and tests:
                # Check if sample result already exists
                existing_result = app.TestResult.query.filter_by(user_id=users[0].id, test_id=tests[0].id).first()
                if not existing_result:
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
                    print("Created sample test result")
                else:
                    print("Sample test result already exists")
            
            # Create sample certificate
            if users:
                existing_cert = app.Certificate.query.filter_by(user_id=users[0].id).first()
                if not existing_cert:
                    sample_cert = app.Certificate(
                        title='Ingliz tili B2',
                        description='Ingliz tili B2 darajasi',
                        level='B2',
                        subject_level='B2',
                        certificate_type='achievement',
                        user_id=users[0].id
                    )
                    app.db.session.add(sample_cert)
                    print("Created sample certificate")
                else:
                    print("Sample certificate already exists")
            
            # Create sample AI chat
            if users:
                existing_chat = app.AIChat.query.filter_by(user_id=users[0].id).first()
                if not existing_chat:
                    sample_chat = app.AIChat(
                        user_id=users[0].id,
                        question='Ingliz tili grammatikasi haqida savol',
                        answer='Ingliz tili grammatikasi juda muhim...',
                        test_generated=False
                    )
                    app.db.session.add(sample_chat)
                    print("Created sample AI chat")
                else:
                    print("Sample AI chat already exists")
            
            app.db.session.commit()
            print("Sample data created successfully!")
            
            # Display created data
            print("\n=== CREATED DATA SUMMARY ===")
            print(f"Topics: {app.Topic.query.count()}")
            print(f"Test Results: {app.TestResult.query.count()}")
            print(f"Certificates: {app.Certificate.query.count()}")
            print(f"AI Chats: {app.AIChat.query.count()}")
            
            return True
            
    except Exception as e:
        print(f"Error creating sample data: {e}")
        return False

def main():
    """Main function"""
    print("STEP BY STEP EDUCATION PLATFORM - SAMPLE DATA CREATION")
    print("Creating sample data for testing...")
    
    if create_sample_data():
        print("Sample data creation completed!")
        return True
    else:
        print("Sample data creation failed!")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
