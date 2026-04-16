#!/usr/bin/env python3
"""
Debug Server Error
Investigate and fix Internal Server Error
"""

import os
import sys
import traceback

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_app_syntax():
    """Check app.py for syntax errors"""
    print("=== CHECKING APP SYNTAX ===")
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to compile
        compile(content, 'app.py', 'exec')
        print("Syntax check: PASSED")
        return True
        
    except SyntaxError as e:
        print(f"Syntax error: {e}")
        print(f"Line {e.lineno}: {e.text}")
        return False
    except Exception as e:
        print(f"Syntax check error: {e}")
        return False

def test_app_import():
    """Test if app can be imported"""
    print("\n=== TESTING APP IMPORT ===")
    
    try:
        import app
        print("App import: PASSED")
        print(f"App object: {app.app}")
        return True
    except Exception as e:
        print(f"App import error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_database_connection():
    """Test database connection"""
    print("\n=== TESTING DATABASE CONNECTION ===")
    
    try:
        import app
        
        with app.app.app_context():
            # Try to execute a simple query
            result = app.db.session.execute('SELECT 1').fetchone()
            print(f"Database connection: OK (result: {result})")
            
            # Check tables
            tables = app.db.session.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' 
                ORDER BY name
            """).fetchall()
            
            print(f"Tables found: {[t[0] for t in tables]}")
            return True
            
    except Exception as e:
        print(f"Database connection error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_routes():
    """Test if routes are properly defined"""
    print("\n=== TESTING ROUTES ===")
    
    try:
        import app
        
        # Check if we can access the URL map
        routes = list(app.app.url_map.iter_rules())
        print(f"Total routes: {len(routes)}")
        
        # Check for essential routes
        essential_routes = ['/', '/login', '/register', '/admin/dashboard', '/student_dashboard']
        missing_routes = []
        
        for route in essential_routes:
            found = any(rule.rule == route for rule in routes)
            if not found:
                missing_routes.append(route)
        
        if missing_routes:
            print(f"Missing routes: {missing_routes}")
            return False
        else:
            print("All essential routes found")
            return True
            
    except Exception as e:
        print(f"Routes test error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_models():
    """Test if models are properly defined"""
    print("\n=== TESTING MODELS ===")
    
    try:
        import app
        
        models = ['User', 'Group', 'Subject', 'Topic', 'Test', 'Question', 'TestResult', 'Certificate']
        
        for model_name in models:
            if hasattr(app, model_name):
                model_class = getattr(app, model_name)
                print(f"Model {model_name}: OK")
            else:
                print(f"Model {model_name}: MISSING")
                return False
        
        return True
        
    except Exception as e:
        print(f"Models test error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

def check_missing_functions():
    """Check for missing functions that might be called"""
    print("\n=== CHECKING MISSING FUNCTIONS ===")
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for function calls that might not exist
        missing_functions = []
        
        # Common functions that might be missing
        functions_to_check = [
            'calculate_daily_points',
            'calculate_dtm_points',
            'generate_username',
            'generate_password',
            'check_password_hash',
            'ensure_database_integrity',
            'clear_all_caches'
        ]
        
        for func_name in functions_to_check:
            if func_name in content and f'def {func_name}(' not in content:
                missing_functions.append(func_name)
        
        if missing_functions:
            print(f"Missing functions: {missing_functions}")
            return False
        else:
            print("All required functions found")
            return True
            
    except Exception as e:
        print(f"Function check error: {e}")
        return False

def create_missing_functions():
    """Create missing helper functions"""
    print("\n=== CREATING MISSING FUNCTIONS ===")
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add missing functions at the end
        missing_functions_code = '''

# Helper Functions
def calculate_daily_points(percentage):
    """Calculate daily points based on percentage"""
    if percentage >= 95:
        return 10
    elif percentage >= 85:
        return 8
    elif percentage >= 75:
        return 6
    elif percentage >= 60:
        return 4
    elif percentage >= 50:
        return 2
    else:
        return 0

def calculate_dtm_points(rank, total_participants):
    """Calculate DTM test points"""
    if rank == 1:
        return 100
    elif rank == 2:
        return 80
    elif rank == 3:
        return 60
    elif rank == 4:
        return 40
    elif rank == 5:
        return 20
    else:
        return 10

def generate_username(first_name, last_name, group_name):
    """Generate username from name and group"""
    base_name = f"{first_name.lower()}.{last_name.lower()}"
    username = f"{base_name}.{group_name.lower()}"
    
    # Check if username exists and add number if needed
    counter = 1
    original_username = username
    while User.query.filter_by(username=username).first():
        username = f"{original_username}{counter}"
        counter += 1
    
    return username

def generate_password(length=8):
    """Generate random password"""
    import random
    import string
    
    characters = string.ascii_letters + string.digits
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

def ensure_database_integrity():
    """Ensure database integrity"""
    try:
        with app.app_context():
            from sqlalchemy import text
            
            # Clean up orphaned records
            db.session.execute(text("DELETE FROM test_registration WHERE user_id NOT IN (SELECT id FROM user)"))
            db.session.execute(text("DELETE FROM test_result WHERE user_id NOT IN (SELECT id FROM user)"))
            db.session.execute(text("DELETE FROM certificate WHERE user_id NOT IN (SELECT id FROM user)"))
            db.session.commit()
            
    except Exception as e:
        app.logger.error(f"Database integrity error: {e}")
        db.session.rollback()

def clear_all_caches():
    """Clear all caches"""
    try:
        # Clear any application-level caches
        if hasattr(app, '_cached_user_data'):
            app._cached_user_data.clear()
        
        # Clear session data if in request context
        try:
            from flask import session
            session.clear()
        except RuntimeError:
            pass
        
    except Exception as e:
        app.logger.error(f"Cache clearing error: {e}")
'''
        
        # Add missing functions before the last part
        if 'if __name__ == \'__main__\':' in content:
            insert_pos = content.find('if __name__ == \'__main__\':')
            content = content[:insert_pos] + missing_functions_code + '\n' + content[insert_pos:]
        else:
            content += missing_functions_code
        
        # Write back
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("Missing functions added!")
        return True
        
    except Exception as e:
        print(f"Error creating missing functions: {e}")
        return False

def main():
    """Main debug function"""
    print("STEP BY STEP EDUCATION PLATFORM - SERVER ERROR DEBUG")
    print("Investigating Internal Server Error...")
    
    tests = [
        ("Syntax Check", check_app_syntax),
        ("App Import", test_app_import),
        ("Database Connection", test_database_connection),
        ("Routes", test_routes),
        ("Models", test_models),
        ("Missing Functions", check_missing_functions)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print('='*50)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"Test {test_name} failed: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*50}")
    print("DEBUG SUMMARY")
    print('='*50)
    
    failed_tests = [name for name, result in results if not result]
    
    if failed_tests:
        print(f"Failed tests: {failed_tests}")
        
        # Try to fix missing functions
        if "Missing Functions" in failed_tests:
            print("\nTrying to create missing functions...")
            if create_missing_functions():
                print("Missing functions created successfully!")
            else:
                print("Failed to create missing functions")
        
        return False
    else:
        print("All tests passed!")
        return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
