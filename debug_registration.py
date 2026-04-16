#!/usr/bin/env python3
"""
Debug Registration Issues
Detailed debugging of registration functionality
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_registration_form_details():
    """Test registration form with detailed debugging"""
    print("=== DEBUGGING REGISTRATION FORM ===")
    
    try:
        import app
        
        with app.app.test_client() as client:
            # Test GET request with details
            print("Testing GET /register...")
            response = client.get('/register')
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                content = response.data.decode('utf-8')
                
                # Check form elements
                form_elements = {
                    'first_name': 'name="first_name"' in content,
                    'last_name': 'name="last_name"' in content,
                    'group_id': 'name="group_id"' in content,
                    'password': 'name="password"' in content,
                    'confirm_password': 'name="confirm_password"' in content,
                    'form_tag': '<form method="POST"' in content,
                    'submit_button': 'type="submit"' in content
                }
                
                print("Form elements check:")
                for element, exists in form_elements.items():
                    status = "OK" if exists else "MISSING"
                    print(f"  {element}: {status}")
                
                # Check groups display
                groups_count = content.count('<tr>')
                print(f"Groups table rows: {groups_count}")
                
                # Check error display
                error_display = '{% if error %}' in content
                print(f"Error display template: {'OK' if error_display else 'MISSING'}")
                
                return all(form_elements.values())
            else:
                print(f"GET request failed: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"Form test error: {e}")
        return False

def test_registration_post_scenarios():
    """Test various POST scenarios"""
    print("\n=== TESTING POST SCENARIOS ===")
    
    try:
        import app
        
        with app.app.test_client() as client:
            # Get groups for testing
            groups = app.Group.query.filter(
                app.Group.name.in_(['101', '102', '103', '104', '105', '106', '107', '108'])
            ).all()
            
            if not groups:
                print("No groups available for testing")
                return False
            
            test_group = groups[0]
            
            # Test scenarios
            scenarios = [
                {
                    'name': 'Empty form',
                    'data': {},
                    'expected_status': 200,
                    'should_have_error': True
                },
                {
                    'name': 'Missing first name',
                    'data': {
                        'last_name': 'Test',
                        'group_id': str(test_group.id),
                        'password': 'test123',
                        'confirm_password': 'test123'
                    },
                    'expected_status': 200,
                    'should_have_error': True
                },
                {
                    'name': 'Missing last name',
                    'data': {
                        'first_name': 'Test',
                        'group_id': str(test_group.id),
                        'password': 'test123',
                        'confirm_password': 'test123'
                    },
                    'expected_status': 200,
                    'should_have_error': True
                },
                {
                    'name': 'Missing group',
                    'data': {
                        'first_name': 'Test',
                        'last_name': 'Student',
                        'password': 'test123',
                        'confirm_password': 'test123'
                    },
                    'expected_status': 200,
                    'should_have_error': True
                },
                {
                    'name': 'Password mismatch',
                    'data': {
                        'first_name': 'Test',
                        'last_name': 'Student',
                        'group_id': str(test_group.id),
                        'password': 'test123',
                        'confirm_password': 'different'
                    },
                    'expected_status': 200,
                    'should_have_error': True
                },
                {
                    'name': 'Short password',
                    'data': {
                        'first_name': 'Test',
                        'last_name': 'Student',
                        'group_id': str(test_group.id),
                        'password': '123',
                        'confirm_password': '123'
                    },
                    'expected_status': 200,
                    'should_have_error': True
                },
                {
                    'name': 'Valid registration',
                    'data': {
                        'first_name': 'Debug',
                        'last_name': 'User',
                        'group_id': str(test_group.id),
                        'password': 'debug123',
                        'confirm_password': 'debug123'
                    },
                    'expected_status': 302,  # Redirect after success
                    'should_have_error': False
                }
            ]
            
            for scenario in scenarios:
                print(f"\nTesting: {scenario['name']}")
                response = client.post('/register', data=scenario['data'], follow_redirects=False)
                
                print(f"  Status: {response.status_code} (expected: {scenario['expected_status']})")
                
                if response.status_code == scenario['expected_status']:
                    print(f"  Status: OK")
                else:
                    print(f"  Status: MISMATCH")
                
                # Check for error in response
                content = response.data.decode('utf-8')
                has_error = 'alert' in content or 'error' in content.lower()
                
                if scenario['should_have_error']:
                    print(f"  Error display: {'OK' if has_error else 'MISSING'}")
                else:
                    print(f"  No error: {'OK' if not has_error else 'UNEXPECTED ERROR'}")
                
                # If successful, check if user was created
                if response.status_code == 302:
                    user = app.User.query.filter_by(
                        first_name=scenario['data'].get('first_name'),
                        last_name=scenario['data'].get('last_name'),
                        group_id=scenario['data'].get('group_id')
                    ).first()
                    
                    if user:
                        print(f"  User created: OK ({user.username})")
                    else:
                        print(f"  User created: FAILED")
            
            return True
            
    except Exception as e:
        print(f"POST scenarios test error: {e}")
        return False

def check_registration_route_logic():
    """Check registration route logic"""
    print("\n=== CHECKING REGISTRATION ROUTE LOGIC ===")
    
    try:
        import app
        
        # Check if route exists
        if hasattr(app, 'register'):
            print("Register route: EXISTS")
        else:
            print("Register route: MISSING")
            return False
        
        # Check route decorator
        import inspect
        route_source = inspect.getsource(app.register)
        
        checks = {
            'POST method': '@app.route(\'/register\', methods=[\'GET\', \'POST\'])' in route_source,
            'Form validation': 'request.form.get' in route_source,
            'Password validation': 'password != confirm_password' in route_source,
            'Password length': 'len(password) < 6' in route_source,
            'Group validation': 'Group.query.get(group_id)' in route_source,
            'User creation': 'User(' in route_source,
            'Database commit': 'db.session.commit()' in route_source,
            'Session creation': 'session[' in route_source,
            'Redirect': 'redirect(url_for(' in route_source
        }
        
        print("Route logic checks:")
        for check, exists in checks.items():
            status = "OK" if exists else "MISSING"
            print(f"  {check}: {status}")
        
        return all(checks.values())
        
    except Exception as e:
        print(f"Route logic check error: {e}")
        return False

def check_database_models():
    """Check database models for registration"""
    print("\n=== CHECKING DATABASE MODELS ===")
    
    try:
        import app
        
        # Check User model
        user_fields = {
            'username': hasattr(app.User, 'username'),
            'password_hash': hasattr(app.User, 'password_hash'),
            'first_name': hasattr(app.User, 'first_name'),
            'last_name': hasattr(app.User, 'last_name'),
            'group_id': hasattr(app.User, 'group_id'),
            'is_admin': hasattr(app.User, 'is_admin'),
            'is_group_leader': hasattr(app.User, 'is_group_leader')
        }
        
        print("User model fields:")
        for field, exists in user_fields.items():
            status = "OK" if exists else "MISSING"
            print(f"  {field}: {status}")
        
        # Check Group model
        group_fields = {
            'name': hasattr(app.Group, 'name'),
            'description': hasattr(app.Group, 'description'),
            'total_score': hasattr(app.Group, 'total_score')
        }
        
        print("\nGroup model fields:")
        for field, exists in group_fields.items():
            status = "OK" if exists else "MISSING"
            print(f"  {field}: {status}")
        
        return all(user_fields.values()) and all(group_fields.values())
        
    except Exception as e:
        print(f"Database models check error: {e}")
        return False

def main():
    """Main debugging function"""
    print("STEP BY STEP EDUCATION PLATFORM - REGISTRATION DEBUG")
    print("Debugging registration issues...")
    
    results = []
    
    # Test form details
    results.append(("Form Details", test_registration_form_details()))
    
    # Test POST scenarios
    results.append(("POST Scenarios", test_registration_post_scenarios()))
    
    # Check route logic
    results.append(("Route Logic", check_registration_route_logic()))
    
    # Check database models
    results.append(("Database Models", check_database_models()))
    
    print("\n=== DEBUG RESULTS ===")
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"{test_name}: {status}")
    
    failed_tests = [name for name, result in results if not result]
    
    if failed_tests:
        print(f"\nFailed tests: {failed_tests}")
        print("Please check the issues above.")
        return False
    else:
        print("\nAll debug tests passed!")
        print("Registration functionality appears to be working correctly.")
        print("If you're still experiencing issues, please provide more specific details.")
        return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
