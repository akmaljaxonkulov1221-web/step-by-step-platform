#!/usr/bin/env python3
"""
Fix All Duplicate Routes
Remove all duplicate route definitions
"""

import os
import sys
import re

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def fix_all_duplicate_routes():
    """Fix all duplicate route definitions"""
    print("=== FIXING ALL DUPLICATE ROUTES ===")
    
    try:
        # Read current app.py
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all route definitions with their positions
        route_pattern = r"@app\.route\('([^']+)'\)"
        routes = []
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            match = re.search(route_pattern, line)
            if match:
                routes.append({
                    'route': match.group(1),
                    'line': i,
                    'full_line': line
                })
        
        # Find duplicates
        route_counts = {}
        for route_info in routes:
            route = route_info['route']
            if route not in route_counts:
                route_counts[route] = []
            route_counts[route].append(route_info)
        
        duplicates = {route: infos for route, infos in route_counts.items() if len(infos) > 1}
        
        print(f"Found {len(duplicates)} duplicate routes:")
        for route, infos in duplicates.items():
            print(f"  {route}: {len(infos)} times at lines {[i['line'] + 1 for i in infos]}")
        
        # Remove duplicates, keeping first occurrence
        new_lines = []
        lines_to_skip = set()
        
        for route, infos in duplicates.items():
            # Keep first, skip others
            for info in infos[1:]:
                lines_to_skip.add(info['line'])
                # Also skip the function definition lines
                for j in range(info['line'], len(lines)):
                    if j >= len(lines):
                        break
                    if lines[j].strip().startswith('def ') and j > info['line']:
                        # Find the end of this function
                        for k in range(j + 1, len(lines)):
                            if lines[k].strip() and not lines[k].startswith(' ') and not lines[k].startswith('\t'):
                                break
                            lines_to_skip.add(k)
                        break
                    lines_to_skip.add(j)
        
        # Build new content
        for i, line in enumerate(lines):
            if i not in lines_to_skip:
                new_lines.append(line)
        
        # Write fixed content
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        
        print(f"Removed {len(lines_to_skip)} lines containing duplicate routes")
        return True
        
    except Exception as e:
        print(f"Error fixing duplicate routes: {e}")
        return False

def verify_fix():
    """Verify that duplicates are fixed"""
    print("\n=== VERIFYING FIX ===")
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
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
            print(f"Total routes: {len(routes)}")
            return True
            
    except Exception as e:
        print(f"Error verifying fix: {e}")
        return False

def main():
    """Main function"""
    print("STEP BY STEP EDUCATION PLATFORM - FIX ALL DUPLICATE ROUTES")
    print("Fixing all duplicate route definitions...")
    
    if fix_all_duplicate_routes():
        if verify_fix():
            print("\n=== ALL DUPLICATES FIXED ===")
            print("All duplicate routes removed successfully!")
            return True
        else:
            print("\nFix verification failed!")
            return False
    else:
        print("\nDuplicate fix failed!")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
