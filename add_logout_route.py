#!/usr/bin/env python3
"""
Add Logout Route
Add missing logout route
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def add_logout_route():
    """Add missing logout route"""
    print("=== ADDING LOGOUT ROUTE ===")
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if logout route exists
        if 'def logout():' not in content:
            # Add logout route before the last route
            logout_route_code = '''@app.route('/logout')
def logout():
    session.clear()
    flash('Siz tizimdan chiqdingiz', 'info')
    return redirect(url_for('login'))

'''
            
            # Find a good place to insert (before the last route)
            last_route_pos = content.rfind('@app.route')
            if last_route_pos != -1:
                content = content[:last_route_pos] + logout_route_code + '\n' + content[last_route_pos:]
            
            # Write back
            with open('app.py', 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("Logout route added!")
            return True
        else:
            print("Logout route already exists")
            return True
            
    except Exception as e:
        print(f"Error adding logout route: {e}")
        return False

def test_logout_route():
    """Test logout route"""
    print("\n=== TESTING LOGOUT ROUTE ===")
    
    try:
        import app
        
        # Check if route exists
        routes = list(app.app.url_map.iter_rules())
        route_rules = [route.rule for route in routes]
        
        if '/logout' in route_rules:
            print("Logout route: EXISTS")
            return True
        else:
            print("Logout route: MISSING")
            return False
            
    except Exception as e:
        print(f"Error testing logout route: {e}")
        return False

def test_login_after_logout_fix():
    """Test login after adding logout route"""
    print("\n=== TESTING LOGIN AFTER LOGOUT FIX ===")
    
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
    print("STEP BY STEP EDUCATION PLATFORM - ADD LOGOUT ROUTE")
    print("Adding missing logout route...")
    
    if add_logout_route():
        if test_logout_route():
            if test_login_after_logout_fix():
                print("\n=== LOGOUT ROUTE ADDED SUCCESSFULLY ===")
                print("Internal Server Error should be fixed!")
                return True
            else:
                print("\nLogin test failed!")
                return False
        else:
            print("\nLogout route test failed!")
            return False
    else:
        print("\nLogout route addition failed!")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
