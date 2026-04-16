#!/usr/bin/env python3
"""
Remove Duplicate Restore Route
Completely remove the duplicate admin_restore route
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def remove_duplicate_restore():
    """Remove duplicate admin_restore route"""
    print("=== REMOVING DUPLICATE ADMIN_RESTORE ===")
    
    try:
        # Read the file
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all admin_restore routes
        lines = content.split('\n')
        restore_indices = []
        
        for i, line in enumerate(lines):
            if '@app.route(\'/admin/restore\')' in line:
                restore_indices.append(i)
        
        print(f"Found admin_restore routes at lines: {[i+1 for i in restore_indices]}")
        
        if len(restore_indices) > 1:
            # Remove the last one (around line 1877)
            last_restore = restore_indices[-1]
            
            # Find the end of this function
            end_line = len(lines)
            for i in range(last_restore + 1, len(lines)):
                if lines[i].strip() and not lines[i].startswith(' ') and not lines[i].startswith('\t'):
                    end_line = i
                    break
            
            print(f"Removing lines {last_restore+1} to {end_line}")
            
            # Remove the duplicate
            new_lines = lines[:last_restore] + lines[end_line:]
            
            # Write back
            with open('app.py', 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_lines))
            
            print(f"Removed {end_line - last_restore} lines")
            return True
        else:
            print("No duplicate admin_restore found")
            return True
            
    except Exception as e:
        print(f"Error removing duplicate: {e}")
        return False

def test_final():
    """Final test"""
    print("\n=== FINAL TEST ===")
    
    try:
        import subprocess
        
        # Test syntax
        result = subprocess.run(['python', '-m', 'py_compile', 'app.py'], 
                              capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Syntax error: {result.stderr}")
            return False
        
        # Test import
        result = subprocess.run(['python', '-c', 'import app'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            print(f"Import error: {result.stderr}")
            return False
        
        print("All tests passed!")
        return True
        
    except Exception as e:
        print(f"Error in final test: {e}")
        return False

def main():
    """Main function"""
    print("STEP BY STEP EDUCATION PLATFORM - REMOVE DUPLICATE RESTORE")
    print("Removing duplicate admin_restore route...")
    
    if remove_duplicate_restore():
        if test_final():
            print("\n=== DUPLICATE REMOVAL SUCCESS ===")
            print("Ready for deployment!")
            return True
        else:
            print("\nFinal test failed!")
            return False
    else:
        print("\nDuplicate removal failed!")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
