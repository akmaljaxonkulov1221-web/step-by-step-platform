#!/usr/bin/env python3
"""
Fix Duplicate Student Dashboard
Remove duplicate student_dashboard route
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def fix_duplicate_student_dashboard():
    """Fix duplicate student_dashboard route"""
    print("=== FIXING DUPLICATE STUDENT DASHBOARD ===")
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all student_dashboard routes
        lines = content.split('\n')
        dashboard_routes = []
        
        for i, line in enumerate(lines):
            if '@app.route(\'/student/dashboard\')' in line:
                dashboard_routes.append(i)
        
        print(f"Found student_dashboard routes at lines: {[i+1 for i in dashboard_routes]}")
        
        if len(dashboard_routes) > 1:
            # Remove duplicates, keep the first one
            first_route = dashboard_routes[0]
            lines_to_remove = set()
            
            for route_pos in dashboard_routes[1:]:
                # Remove from decorator to end of function
                for i in range(route_pos, len(lines)):
                    if i == route_pos and '@app.route' in lines[i]:
                        lines_to_remove.add(i)
                    elif i > route_pos and lines[i].strip().startswith('@app.route'):
                        break
                    elif i > route_pos and lines[i].strip().startswith('def '):
                        lines_to_remove.add(i)
                    elif i in lines_to_remove:
                        lines_to_remove.add(i)
                    elif i > route_pos and lines[i].strip() and not lines[i].startswith(' ') and not lines[i].startswith('\t'):
                        break
            
            # Build new content
            new_lines = []
            for i, line in enumerate(lines):
                if i not in lines_to_remove:
                    new_lines.append(line)
            
            # Write back
            with open('app.py', 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_lines))
            
            print(f"Removed {len(lines_to_remove)} lines containing duplicate student_dashboard routes")
            return True
        else:
            print("No duplicate student_dashboard routes found")
            return True
            
    except Exception as e:
        print(f"Error fixing duplicate student_dashboard: {e}")
        return False

def test_final_app():
    """Test the final app"""
    print("\n=== TESTING FINAL APP ===")
    
    try:
        import app
        
        # Test database connection
        with app.app.app_context():
            from sqlalchemy import text
            result = app.db.session.execute(text('SELECT 1')).fetchone()
            print("Database connection: OK")
        
        # Test routes
        routes = list(app.app.url_map.iter_rules())
        route_rules = [route.rule for route in routes]
        
        essential_routes = ['/', '/login', '/register', '/admin/dashboard', '/student/dashboard']
        missing_routes = [route for route in essential_routes if route not in route_rules]
        
        if missing_routes:
            print(f"Missing routes: {missing_routes}")
            return False
        else:
            print("All essential routes found")
        
        # Test helper functions
        required_functions = ['check_password_hash', 'calculate_daily_points', 'calculate_dtm_points']
        for func_name in required_functions:
            if hasattr(app, func_name):
                print(f"{func_name} function: OK")
            else:
                print(f"{func_name} function: MISSING")
                return False
        
        return True
        
    except Exception as e:
        print(f"Final test error: {e}")
        return False

def main():
    """Main function"""
    print("STEP BY STEP EDUCATION PLATFORM - FIX DUPLICATE STUDENT DASHBOARD")
    print("Fixing duplicate student_dashboard route...")
    
    if fix_duplicate_student_dashboard():
        if test_final_app():
            print("\n=== ALL FIXES COMPLETE ===")
            print("Server errors fixed successfully!")
            return True
        else:
            print("\nFinal test failed!")
            return False
    else:
        print("\nDuplicate fix failed!")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
