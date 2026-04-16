#!/usr/bin/env python3
"""
Clean state restoration script for education platform
Restores subjects, groups, and tests WITHOUT any students
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import app
from app import db, User, Group, Subject, Topic, Test, Question
from datetime import datetime, date, timedelta

def restore_clean_state():
    """Restore platform to clean state without students"""
    
    print('=== RESTORING TO CLEAN STATE (NO STUDENTS) ===')
    
    with app.app.app_context():
        try:
            # Ensure admin user exists
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(
                    username='admin',
                    password='admin123',  # This will be hashed automatically
                    first_name='Admin',
                    last_name='User',
                    is_admin=True,
                    is_group_leader=False
                )
                db.session.add(admin)
                print('Admin user created!')
            
            # Create default subjects
            subjects_data = [
                {'name': 'O\'zbekiston tarixi', 'description': 'O\'zbekiston mustaqilligi tarixi'},
                {'name': 'Huquqshunoslik asoslari', 'description': 'Huquqning asosiy tushunchalari'},
                {'name': 'Ingliz tili', 'description': 'Ingliz tili grammatikasi va so\'zboyligi'},
                {'name': 'Matematika', 'description': 'Matematikaning asosiy bo\'limlari'},
                {'name': 'Axborot texnologiyalari', 'description': 'Kompyuter texnologiyalari va dasturlash'}
            ]
            
            for subj_data in subjects_data:
                subject = Subject.query.filter_by(name=subj_data['name']).first()
                if not subject:
                    subject = Subject(name=subj_data['name'], description=subj_data['description'])
                    db.session.add(subject)
            
            db.session.commit()
            print('Subjects created successfully!')
            
            # Create 8 groups
            groups_data = [
                {'name': '101-guruh', 'total_score': 0},
                {'name': '102-guruh', 'total_score': 0},
                {'name': '103-guruh', 'total_score': 0},
                {'name': '104-guruh', 'total_score': 0},
                {'name': '105-guruh', 'total_score': 0},
                {'name': '106-guruh', 'total_score': 0},
                {'name': '107-guruh', 'total_score': 0},
                {'name': '108-guruh', 'total_score': 0}
            ]
            
            for group_data in groups_data:
                group = Group.query.filter_by(name=group_data['name']).first()
                if not group:
                    group = Group(name=group_data['name'], total_score=group_data['total_score'])
                    db.session.add(group)
            
            db.session.commit()
            print('8 groups created successfully!')
            
            # Create 7-day test schedule
            subjects = Subject.query.all()
            today = date.today()
            
            # Create tests for 7 days
            for day_offset in range(7):
                test_date = today + timedelta(days=day_offset)
                
                # Every 3 days create 90-question tests
                if day_offset % 3 == 0:
                    # Create 90-question tests for all subjects
                    for subject in subjects:
                        test = Test.query.filter_by(
                            subject_id=subject.id,
                            test_type='comprehensive',
                            test_date=test_date
                        ).first()
                        
                        if not test:
                            test = Test(
                                title=f'{subject.name} - 90 savol test',
                                subject_id=subject.id,
                                test_type='comprehensive',
                                test_date=test_date,
                                start_time=datetime.strptime('09:00', '%H:%M').time(),
                                end_time=datetime.strptime('12:00', '%H:%M').time(),
                                duration_minutes=180  # 3 hours for 90 questions
                            )
                            db.session.add(test)
                else:
                    # Regular daily tests
                    for subject in subjects:
                        test = Test.query.filter_by(
                            subject_id=subject.id,
                            test_type='daily',
                            test_date=test_date
                        ).first()
                        
                        if not test:
                            test = Test(
                                title=f'{subject.name} - Kunlik test',
                                subject_id=subject.id,
                                test_type='daily',
                                test_date=test_date,
                                start_time=datetime.strptime('10:00', '%H:%M').time(),
                                end_time=datetime.strptime('18:00', '%H:%M').time(),
                                duration_minutes=60
                            )
                            db.session.add(test)
            
            db.session.commit()
            print('7-day test schedule created successfully!')
            
            # Create DTM tests (every Sunday)
            # Find next Sunday
            days_until_sunday = (6 - today.weekday()) % 7
            next_sunday = today + timedelta(days=days_until_sunday)
            
            dtm_subjects = ['O\'zbekiston tarixi', 'Huquqshunoslik asoslari']
            for subject_name in dtm_subjects:
                subject = Subject.query.filter_by(name=subject_name).first()
                if subject:
                    dtm_test = Test.query.filter_by(
                        subject_id=subject.id,
                        test_type='dtm',
                        test_date=next_sunday
                    ).first()
                    
                    if not dtm_test:
                        dtm_test = Test(
                            title=f'DTM test - {subject.name}',
                            subject_id=subject.id,
                            test_type='dtm',
                            test_date=next_sunday,
                            start_time=datetime.strptime('14:00', '%H:%M').time(),
                            end_time=datetime.strptime('16:00', '%H:%M').time(),
                            duration_minutes=120
                        )
                        db.session.add(dtm_test)
            
            db.session.commit()
            print('DTM tests created successfully!')
            
            # Create questions for all tests
            tests = Test.query.all()
            for test in tests:
                existing_questions = Question.query.filter_by(test_id=test.id).count()
                if existing_questions == 0:
                    if test.test_type == 'comprehensive':
                        # 90 questions for comprehensive tests
                        questions_data = []
                        for i in range(90):
                            questions_data.append({
                                'text': f'{test.subject.name} fanidan {i+1}-savol',
                                'option_a': 'A variant',
                                'option_b': 'B variant',
                                'option_c': 'C variant',
                                'option_d': 'D variant',
                                'correct_answer': chr(65 + (i % 4))  # A, B, C, D rotation
                            })
                    elif test.test_type == 'dtm':
                        # 30 questions for DTM tests
                        questions_data = []
                        for i in range(30):
                            questions_data.append({
                                'text': f'DTM: {test.subject.name} fanidan {i+1}-savol',
                                'option_a': 'A variant',
                                'option_b': 'B variant',
                                'option_c': 'C variant',
                                'option_d': 'D variant',
                                'correct_answer': chr(65 + (i % 4))
                            })
                    else:  # daily tests
                        # 15 questions for daily tests
                        questions_data = []
                        for i in range(15):
                            questions_data.append({
                                'text': f'{test.subject.name} fanidan kunlik {i+1}-savol',
                                'option_a': 'A variant',
                                'option_b': 'B variant',
                                'option_c': 'C variant',
                                'option_d': 'D variant',
                                'correct_answer': chr(65 + (i % 4))
                            })
                    
                    for q_data in questions_data:
                        question = Question(
                            test_id=test.id,
                            text=q_data['text'],
                            option_a=q_data['option_a'],
                            option_b=q_data['option_b'],
                            option_c=q_data['option_c'],
                            option_d=q_data['option_d'],
                            correct_answer=q_data['correct_answer']
                        )
                        db.session.add(question)
            
            db.session.commit()
            print('Questions created successfully!')
            
            # Clear any remaining students (double-check)
            remaining_students = User.query.filter(User.username != 'admin').all()
            if remaining_students:
                print(f'Warning: Found {len(remaining_students)} remaining students, deleting them...')
                User.query.filter(User.username != 'admin').delete()
                db.session.commit()
            
            # Show final status
            subjects = Subject.query.all()
            groups = Group.query.all()
            tests = Test.query.all()
            questions = Question.query.all()
            daily_tests = Test.query.filter_by(test_type='daily').all()
            comprehensive_tests = Test.query.filter_by(test_type='comprehensive').all()
            dtm_tests = Test.query.filter_by(test_type='dtm').all()
            admin = User.query.filter_by(username='admin').first()
            students = User.query.filter(User.username != 'admin').all()
            
            print(f'Admin user: {admin.username if admin else "None"}')
            print(f'Students: {len(students)} (SHOULD BE 0)')
            print(f'Subjects: {len(subjects)}')
            print(f'Groups: {len(groups)}')
            print(f'Tests: {len(tests)}')
            print(f'  - Daily tests: {len(daily_tests)}')
            print(f'  - 90-question tests: {len(comprehensive_tests)}')
            print(f'  - DTM tests: {len(dtm_tests)}')
            print(f'Questions: {len(questions)}')
            
            return True
            
        except Exception as e:
            print(f'Error: {e}')
            db.session.rollback()
            return False

if __name__ == '__main__':
    success = restore_clean_state()
    if success:
        print('\n=== CLEAN STATE RESTORED SUCCESSFULLY! ===')
        print('NO STUDENTS WILL BE CREATED ON RESTART!')
    else:
        print('\n=== CLEAN STATE RESTORATION FAILED! ===')
