#!/usr/bin/env python3
"""
Fix Restore Duplicate Route
Remove duplicate admin_restore route definition
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def fix_restore_duplicate():
    """Fix duplicate admin_restore route"""
    print("=== FIXING ADMIN_RESTORE DUPLICATE ===")
    
    try:
        # Read current app.py
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all admin_restore route definitions
        lines = content.split('\n')
        restore_routes_found = []
        
        for i, line in enumerate(lines):
            if '@app.route(\'/admin/restore\')' in line:
                restore_routes_found.append(i)
                print(f"Found admin_restore route at line {i+1}")
        
        if len(restore_routes_found) > 1:
            print(f"Found {len(restore_routes_found)} admin_restore routes, keeping the first one")
            
            # Remove all except the first
            first_route = restore_routes_found[0]
            lines_to_remove = set()
            
            for route_pos in restore_routes_found[1:]:
                # Remove from decorator line to end of function
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
            
            # Write fixed content
            with open('app.py', 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_lines))
            
            print(f"Removed {len(lines_to_remove)} lines containing duplicate admin_restore routes")
            return True
        else:
            print("No duplicate admin_restore routes found")
            return True
            
    except Exception as e:
        print(f"Error fixing admin_restore duplicate: {e}")
        return False

def final_verification():
    """Final verification of all routes"""
    print("\n=== FINAL VERIFICATION ===")
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        import re
        route_pattern = r"@app\.route\('([^']+)'"
        routes = re.findall(route_pattern, content)
        
        route_counts = {}
        for route in routes:
            route_counts[route] = route_counts.get(route, 0) + 1
        
        duplicates = {route: count for route, count in route_counts.items() if count > 1}
        
        if duplicates:
            print("Still found duplicates:")
            for route, count in duplicates.items():
                print(f"  {route}: {count} times")
            return False
        else:
            print("No duplicates found!")
            print(f"Total unique routes: {len(routes)}")
            
            # Check for specific routes we need
            required_routes = ['/admin/backup', '/admin/restore', '/ai_chat']
            missing_routes = [route for route in required_routes if route not in routes]
            
            if missing_routes:
                print(f"Missing required routes: {missing_routes}")
                return False
            else:
                print("All required routes present!")
                return True
            
    except Exception as e:
        print(f"Error in final verification: {e}")
        return False

def main():
    """Main function"""
    print("STEP BY STEP EDUCATION PLATFORM - FIX RESTORE DUPLICATE")
    print("Fixing duplicate admin_restore route...")
    
    if fix_restore_duplicate():
        if final_verification():
            print("\n=== ALL DUPLICATES FIXED ===")
            print("All duplicate routes removed successfully!")
            print("Ready for deployment!")
            return True
        else:
            print("\nFinal verification failed!")
            return False
    else:
        print("\nRestore duplicate fix failed!")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
