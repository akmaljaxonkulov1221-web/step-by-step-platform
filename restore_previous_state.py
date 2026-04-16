#!/usr/bin/env python3
"""
Restore platform to previous state with daily and DTM tests
Includes subjects, groups, daily tests, and DTM tests
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import app
from app import db, User, Group, Subject, Topic, Test, Question
from datetime import datetime, date, timedelta

def restore_previous_state():
    """Restore platform to previous state with daily and DTM tests"""
    
    print('=== RESTORING TO PREVIOUS STATE ===')
    
    with app.app.app_context():
        try:
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
            
            # Create groups
            groups_data = [
                {'name': '101-guruh', 'total_score': 0},
                {'name': '102-guruh', 'total_score': 0},
                {'name': '103-guruh', 'total_score': 0},
                {'name': '104-guruh', 'total_score': 0}
            ]
            
            for group_data in groups_data:
                group = Group.query.filter_by(name=group_data['name']).first()
                if not group:
                    group = Group(name=group_data['name'], total_score=group_data['total_score'])
                    db.session.add(group)
            
            db.session.commit()
            print('Groups created successfully!')
            
            # Create daily tests (kunlik testlar)
            subjects = Subject.query.all()
            today = date.today()
            
            for subject in subjects:
                # Daily test for today
                daily_test = Test.query.filter_by(
                    subject_id=subject.id,
                    test_type='daily',
                    test_date=today
                ).first()
                
                if not daily_test:
                    daily_test = Test(
                        title=f'{subject.name} - Kunlik test',
                        subject_id=subject.id,
                        test_type='daily',
                        test_date=today,
                        start_time=datetime.strptime('10:00', '%H:%M').time(),
                        end_time=datetime.strptime('18:00', '%H:%M').time(),
                        duration_minutes=60
                    )
                    db.session.add(daily_test)
            
            db.session.commit()
            print('Daily tests created successfully!')
            
            # Create DTM tests (DTM testlar)
            dtm_subjects = ['O\'zbekiston tarixi', 'Huquqshunoslik asoslari']
            dtm_date = today + timedelta(days=7)  # Next week
            
            for subject_name in dtm_subjects:
                subject = Subject.query.filter_by(name=subject_name).first()
                if subject:
                    dtm_test = Test.query.filter_by(
                        subject_id=subject.id,
                        test_type='dtm',
                        test_date=dtm_date
                    ).first()
                    
                    if not dtm_test:
                        dtm_test = Test(
                            title=f'DTM test - {subject.name}',
                            subject_id=subject.id,
                            test_type='dtm',
                            test_date=dtm_date,
                            start_time=datetime.strptime('14:00', '%H:%M').time(),
                            end_time=datetime.strptime('16:00', '%H:%M').time(),
                            duration_minutes=120
                        )
                        db.session.add(dtm_test)
            
            db.session.commit()
            print('DTM tests created successfully!')
            
            # Create sample questions for all tests
            tests = Test.query.all()
            for test in tests:
                existing_questions = Question.query.filter_by(test_id=test.id).count()
                if existing_questions == 0:
                    # Different questions for different test types
                    if test.test_type == 'daily':
                        questions_data = [
                            {
                                'text': f'{test.subject.name} fanidan kunlik 1-savol',
                                'option_a': 'A variant',
                                'option_b': 'B variant',
                                'option_c': 'C variant',
                                'option_d': 'D variant',
                                'correct_answer': 'A'
                            },
                            {
                                'text': f'{test.subject.name} fanidan kunlik 2-savol',
                                'option_a': 'A variant',
                                'option_b': 'B variant',
                                'option_c': 'C variant',
                                'option_d': 'D variant',
                                'correct_answer': 'B'
                            },
                            {
                                'text': f'{test.subject.name} fanidan kunlik 3-savol',
                                'option_a': 'A variant',
                                'option_b': 'B variant',
                                'option_c': 'C variant',
                                'option_d': 'D variant',
                                'correct_answer': 'C'
                            }
                        ]
                    else:  # DTM test
                        questions_data = [
                            {
                                'text': f'DTM: {test.subject.name} fanidan 1-savol',
                                'option_a': 'A variant',
                                'option_b': 'B variant',
                                'option_c': 'C variant',
                                'option_d': 'D variant',
                                'correct_answer': 'A'
                            },
                            {
                                'text': f'DTM: {test.subject.name} fanidan 2-savol',
                                'option_a': 'A variant',
                                'option_b': 'B variant',
                                'option_c': 'C variant',
                                'option_d': 'D variant',
                                'correct_answer': 'B'
                            },
                            {
                                'text': f'DTM: {test.subject.name} fanidan 3-savol',
                                'option_a': 'A variant',
                                'option_b': 'B variant',
                                'option_c': 'C variant',
                                'option_d': 'D variant',
                                'correct_answer': 'C'
                            }
                        ]
                    
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
            
            # Show final status
            subjects = Subject.query.all()
            groups = Group.query.all()
            tests = Test.query.all()
            questions = Question.query.all()
            daily_tests = Test.query.filter_by(test_type='daily').all()
            dtm_tests = Test.query.filter_by(test_type='dtm').all()
            
            print(f'\n=== FINAL STATUS ===')
            print(f'Subjects: {len(subjects)}')
            print(f'Groups: {len(groups)}')
            print(f'Tests: {len(tests)}')
            print(f'  - Daily tests: {len(daily_tests)}')
            print(f'  - DTM tests: {len(dtm_tests)}')
            print(f'Questions: {len(questions)}')
            
            print(f'\n=== DAILY TESTS ===')
            for test in daily_tests:
                print(f'- {test.title} ({test.test_date})')
            
            print(f'\n=== DTM TESTS ===')
            for test in dtm_tests:
                print(f'- {test.title} ({test.test_date})')
            
            return True
            
        except Exception as e:
            print(f'Error: {e}')
            db.session.rollback()
            return False

if __name__ == '__main__':
    success = restore_previous_state()
    if success:
        print('\n=== PREVIOUS STATE RESTORED SUCCESSFULLY! ===')
    else:
        print('\n=== PREVIOUS STATE RESTORATION FAILED! ===')
