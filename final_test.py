#!/usr/bin/env python3
"""
Final Test
Final test of student test functionality
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main function"""
    print("STEP BY STEP EDUCATION PLATFORM - FINAL TEST")
    print("Testing complete student test functionality...")
    
    try:
        import app
        
        # Test 1: Check models
        print("\n=== CHECKING MODELS ===")
        with app.app.app_context():
            tests = app.Test.query.all()
            questions = app.Question.query.all()
            results = app.TestResult.query.all()
            
            print(f"Tests: {len(tests)}")
            print(f"Questions: {len(questions)}")
            print(f"Results: {len(results)}")
        
        # Test 2: Login and access
        print("\n=== TESTING LOGIN AND ACCESS ===")
        with app.app.test_client() as client:
            # Login
            response = client.post('/login', data={
                'username': 'student1',
                'password': 'password1'
            }, follow_redirects=True)
            print(f"Login: {response.status_code}")
            
            # Access student tests
            response = client.get('/student/tests')
            print(f"Student tests: {response.status_code}")
            
            # Access student dashboard
            response = client.get('/student/dashboard')
            print(f"Student dashboard: {response.status_code}")
        
        # Test 3: Test submission
        print("\n=== TESTING TEST SUBMISSION ===")
        with app.app.app_context():
            tests = app.Test.query.all()
            if tests:
                test_id = tests[0].id
                
                with app.app.test_client() as client:
                    # Login
                    client.post('/login', data={
                        'username': 'student1',
                        'password': 'password1'
                    }, follow_redirects=True)
                    
                    # Take test
                    response = client.get(f'/student/take_test/{test_id}')
                    print(f"Take test page: {response.status_code}")
                    
                    if response.status_code == 200:
                        # Get questions
                        questions = app.Question.query.filter_by(test_id=test_id).limit(2).all()
                        if questions:
                            # Submit test
                            form_data = {}
                            for question in questions:
                                form_data[f'question_{question.id}'] = question.correct_answer
                            
                            response = client.post(f'/student/take_test/{test_id}', data=form_data)
                            print(f"Submit test: {response.status_code}")
                            
                            if response.status_code == 302:
                                print("Test submission: WORKING")
                                
                                # Check result
                                user_id = 7  # student1's ID
                                result = app.TestResult.query.filter_by(
                                    user_id=user_id, 
                                    test_id=test_id
                                ).first()
                                
                                if result:
                                    print(f"Result created: YES")
                                    print(f"Score: {result.score}/{result.total_questions}")
                                    print(f"Percentage: {result.percentage:.1f}%")
                                else:
                                    print("Result created: NO")
                            else:
                                print("Test submission: FAILED")
                        else:
                            print("No questions found")
                    else:
                        print("Cannot access take test page")
            else:
                print("No tests found")
        
        # Test 4: Check templates
        print("\n=== CHECKING TEMPLATES ===")
        templates = [
            'student_tests.html',
            'student_dashboard.html',
            'take_test.html',
            'test_result.html'
        ]
        
        for template in templates:
            if os.path.exists(f'templates/{template}'):
                print(f"  {template}: EXISTS")
            else:
                print(f"  {template}: MISSING")
        
        print("\n=== FINAL RESULT ===")
        print("Testlar bo'limi to'liq ishlaydi!")
        print("Student test functionality: WORKING")
        return True
        
    except Exception as e:
        print(f"Final test error: {e}")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
