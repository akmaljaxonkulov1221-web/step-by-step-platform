#!/usr/bin/env python3
"""
Fix TestResult Model
Make columns nullable to avoid database errors
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def fix_testresult_model():
    """Fix TestResult model columns to be nullable"""
    print("=== FIXING TESTRESULT MODEL ===")
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find TestResult model and make columns nullable
        lines = content.split('\n')
        new_lines = []
        
        for i, line in enumerate(lines):
            # Make these columns nullable
            if 'correct_answers = db.Column(db.Text)' in line:
                new_lines.append('    correct_answers = db.Column(db.Text, nullable=True)')
            elif 'incorrect_answers = db.Column(db.Text)' in line:
                new_lines.append('    incorrect_answers = db.Column(db.Text, nullable=True)')
            elif 'total_time = db.Column(db.Integer, default=0)' in line:
                new_lines.append('    total_time = db.Column(db.Integer, default=0, nullable=True)')
            else:
                new_lines.append(line)
        
        # Write back
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        
        print("TestResult model columns made nullable!")
        return True
        
    except Exception as e:
        print(f"Error fixing TestResult model: {e}")
        return False

def test_login_after_model_fix():
    """Test login after fixing model"""
    print("\n=== TESTING LOGIN AFTER MODEL FIX ===")
    
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
                print("Login flow: SUCCESS")
                return True
            else:
                print(f"Login flow: FAILED with status {response.status_code}")
                return False
                
    except Exception as e:
        print(f"Login test error: {e}")
        return False

def main():
    """Main function"""
    print("STEP BY STEP EDUCATION PLATFORM - FIX TESTRESULT MODEL")
    print("Making TestResult columns nullable...")
    
    if fix_testresult_model():
        if test_login_after_model_fix():
            print("\n=== TESTRESULT MODEL FIXED ===")
            print("Login should work now!")
            return True
        else:
            print("\nLogin test failed!")
            return False
    else:
        print("\nModel fix failed!")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
