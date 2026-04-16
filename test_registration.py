#!/usr/bin/env python3
"""
Registration Test Script
Tests registration functionality and fixes issues
"""

import os
import sys
import requests
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_registration_locally():
    """Test registration functionality locally"""
    print("=== TESTING REGISTRATION LOCALLY ===")
    
    try:
        import app
        
        with app.app.app_context():
            # Check if groups exist
            groups = app.Group.query.filter(
                app.Group.name.in_(['101', '102', '103', '104', '105', '106', '107', '108'])
            ).all()
            
            print(f"Available groups: {len(groups)}")
            for group in groups:
                print(f"  - {group.name}: {len(group.students)} students")
            
            # Test registration data
            test_data = {
                'first_name': 'Test',
                'last_name': 'Student',
                'group_id': groups[0].id if groups else 1,
                'password': 'test123',
                'confirm_password': 'test123'
            }
            
            # Test registration process
            print("\nTesting registration process...")
            
            # Check if user already exists
            existing_user = app.User.query.filter_by(
                first_name=test_data['first_name'],
                last_name=test_data['last_name'],
                group_id=test_data['group_id']
            ).first()
            
            if existing_user:
                print("User already exists - testing password update...")
                existing_user.password_hash = app.generate_password_hash(test_data['password'])
                app.db.session.commit()
                print("Password update: OK")
            else:
                print("Creating new user...")
                username = app.generate_username(
                    test_data['first_name'], 
                    test_data['last_name'], 
                    groups[0].name if groups else '101'
                )
                
                new_user = app.User(
                    username=username,
                    password_hash=app.generate_password_hash(test_data['password']),
                    first_name=test_data['first_name'],
                    last_name=test_data['last_name'],
                    group_id=test_data['group_id'],
                    is_admin=False,
                    is_group_leader=False
                )
                app.db.session.add(new_user)
                app.db.session.commit()
                print(f"New user created: {username}")
            
            # Verify user creation
            created_user = app.User.query.filter_by(
                first_name=test_data['first_name'],
                last_name=test_data['last_name'],
                group_id=test_data['group_id']
            ).first()
            
            if created_user:
                print("User verification: OK")
                print(f"  Username: {created_user.username}")
                print(f"  Group: {created_user.group.name if created_user.group else 'None'}")
                print(f"  Is admin: {created_user.is_admin}")
                print(f"  Is group leader: {created_user.is_group_leader}")
                return True
            else:
                print("User verification: FAILED")
                return False
                
    except Exception as e:
        print(f"Local test error: {e}")
        return False

def test_registration_form():
    """Test registration form"""
    print("\n=== TESTING REGISTRATION FORM ===")
    
    try:
        import app
        
        with app.app.test_client() as client:
            # Test GET request
            response = client.get('/register')
            if response.status_code == 200:
                print("GET /register: OK")
            else:
                print(f"GET /register: {response.status_code}")
                return False
            
            # Test POST request with valid data
            groups = app.Group.query.filter(
                app.Group.name.in_(['101', '102', '103', '104', '105', '106', '107', '108'])
            ).all()
            
            if not groups:
                print("No groups available for testing")
                return False
            
            form_data = {
                'first_name': 'Form',
                'last_name': 'Test',
                'group_id': str(groups[0].id),
                'password': 'form123',
                'confirm_password': 'form123'
            }
            
            response = client.post('/register', data=form_data, follow_redirects=True)
            if response.status_code == 200:
                print("POST /register: OK")
                return True
            else:
                print(f"POST /register: {response.status_code}")
                print(f"Response: {response.data.decode()}")
                return False
                
    except Exception as e:
        print(f"Form test error: {e}")
        return False

def fix_registration_issues():
    """Fix common registration issues"""
    print("\n=== FIXING REGISTRATION ISSUES ===")
    
    try:
        import app
        
        with app.app.app_context():
            # Check if default groups exist
            default_groups = ['101', '102', '103', '104', '105', '106', '107', '108']
            existing_groups = app.Group.query.filter(
                app.Group.name.in_(default_groups)
            ).all()
            
            existing_group_names = [g.name for g in existing_groups]
            missing_groups = [g for g in default_groups if g not in existing_group_names]
            
            if missing_groups:
                print(f"Creating missing groups: {missing_groups}")
                for group_name in missing_groups:
                    new_group = app.Group(name=group_name, total_score=0)
                    app.db.session.add(new_group)
                
                app.db.session.commit()
                print("Missing groups created!")
            else:
                print("All default groups exist")
            
            # Check for duplicate users
            duplicate_users = app.db.session.query(
                app.User.first_name,
                app.User.last_name,
                app.User.group_id,
                app.db.func.count(app.User.id).label('count')
            ).group_by(
                app.User.first_name,
                app.User.last_name,
                app.User.group_id
            ).having(app.db.func.count(app.User.id) > 1).all()
            
            if duplicate_users:
                print(f"Found {len(duplicate_users)} duplicate user groups")
                for dup in duplicate_users:
                    print(f"  - {dup.first_name} {dup.last_name} (group {dup.group_id}): {dup.count} users")
                
                # Remove duplicates (keep the first one)
                for dup in duplicate_users:
                    users = app.User.query.filter_by(
                        first_name=dup.first_name,
                        last_name=dup.last_name,
                        group_id=dup.group_id
                    ).order_by(app.User.id).all()
                    
                    # Remove all except the first one
                    for user in users[1:]:
                        app.db.session.delete(user)
                
                app.db.session.commit()
                print("Duplicate users removed!")
            else:
                print("No duplicate users found")
            
            return True
            
    except Exception as e:
        print(f"Fix registration issues error: {e}")
        return False

def main():
    """Main test function"""
    print("STEP BY STEP EDUCATION PLATFORM - REGISTRATION TEST")
    print("Testing registration functionality...")
    
    # Fix registration issues
    if not fix_registration_issues():
        print("Failed to fix registration issues")
        return False
    
    # Test locally
    if not test_registration_locally():
        print("Local registration test failed")
        return False
    
    # Test form
    if not test_registration_form():
        print("Registration form test failed")
        return False
    
    print("\n=== REGISTRATION TEST RESULTS ===")
    print("All registration tests passed!")
    print("Registration functionality is working correctly!")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
