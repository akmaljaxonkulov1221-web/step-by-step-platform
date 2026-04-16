#!/usr/bin/env python3
"""
Fix Werkzeug Import
Fix werkzeug import issue in check_password_hash function
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def fix_werkzeug_import():
    """Fix werkzeug import in app.py"""
    print("=== FIXING WERKZEUG IMPORT ===")
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if werkzeug is imported
        if 'import werkzeug' not in content and 'from werkzeug' not in content:
            # Add werkzeug import at the top
            import_end = content.find('from flask import')
            if import_end != -1:
                # Find the end of the import section
                end_of_imports = content.find('\n\n', import_end)
                if end_of_imports == -1:
                    end_of_imports = len(content)
                
                # Add werkzeug import
                werkzeug_import = 'from werkzeug.security import generate_password_hash, check_password_hash\n'
                content = content[:end_of_imports] + werkzeug_import + '\n' + content[end_of_imports:]
                
                # Update check_password_hash function to use werkzeug.security
                content = content.replace(
                    'def check_password_hash(pw_hash, password):\n    """Check if password matches hash"""\n    return werkzeug.security.check_password_hash(pw_hash, password)',
                    'def check_password_hash(pw_hash, password):\n    """Check if password matches hash"""\n    return check_password_hash(pw_hash, password)'
                )
                
                # Update generate_password_hash function
                content = content.replace(
                    'def generate_password(length=8):\n    """Generate random password"""\n    import random\n    import string\n    \n    characters = string.ascii_letters + string.digits\n    password = \'\'.join(random.choice(characters) for _ in range(length))\n    return password',
                    'def generate_password(length=8):\n    """Generate random password"""\n    return generate_password_hash(length)'
                )
                
                # Write back
                with open('app.py', 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print("Werkzeug import fixed!")
                return True
            else:
                print("Could not find import section")
                return False
        else:
            print("Werkzeug already imported")
            return True
            
    except Exception as e:
        print(f"Error fixing werkzeug import: {e}")
        return False

def test_fixed_login():
    """Test login after fixing werkzeug import"""
    print("\n=== TESTING FIXED LOGIN ===")
    
    try:
        import app
        
        with app.app.app_context():
            # Test check_password_hash function
            admin_user = app.User.query.filter_by(username='admin').first()
            if admin_user:
                if app.check_password_hash(admin_user.password_hash, 'admin123'):
                    print("Password verification: OK")
                    return True
                else:
                    print("Password verification: FAILED")
                    return False
            else:
                print("Admin user not found")
                return False
                
    except Exception as e:
        print(f"Login test error: {e}")
        return False

def main():
    """Main function"""
    print("STEP BY STEP EDUCATION PLATFORM - FIX WERKZEUG IMPORT")
    print("Fixing werkzeug import issue...")
    
    if fix_werkzeug_import():
        if test_fixed_login():
            print("\n=== WERKZEUG IMPORT FIXED ===")
            print("Login functionality should work now!")
            return True
        else:
            print("\nLogin test failed!")
            return False
    else:
        print("\nWerkzeug import fix failed!")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
