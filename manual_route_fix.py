#!/usr/bin/env python3
"""
Manual Route Fix
Manually fix duplicate routes by editing specific lines
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def manual_fix_routes():
    """Manually fix duplicate routes"""
    print("=== MANUAL ROUTE FIX ===")
    
    try:
        # Read current app.py
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find and remove the duplicate admin_restore route
        # Look for the pattern around line 1873 based on error
        lines = content.split('\n')
        
        # Find the second admin_restore route
        admin_restore_count = 0
        duplicate_start = -1
        duplicate_end = -1
        
        for i, line in enumerate(lines):
            if '@app.route(\'/admin/restore\')' in line:
                admin_restore_count += 1
                if admin_restore_count == 2:
                    duplicate_start = i
                    print(f"Found duplicate admin_restore at line {i+1}")
                    break
        
        if duplicate_start != -1:
            # Find the end of this function
            for i in range(duplicate_start + 1, len(lines)):
                if lines[i].strip() and not lines[i].startswith(' ') and not lines[i].startswith('\t'):
                    duplicate_end = i
                    break
                elif i == len(lines) - 1:
                    duplicate_end = i + 1
                    break
            
            print(f"Removing lines {duplicate_start+1} to {duplicate_end}")
            
            # Remove the duplicate function
            new_lines = lines[:duplicate_start] + lines[duplicate_end:]
            
            # Write fixed content
            with open('app.py', 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_lines))
            
            print(f"Removed {duplicate_end - duplicate_start} lines")
            return True
        else:
            print("No duplicate admin_restore found")
            return False
            
    except Exception as e:
        print(f"Error in manual fix: {e}")
        return False

def check_syntax():
    """Check if the Python syntax is valid"""
    print("\n=== CHECKING SYNTAX ===")
    
    try:
        import subprocess
        
        # Try to compile the Python file
        result = subprocess.run(['python', '-m', 'py_compile', 'app.py'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Python syntax is valid!")
            return True
        else:
            print(f"Syntax error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Error checking syntax: {e}")
        return False

def main():
    """Main function"""
    print("STEP BY STEP EDUCATION PLATFORM - MANUAL ROUTE FIX")
    print("Manually fixing duplicate routes...")
    
    if manual_fix_routes():
        if check_syntax():
            print("\n=== MANUAL FIX COMPLETE ===")
            print("Duplicate routes fixed successfully!")
            print("Ready for deployment!")
            return True
        else:
            print("\nSyntax check failed!")
            return False
    else:
        print("\nManual fix failed!")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
