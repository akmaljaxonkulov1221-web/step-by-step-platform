#!/usr/bin/env python3
"""
Fix Duplicate Routes
Remove duplicate admin_backup route
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def fix_duplicate_routes():
    """Fix duplicate route definitions"""
    print("=== FIXING DUPLICATE ROUTES ===")
    
    try:
        # Read current app.py
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find and remove duplicate admin_backup route
        lines = content.split('\n')
        new_lines = []
        skip_next = False
        
        for i, line in enumerate(lines):
            if 'def admin_backup():' in line:
                # Check if this is a duplicate
                if i > 0 and 'def admin_backup():' in '\n'.join(lines[max(0, i-10):i]):
                    print(f"Found duplicate admin_backup at line {i+1}")
                    skip_next = True
                    continue
            
            if skip_next and line.strip().startswith('@app.route'):
                # Found the next route, stop skipping
                skip_next = False
                new_lines.append(line)
            elif not skip_next:
                new_lines.append(line)
        
        # Write fixed content
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        
        print("Duplicate routes fixed!")
        return True
        
    except Exception as e:
        print(f"Error fixing duplicate routes: {e}")
        return False

def main():
    """Main function"""
    print("STEP BY STEP EDUCATION PLATFORM - FIX DUPLICATE ROUTES")
    print("Fixing duplicate route definitions...")
    
    if fix_duplicate_routes():
        print("Duplicate routes fixed successfully!")
        return True
    else:
        print("Failed to fix duplicate routes!")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
