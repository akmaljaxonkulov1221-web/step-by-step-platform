#!/usr/bin/env python3
"""
Test Submission
Test student test submission functionality
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_student_test_submission():
    """Test student test submission"""
    print("=== TESTING STUDENT TEST SUBMISSION ===")
    
    try:
        import app
        
        with app.app.app_context():
            # Get available tests
            tests = app.Test.query.all()
            if tests:
                test_id = tests[0].id
                test = app.Test.query.get(test_id)
                print(f"Test ID: {test_id}")
                print(f"Test title: {test.title}")
                
                # Get questions for this test
                questions = app.Question.query.filter_by(test_id=test_id).limit(3).all()
                print(f"Questions found: {len(questions)}")
                
                if questions:
                    # Create test client
                    with app.app.test_client() as client:
                        # Login
                        response = client.post('/login', data={
                            'username': 'student1',
                            'password': 'password1'
                        }, follow_redirects=True)
                        
                        print(f"Login: {response.status_code}")
                        
                        # Test taking test page
                        response = client.get(f'/student/take_test/{test_id}')
                        print(f"Take test page: {response.status_code}")
                        
                        if response.status_code == 200:
                            # Create form data with answers
                            form_data = {}
                            for question in questions:
                                form_data[f'question_{question.id}'] = question.correct_answer
                                print(f"Question {question.id}: {question.correct_answer}")
                            
                            # Submit test
                            response = client.post(f'/student/take_test/{test_id}', data=form_data)
                            print(f"Submit test: {response.status_code}")
                            
                            if response.status_code == 302:
                                print(f"Redirect location: {response.location}")
                                
                                # Follow redirect to see result
                                response = client.get(response.location)
                                print(f"Result page: {response.status_code}")
                                
                                if response.status_code == 200:
                                    print("Test submission: WORKING")
                                    
                                    # Check if result was created
                                    user_id = 7  # student1's ID
                                    result = app.TestResult.query.filter_by(
                                        user_id=user_id, 
                                        test_id=test_id
                                    ).first()
                                    
                                    if result:
                                        print(f"Result created: YES")
                                        print(f"Score: {result.score}/{result.total_questions}")
                                        print(f"Percentage: {result.percentage:.1f}%")
                                        print(f"Points earned: {result.points_earned}")
                                        return True
                                    else:
                                        print("Result created: NO")
                                        return False
                                else:
                                    print("Result page: FAILED")
                                    return False
                            else:
                                print("Test submission: FAILED")
                                return False
                        else:
                            print("Cannot access take test page")
                            return False
                else:
                    print("No questions found for test")
                    return False
            else:
                print("No tests available")
                return False
            
    except Exception as e:
        print(f"Test submission error: {e}")
        return False

def main():
    """Main function"""
    print("STEP BY STEP EDUCATION PLATFORM - TEST SUBMISSION")
    print("Testing student test submission...")
    
    if test_student_test_submission():
        print("\n=== TEST SUBMISSION WORKING ===")
        print("Testlar bo'limi to'liq ishlaydi!")
        return True
    else:
        print("\nTest submission failed!")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
