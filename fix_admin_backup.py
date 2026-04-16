#!/usr/bin/env python3
"""
Fix Admin Backup Route
Remove duplicate admin_backup route definition
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def fix_admin_backup_route():
    """Fix duplicate admin_backup route"""
    print("=== FIXING ADMIN_BACKUP ROUTE ===")
    
    try:
        # Read current app.py
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all admin_backup route definitions
        lines = content.split('\n')
        new_lines = []
        backup_routes_found = []
        
        for i, line in enumerate(lines):
            if '@app.route(\'/admin/backup\')' in line:
                backup_routes_found.append(i)
                print(f"Found admin_backup route at line {i+1}")
        
        if len(backup_routes_found) > 1:
            print(f"Found {len(backup_routes_found)} admin_backup routes, keeping the first one")
            
            # Keep only the first occurrence
            first_route = backup_routes_found[0]
            
            for i, line in enumerate(lines):
                # Skip duplicate routes
                is_duplicate = False
                for route_pos in backup_routes_found[1:]:
                    if i >= route_pos - 1:  # Include the decorator line
                        # Find the end of this route function
                        if i == route_pos - 1 and '@app.route' in line:
                            is_duplicate = True
                        elif is_duplicate and line.strip().startswith('@app.route'):
                            break
                        elif is_duplicate and line.strip().startswith('def '):
                            is_duplicate = True
                        elif is_duplicate and line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                            break
                        
                        if is_duplicate:
                            continue
                
                new_lines.append(line)
            
            # Write fixed content
            with open('app.py', 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_lines))
            
            print("Duplicate admin_backup routes removed!")
            return True
        else:
            print("No duplicate admin_backup routes found")
            return True
            
    except Exception as e:
        print(f"Error fixing admin_backup route: {e}")
        return False

def check_for_other_duplicates():
    """Check for other duplicate routes"""
    print("\n=== CHECKING FOR OTHER DUPLICATES ===")
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all route definitions
        import re
        route_pattern = r"@app\.route\('([^']+)'"
        routes = re.findall(route_pattern, content)
        
        # Count occurrences
        route_counts = {}
        for route in routes:
            route_counts[route] = route_counts.get(route, 0) + 1
        
        duplicates = {route: count for route, count in route_counts.items() if count > 1}
        
        if duplicates:
            print("Found duplicate routes:")
            for route, count in duplicates.items():
                print(f"  {route}: {count} times")
        else:
            print("No other duplicate routes found")
        
        return len(duplicates) == 0
        
    except Exception as e:
        print(f"Error checking duplicates: {e}")
        return False

def main():
    """Main function"""
    print("STEP BY STEP EDUCATION PLATFORM - FIX ADMIN_BACKUP ROUTE")
    print("Fixing duplicate admin_backup route...")
    
    success = True
    
    if not fix_admin_backup_route():
        success = False
    
    if not check_for_other_duplicates():
        success = False
    
    if success:
        print("\n=== ROUTE FIX COMPLETE ===")
        print("Admin backup route fixed successfully!")
        return True
    else:
        print("\nRoute fix failed!")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
