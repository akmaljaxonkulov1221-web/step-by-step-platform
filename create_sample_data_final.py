#!/usr/bin/env python3
"""
Create Final Sample Data
Create comprehensive sample data for all enhanced features
"""

import os
import sys
import random
from datetime import datetime, timedelta

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_comprehensive_sample_data():
    """Create comprehensive sample data for testing"""
    print("=== CREATING COMPREHENSIVE SAMPLE DATA ===")
    
    try:
        import app
        
        with app.app.app_context():
            # 1. Enhanced Topics with YouTube, PDF, descriptions
            print("\n1. Creating Enhanced Topics")
            subjects = app.Subject.query.all()
            if not subjects:
                print("   No subjects found, creating sample subjects...")
                sample_subjects = [
                    app.Subject(name="Ingliz tili", description="Ingliz tili kursi"),
                    app.Subject(name="Matematika", description="Matematika kursi"),
                    app.Subject(name="Fizika", description="Fizika kursi")
                ]
                for subject in sample_subjects:
                    app.db.session.add(subject)
                app.db.session.flush()
                subjects = sample_subjects
            
            sample_topics = [
                {
                    'name': 'Ingliz tili grammatikasi - Present Tense',
                    'title': 'Present Tense Grammatikasi',
                    'subject_id': subjects[0].id,
                    'youtube_link': 'https://www.youtube.com/watch?v=dX3nQXkXGao',
                    'pdf_file': 'present_tense_grammar.pdf',
                    'description': 'Present tense vaqtidagi grammatik qoidalarini o\'rganing. Bu mavzuda oddiy vaqt, davomiy vaqt, mukammal vaqt shakllari ko\'rib chiqiladi.'
                },
                {
                    'name': 'Ingliz tili - So\'zboylash',
                    'title': 'Ingliz tili So\'zboylash',
                    'subject_id': subjects[0].id,
                    'youtube_link': 'https://www.youtube.com/watch?v=1kNQbHsS4ZE',
                    'pdf_file': 'vocabulary_builder.pdf',
                    'description': 'Ingliz tilida so\'zboylash usullari va yangi so\'zlarni esda saqlash texnikalari. Har kuni 5 ta yangi so\'z o\'rganing!'
                },
                {
                    'name': 'Matematika - Kvadrat tenglamalar',
                    'title': 'Kvadrat Tenglamalar',
                    'subject_id': subjects[1].id,
                    'youtube_link': 'https://www.youtube.com/watch?v=U0Yg--eJZ-U',
                    'pdf_file': 'quadratic_equations.pdf',
                    'description': 'Kvadrat tenglamalarni yechish usullari: diskriminant usuli, faktorizatsiya usuli, kvadrat ildiz formulasi.'
                },
                {
                    'name': 'Fizika - Newton qonunlari',
                    'title': 'Newtonning Harakat Qonunlari',
                    'subject_id': subjects[2].id,
                    'youtube_link': 'https://www.youtube.com/watch?v=KKMW5M-7fYY',
                    'pdf_file': 'newton_laws.pdf',
                    'description': 'Newtonning uchta harakat qonuni: birinchi qonun (inertsiya), ikkinchi qonun (F=ma), uchinchi qonun (harakat va reaktsiya).'
                }
            ]
            
            for topic_data in sample_topics:
                existing_topic = app.Topic.query.filter_by(name=topic_data['name']).first()
                if not existing_topic:
                    topic = app.Topic(**topic_data)
                    app.db.session.add(topic)
                    print(f"   Created topic: {topic_data['name']}")
                else:
                    print(f"   Topic already exists: {topic_data['name']}")
            
            # 2. AI Chat conversations
            print("\n2. Creating AI Chat Conversations")
            users = app.User.query.filter_by(is_admin=False).all()
            topics = app.Topic.query.all()
            
            if users and topics:
                sample_conversations = [
                    {
                        'user_id': users[0].id,
                        'question': 'Ingliz tili grammatikasida Present Tense qanday ishlatiladi?',
                        'answer': 'Present Tense - bu hozirgi vaqtni ifodalovchi vaqt. U oddiy harakatlarni (I work - Men ishlayman), muntazam harakatlarni (He plays - U o\'ynaydi) va umumiy haqiqatlarni (Water boils - Suv qaynaydi) ifodalaydi. Present Continuous esa hozirgi vaqtda davom etayotgan harakatlarni ifodalaydi (I am working - Men hozir ishlamoqdaman).',
                        'topic_id': topics[0].id if topics else None,
                        'test_generated': False
                    },
                    {
                        'user_id': users[0].id,
                        'question': 'Kvadrat tenglamani qanday yechish mumkin?',
                        'answer': 'Kvadrat tenglamani yechishning bir necha usuli bor: 1) Diskriminant usuli: D = b²-4ac formuladan foydalanib, x = (-b ± sqrt(D))/2a. 2) Faktorizatsiya usuli: Tenglama ko\'paytuvchilarga ajratiladi. 3) To\'la kvadrat usuli: (x + b/2a)² = (b²-4ac)/4a². Diskriminant usuli eng umumiy va ishonatli usul hisoblanadi.',
                        'topic_id': topics[2].id if len(topics) > 2 else None,
                        'test_generated': True
                    },
                    {
                        'user_id': users[1].id if len(users) > 1 else users[0].id,
                        'question': 'Ingliz tilida so\'zboylashning eng samarali usuli nima?',
                        'answer': 'Eng samarali so\'zboylash usullari: 1) Spaced repetition - so\'zlarni muntazam takrorlash (Anki, Quizlet kabi dasturlardan foydalaning). 2) Context learning - so\'zlarni gaplar ichida o\'rganing. 3) Active recall - eslab turishga harakat qiling. 4) Multiple exposure - so\'zni turli shakllarda ko\'ring (eshitib, o\'qib, yozib).',
                        'topic_id': topics[1].id if topics else None,
                        'test_generated': False
                    }
                ]
                
                for conv_data in sample_conversations:
                    existing_chat = app.AIChat.query.filter_by(
                        user_id=conv_data['user_id'],
                        question=conv_data['question']
                    ).first()
                    
                    if not existing_chat:
                        chat = app.AIChat(**conv_data)
                        app.db.session.add(chat)
                        print(f"   Created AI chat: {conv_data['question'][:50]}...")
                else:
                    print(f"   AI chat already exists: {conv_data['question'][:50]}...")
            
            # 3. Enhanced Tests with 20 questions each
            print("\n3. Creating Enhanced Tests (20 questions)")
            if topics:
                sample_tests = [
                    {
                        'title': 'Ingliz tili Present Tense Testi',
                        'subject_id': topics[0].subject_id,
                        'test_type': 'ai_generated',
                        'test_date': datetime.now().date(),
                        'topic_id': topics[0].id
                    },
                    {
                        'title': 'Matematika Kvadrat Tenglamalar Testi',
                        'subject_id': topics[2].subject_id if len(topics) > 2 else topics[0].subject_id,
                        'test_type': 'ai_generated',
                        'test_date': datetime.now().date(),
                        'topic_id': topics[2].id if len(topics) > 2 else topics[0].id
                    }
                ]
                
                for test_data in sample_tests:
                    # Check if test already exists
                    existing_test = app.Test.query.filter_by(title=test_data['title']).first()
                    if not existing_test:
                        test = app.Test(
                            title=test_data['title'],
                            subject_id=test_data['subject_id'],
                            test_type=test_data['test_type'],
                            test_date=test_data['test_date']
                        )
                        app.db.session.add(test)
                        app.db.session.flush()
                        
                        # Create 20 questions for each test
                        for i in range(1, 21):
                            question_text = f"{test.title} - {i}-savol"
                            
                            # Generate 4 options with one correct answer
                            correct_answer = random.choice(['A', 'B', 'C', 'D'])
                            options = {
                                'A': f"Variant A - {test.title} bo'yicha {i}-javob varianti",
                                'B': f"Variant B - {test.title} bo'yicha {i}-javob varianti",
                                'C': f"Variant C - {test.title} bo'yicha {i}-javob varianti",
                                'D': f"Variant D - {test.title} bo'yicha {i}-javob varianti"
                            }
                            
                            question = app.Question(
                                test_id=test.id,
                                question=question_text,
                                option_a=options['A'],
                                option_b=options['B'],
                                option_c=options['C'],
                                option_d=options['D'],
                                correct_answer=correct_answer
                            )
                            app.db.session.add(question)
                        
                        print(f"   Created test: {test_data['title']} (20 questions)")
                    else:
                        print(f"   Test already exists: {test_data['title']}")
            
            # 4. Enhanced Test Results
            print("\n4. Creating Enhanced Test Results")
            students = app.User.query.filter_by(is_admin=False, is_group_leader=False).all()
            tests = app.Test.query.filter_by(test_type='ai_generated').all()
            
            if students and tests:
                for student in students[:2]:  # Create results for first 2 students
                    for test in tests[:1]:  # Create results for first test
                        existing_result = app.TestResult.query.filter_by(
                            user_id=student.id,
                            test_id=test.id
                        ).first()
                        
                        if not existing_result:
                            score = random.randint(12, 20)  # Random score between 12-20
                            percentage = (score / 20) * 100
                            
                            # Generate correct and incorrect answers
                            all_answers = list(range(1, 21))
                            correct_answers = random.sample(all_answers, score)
                            incorrect_answers = [a for a in all_answers if a not in correct_answers]
                            
                            result = app.TestResult(
                                user_id=student.id,
                                test_id=test.id,
                                score=score,
                                total_questions=20,
                                percentage=percentage,
                                correct_answers=','.join(map(str, correct_answers)),
                                incorrect_answers=','.join(map(str, incorrect_answers)),
                                total_time=random.randint(600, 1800),  # 10-30 minutes
                                taken_at=datetime.now() - timedelta(days=random.randint(1, 7))
                            )
                            app.db.session.add(result)
                            print(f"   Created test result: {student.first_name} - {score}/20")
                        else:
                            print(f"   Test result already exists: {student.first_name}")
            
            # 5. Enhanced Certificates
            print("\n5. Creating Enhanced Certificates")
            if students:
                sample_certificates = [
                    {
                        'title': 'Ingliz tili B1 Level',
                        'description': 'Ingliz tili bo\'yicha B1 darajasi sertifikati',
                        'level': 'B1',
                        'subject_level': 'B1',
                        'certificate_type': 'achievement',
                        'points': 50,
                        'user_id': students[0].id
                    },
                    {
                        'title': 'Matematika Asoslari',
                        'description': 'Matematika asosiy kursini tugatgani uchun',
                        'level': 'Basic',
                        'subject_level': 'Basic',
                        'certificate_type': 'completion',
                        'points': 30,
                        'user_id': students[1].id if len(students) > 1 else students[0].id
                    }
                ]
                
                for cert_data in sample_certificates:
                    existing_cert = app.Certificate.query.filter_by(
                        user_id=cert_data['user_id'],
                        title=cert_data['title']
                    ).first()
                    
                    if not existing_cert:
                        cert = app.Certificate(**cert_data)
                        app.db.session.add(cert)
                        print(f"   Created certificate: {cert_data['title']}")
                    else:
                        print(f"   Certificate already exists: {cert_data['title']}")
            
            app.db.session.commit()
            
            # Display created data summary
            print("\n=== SAMPLE DATA SUMMARY ===")
            print(f"Topics: {app.Topic.query.count()}")
            print(f"AI Chats: {app.AIChat.query.count()}")
            print(f"Tests: {app.Test.query.count()}")
            print(f"Questions: {app.Question.query.count()}")
            print(f"Test Results: {app.TestResult.query.count()}")
            print(f"Certificates: {app.Certificate.query.count()}")
            
            return True
            
    except Exception as e:
        print(f"Error creating sample data: {e}")
        return False

def main():
    """Main function"""
    print("STEP BY STEP EDUCATION PLATFORM - SAMPLE DATA CREATION")
    print("Creating comprehensive sample data for all enhanced features...")
    
    if create_comprehensive_sample_data():
        print("\n=== SAMPLE DATA CREATION COMPLETE ===")
        print("All sample data created successfully!")
        print("System is now ready for testing with realistic data!")
        return True
    else:
        print("\nSample data creation failed!")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
