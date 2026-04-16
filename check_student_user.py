#!/usr/bin/env python3
"""
Check Student User
Check if student1 user exists and is properly configured
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_student_user():
    """Check student user"""
    print("=== CHECKING STUDENT USER ===")
    
    try:
        import app
        
        with app.app.app_context():
            # Check if student1 user exists
            student1 = app.User.query.filter_by(username='student1').first()
            
            if student1:
                print(f"Student1 user: FOUND")
                print(f"  ID: {student1.id}")
                print(f"  Username: {student1.username}")
                print(f"  First name: {student1.first_name}")
                print(f"  Last name: {student1.last_name}")
                print(f"  Is admin: {student1.is_admin}")
                print(f"  Is group leader: {student1.is_group_leader}")
                print(f"  Group ID: {student1.group_id}")
                print(f"  Needs password change: {student1.needs_password_change}")
                
                # Check password
                if app.check_password_hash(student1.password_hash, 'password1'):
                    print("  Password: CORRECT")
                else:
                    print("  Password: INCORRECT")
                
                return True
            else:
                print("Student1 user: NOT FOUND")
                
                # Create student1 user
                print("Creating student1 user...")
                
                # Find or create a group
                group = app.Group.query.filter_by(name='101').first()
                if not group:
                    group = app.Group(name='101', total_score=0)
                    app.db.session.add(group)
                    app.db.session.flush()
                
                # Create student1 user
                student1 = app.User(
                    username='student1',
                    password_hash=app.generate_password_hash('password1'),
                    first_name='Student',
                    last_name='One',
                    group_id=group.id,
                    is_admin=False,
                    is_group_leader=False
                )
                app.db.session.add(student1)
                app.db.session.commit()
                
                print("Student1 user: CREATED")
                return True
            
    except Exception as e:
        print(f"Error checking student user: {e}")
        return False

def test_login_with_student1():
    """Test login with student1"""
    print("\n=== TESTING LOGIN WITH STUDENT1 ===")
    
    try:
        import app
        
        with app.app.test_client() as client:
            # Test student login
            response = client.post('/login', data={
                'username': 'student1',
                'password': 'password1'
            }, follow_redirects=False)
            
            print(f"Login response: {response.status_code}")
            
            if response.status_code == 302:
                print(f"Redirect location: {response.location}")
                
                # Follow redirect
                response = client.get(response.location)
                print(f"After redirect: {response.status_code}")
                
                if response.status_code == 200:
                    print("Login and redirect: WORKING")
                    return True
                else:
                    print("After redirect: FAILED")
                    return False
            elif response.status_code == 200:
                print("Login successful (no redirect)")
                
                # Check session
                with client.session_transaction() as sess:
                    print(f"Session logged_in: {sess.get('logged_in', False)}")
                    print(f"Session user_id: {sess.get('user_id', None)}")
                    print(f"Session username: {sess.get('username', None)}")
                    print(f"Session is_admin: {sess.get('is_admin', False)}")
                
                return True
            else:
                print(f"Login failed: {response.status_code}")
                return False
            
    except Exception as e:
        print(f"Login test error: {e}")
        return False

def main():
    """Main function"""
    print("STEP BY STEP EDUCATION PLATFORM - CHECK STUDENT USER")
    print("Checking student1 user configuration...")
    
    if check_student_user():
        if test_login_with_student1():
            print("\n=== STUDENT USER CONFIGURATION WORKING ===")
            return True
        else:
            print("\nLogin test failed!")
            return False
    else:
        print("\nStudent user check failed!")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
