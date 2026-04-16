#!/usr/bin/env python3
"""
Data restoration script for education platform
Restores subjects, groups, tests, and sample questions
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import app
from app import db, User, Group, Subject, Topic, Test, Question
from datetime import datetime, date, timedelta

def restore_data():
    """Restore default data for the education platform"""
    
    print('=== RESTORING SUBJECTS, TESTS, GROUPS ===')
    
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
            
            # Create tests
            subjects = Subject.query.all()
            test_types = ['daily', 'weekly', 'monthly']
            
            for subject in subjects:
                for test_type in test_types:
                    # Create test for different dates
                    if test_type == 'daily':
                        test_date = date.today()
                        start_time = datetime.strptime('10:00', '%H:%M').time()
                        end_time = datetime.strptime('18:00', '%H:%M').time()
                    elif test_type == 'weekly':
                        test_date = date.today() + timedelta(days=7)
                        start_time = datetime.strptime('14:00', '%H:%M').time()
                        end_time = datetime.strptime('16:00', '%H:%M').time()
                    else:  # monthly
                        test_date = date.today() + timedelta(days=30)
                        start_time = datetime.strptime('09:00', '%H:%M').time()
                        end_time = datetime.strptime('12:00', '%H:%M').time()
                    
                    test = Test.query.filter_by(
                        subject_id=subject.id,
                        test_type=test_type,
                        test_date=test_date
                    ).first()
                    
                    if not test:
                        test = Test(
                            title=f'{subject.name} - {test_type.title()} test',
                            subject_id=subject.id,
                            test_type=test_type,
                            test_date=test_date,
                            start_time=start_time,
                            end_time=end_time,
                            duration_minutes=60
                        )
                        db.session.add(test)
            
            db.session.commit()
            print('Tests created successfully!')
            
            # Create sample questions for tests
            tests = Test.query.all()
            for test in tests:
                existing_questions = Question.query.filter_by(test_id=test.id).count()
                if existing_questions == 0:
                    questions_data = [
                        {
                            'question_text': f'{test.subject.name} fanidan 1-savol',
                            'option_a': 'A variant',
                            'option_b': 'B variant',
                            'option_c': 'C variant',
                            'option_d': 'D variant',
                            'correct_answer': 'A'
                        },
                        {
                            'question_text': f'{test.subject.name} fanidan 2-savol',
                            'option_a': 'A variant',
                            'option_b': 'B variant',
                            'option_c': 'C variant',
                            'option_d': 'D variant',
                            'correct_answer': 'B'
                        },
                        {
                            'question_text': f'{test.subject.name} fanidan 3-savol',
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
                            text=q_data['question_text'],
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
            
            print(f'\n=== FINAL STATUS ===')
            print(f'Subjects: {len(subjects)}')
            print(f'Groups: {len(groups)}')
            print(f'Tests: {len(tests)}')
            print(f'Questions: {len(questions)}')
            
            return True
            
        except Exception as e:
            print(f'Error: {e}')
            db.session.rollback()
            return False

if __name__ == '__main__':
    success = restore_data()
    if success:
        print('\n=== DATA RESTORATION COMPLETED SUCCESSFULLY! ===')
    else:
        print('\n=== DATA RESTORATION FAILED! ===')
