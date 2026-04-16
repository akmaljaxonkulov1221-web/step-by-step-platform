#!/usr/bin/env python3
"""
Fix Check Password Hash Function
Directly fix the check_password_hash function
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def fix_check_password_hash_function():
    """Fix check_password_hash function directly"""
    print("=== FIXING CHECK_PASSWORD_HASH FUNCTION ===")
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find and replace the check_password_hash function
        old_function = '''def check_password_hash(pw_hash, password):
    """Check if password matches hash"""
    return werkzeug.security.check_password_hash(pw_hash, password)'''
        
        new_function = '''def check_password_hash(pw_hash, password):
    """Check if password matches hash"""
    from werkzeug.security import check_password_hash as werkzeug_check
    return werkzeug_check(pw_hash, password)'''
        
        if old_function in content:
            content = content.replace(old_function, new_function)
            print("check_password_hash function fixed!")
        else:
            print("check_password_hash function not found with expected format")
            
            # Try to find and fix any version
            lines = content.split('\n')
            new_lines = []
            
            for i, line in enumerate(lines):
                if 'def check_password_hash(pw_hash, password):' in line:
                    new_lines.append(line)
                    # Skip the next line and add correct implementation
                    new_lines.append('    """Check if password matches hash"""')
                    new_lines.append('    from werkzeug.security import check_password_hash as werkzeug_check')
                    new_lines.append('    return werkzeug_check(pw_hash, password)')
                    # Skip the old implementation line
                    if i + 1 < len(lines) and 'return werkzeug.security.check_password_hash' in lines[i + 1]:
                        continue
                else:
                    new_lines.append(line)
            
            content = '\n'.join(new_lines)
            print("check_password_hash function fixed with alternative method!")
        
        # Write back
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
        
    except Exception as e:
        print(f"Error fixing check_password_hash function: {e}")
        return False

def test_login_after_fix():
    """Test login after fixing the function"""
    print("\n=== TESTING LOGIN AFTER FIX ===")
    
    try:
        import app
        
        with app.app.app_context():
            # Test check_password_hash function
            admin_user = app.User.query.filter_by(username='admin').first()
            if admin_user:
                try:
                    if app.check_password_hash(admin_user.password_hash, 'admin123'):
                        print("Password verification: OK")
                        return True
                    else:
                        print("Password verification: FAILED")
                        return False
                except Exception as e:
                    print(f"Password verification error: {e}")
                    return False
            else:
                print("Admin user not found")
                return False
                
    except Exception as e:
        print(f"Login test error: {e}")
        return False

def test_full_login_flow():
    """Test full login flow"""
    print("\n=== TESTING FULL LOGIN FLOW ===")
    
    try:
        import app
        
        with app.app.test_client() as client:
            # Test login POST
            login_data = {
                'username': 'admin',
                'password': 'admin123'
            }
            
            response = client.post('/login', data=login_data, follow_redirects=True)
            print(f"Login POST status: {response.status_code}")
            
            if response.status_code == 200:
                # Check if redirected to dashboard
                if 'dashboard' in response.data.decode().lower() or 'admin' in response.data.decode().lower():
                    print("Login flow: SUCCESS")
                    return True
                else:
                    print("Login flow: REDIRECT ISSUE")
                    return False
            else:
                print(f"Login flow: FAILED with status {response.status_code}")
                return False
                
    except Exception as e:
        print(f"Full login flow test error: {e}")
        return False

def main():
    """Main function"""
    print("STEP BY STEP EDUCATION PLATFORM - FIX CHECK_PASSWORD_HASH")
    print("Fixing check_password_hash function...")
    
    if fix_check_password_hash_function():
        if test_login_after_fix():
            if test_full_login_flow():
                print("\n=== LOGIN FUNCTIONALITY FIXED ===")
                print("Login should work properly now!")
                return True
            else:
                print("\nFull login flow test failed!")
                return False
        else:
            print("\nLogin test failed!")
            return False
    else:
        print("\nFunction fix failed!")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
