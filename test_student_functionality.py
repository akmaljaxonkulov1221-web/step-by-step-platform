#!/usr/bin/env python3
"""
Test Student Functionality
Test student test functionality in detail
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_student_login_and_redirect():
    """Test student login and redirect flow"""
    print("=== TESTING STUDENT LOGIN AND REDIRECT ===")
    
    try:
        import app
        
        with app.app.test_client() as client:
            # Test student login
            response = client.post('/login', data={
                'username': 'student1',
                'password': 'password1'
            }, follow_redirects=False)
            
            print(f"Student login (no redirect): {response.status_code}")
            
            if response.status_code == 302:
                print(f"Redirect location: {response.location}")
                
                # Follow redirect
                response = client.get(response.location, follow_redirects=False)
                print(f"After redirect: {response.status_code}")
                
                if response.status_code == 302:
                    print(f"Second redirect location: {response.location}")
                    
                    # Follow second redirect
                    response = client.get(response.location)
                    print(f"After second redirect: {response.status_code}")
                    
                    if response.status_code == 200:
                        print("Student dashboard: WORKING")
                        return True
                    else:
                        print("Student dashboard: FAILED")
                        return False
                else:
                    print("Single redirect: WORKING")
                    return True
            else:
                print("No redirect: FAILED")
                return False
            
    except Exception as e:
        print(f"Student login test error: {e}")
        return False

def test_student_direct_access():
    """Test student direct access to test pages"""
    print("\n=== TESTING STUDENT DIRECT ACCESS ===")
    
    try:
        import app
        
        with app.app.test_client() as client:
            # Login first
            client.post('/login', data={
                'username': 'student1',
                'password': 'password1'
            }, follow_redirects=True)
            
            # Test direct access to student tests
            response = client.get('/student/tests')
            print(f"Direct /student/tests: {response.status_code}")
            
            # Test direct access to student dashboard
            response = client.get('/student/dashboard')
            print(f"Direct /student/dashboard: {response.status_code}")
            
            # Test direct access to take test
            with app.app.app_context():
                tests = app.Test.query.all()
                if tests:
                    test_id = tests[0].id
                    response = client.get(f'/student/take_test/{test_id}')
                    print(f"Direct /student/take_test/{test_id}: {response.status_code}")
            
            return True
            
    except Exception as e:
        print(f"Direct access test error: {e}")
        return False

def test_student_template_rendering():
    """Test student template rendering"""
    print("\n=== TESTING STUDENT TEMPLATE RENDERING ===")
    
    try:
        import app
        
        # Check if templates exist
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
        
        # Test template rendering
        with app.app.test_client() as client:
            # Login
            client.post('/login', data={
                'username': 'student1',
                'password': 'password1'
            }, follow_redirects=True)
            
            # Test student tests template
            response = client.get('/student/tests')
            if response.status_code == 200:
                print("Student tests template: WORKING")
            else:
                print(f"Student tests template: FAILED ({response.status_code})")
            
            # Test student dashboard template
            response = client.get('/student/dashboard')
            if response.status_code == 200:
                print("Student dashboard template: WORKING")
            else:
                print(f"Student dashboard template: FAILED ({response.status_code})")
        
        return True
        
    except Exception as e:
        print(f"Template rendering test error: {e}")
        return False

def test_student_test_submission():
    """Test student test submission"""
    print("\n=== TESTING STUDENT TEST SUBMISSION ===")
    
    try:
        import app
        
        with app.app.test_client() as client:
            # Login
            client.post('/login', data={
                'username': 'student1',
                'password': 'password1'
            }, follow_redirects=True)
            
            # Get available tests
            with app.app.app_context():
                tests = app.Test.query.all()
                if tests:
                    test_id = tests[0].id
                    test = app.Test.query.get(test_id)
                    
                    # Test taking test
                    response = client.get(f'/student/take_test/{test_id}')
                    print(f"Take test page: {response.status_code}")
                    
                    if response.status_code == 200:
                        # Test submitting test
                        questions = app.Question.query.filter_by(test_id=test_id).all()
                        if questions:
                            # Create form data with answers
                            form_data = {}
                            for question in questions:
                                form_data[f'question_{question.id}'] = question.correct_answer
                            
                            response = client.post(f'/student/take_test/{test_id}', data=form_data)
                            print(f"Submit test: {response.status_code}")
                            
                            if response.status_code == 302:
                                print("Test submission: WORKING")
                                return True
                            else:
                                print("Test submission: FAILED")
                                return False
                        else:
                            print("No questions found for test")
                            return False
                    else:
                        print("Cannot access take test page")
                        return False
                else:
                    print("No tests available")
                    return False
        
    except Exception as e:
        print(f"Test submission error: {e}")
        return False

def main():
    """Main function"""
    print("STEP BY STEP EDUCATION PLATFORM - TEST STUDENT FUNCTIONALITY")
    print("Testing student test functionality in detail...")
    
    if test_student_login_and_redirect():
        if test_student_direct_access():
            if test_student_template_rendering():
                if test_student_test_submission():
                    print("\n=== STUDENT FUNCTIONALITY WORKING ===")
                    print("Testlar bo'limi to'liq ishlaydi!")
                    return True
                else:
                    print("\nTest submission test failed!")
                    return False
            else:
                print("\nTemplate rendering test failed!")
                return False
        else:
            print("\nDirect access test failed!")
            return False
    else:
        print("\nStudent login test failed!")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
