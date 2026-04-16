#!/usr/bin/env python3
"""
Quick Route Fix
Quickly fix duplicate routes by removing specific lines
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def quick_fix():
    """Quick fix for duplicate routes"""
    print("=== QUICK ROUTE FIX ===")
    
    try:
        # Read the file
        with open('app.py', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Find and remove duplicate admin_restore around line 1873
        # Based on the error, the duplicate is around line 1873
        new_lines = []
        skip_section = False
        
        for i, line in enumerate(lines):
            line_num = i + 1
            
            # Check if we're in the duplicate section
            if line_num >= 1870 and line_num <= 1900:
                if '@app.route(\'/admin/restore\')' in line:
                    # Check if this is the second occurrence
                    admin_restore_count = 0
                    for j in range(min(i, len(lines))):
                        if '@app.route(\'/admin/restore\')' in lines[j]:
                            admin_restore_count += 1
                    
                    if admin_restore_count > 1:
                        print(f"Skipping duplicate admin_restore at line {line_num}")
                        skip_section = True
                        continue
                
                if skip_section:
                    # Skip until we find the next route
                    if line.strip().startswith('@app.route') and 'admin/restore' not in line:
                        skip_section = False
                        new_lines.append(line)
                    elif line.strip().startswith('@app.route') and 'admin/restore' in line:
                        continue
                    elif skip_section:
                        continue
            
            new_lines.append(line)
        
        # Write the fixed file
        with open('app.py', 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        print("Quick fix applied!")
        return True
        
    except Exception as e:
        print(f"Error in quick fix: {e}")
        return False

def test_import():
    """Test if the file can be imported"""
    print("\n=== TESTING IMPORT ===")
    
    try:
        import subprocess
        result = subprocess.run(['python', '-c', 'import app'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("App imports successfully!")
            return True
        else:
            print(f"Import failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Error testing import: {e}")
        return False

def main():
    """Main function"""
    print("STEP BY STEP EDUCATION PLATFORM - QUICK ROUTE FIX")
    print("Quickly fixing duplicate routes...")
    
    if quick_fix():
        if test_import():
            print("\n=== QUICK FIX SUCCESS ===")
            print("Routes fixed successfully!")
            return True
        else:
            print("\nImport test failed!")
            return False
    else:
        print("\nQuick fix failed!")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
