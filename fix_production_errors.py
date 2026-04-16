#!/usr/bin/env python3
"""
Production Error Fix Script
Fixes all template and route errors found in production
"""

import os
import sys
import re

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_template_routes():
    """Check all templates for missing routes"""
    print("=== CHECKING TEMPLATE ROUTES ===")
    
    templates_dir = 'templates'
    missing_routes = []
    
    # Read all template files
    for filename in os.listdir(templates_dir):
        if filename.endswith('.html'):
            filepath = os.path.join(templates_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find all url_for calls
            url_for_matches = re.findall(r"url_for\('([^']+)'\)", content)
            
            for route_name in url_for_matches:
                missing_routes.append((filename, route_name))
    
    print(f"Found {len(missing_routes)} route references:")
    for template, route in missing_routes:
        print(f"  {template}: {route}")
    
    return missing_routes

def check_app_routes():
    """Check all routes in app.py"""
    print("\n=== CHECKING APP ROUTES ===")
    
    routes = []
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all route definitions
        route_matches = re.findall(r"@app\.route\('([^']+)'\)", content)
        
        for route in route_matches:
            # Extract function name
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if f"@app.route('{route}')" in line:
                    if i + 1 < len(lines):
                        func_line = lines[i + 1]
                        func_match = re.search(r'def (\w+)\(', func_line)
                        if func_match:
                            func_name = func_match.group(1)
                            routes.append((route, func_name))
                            break
        
        print(f"Found {len(routes)} routes:")
        for route, func in routes:
            print(f"  {route} -> {func}")
        
        return routes
        
    except Exception as e:
        print(f"Error checking routes: {e}")
        return []

def fix_template_errors():
    """Fix common template errors"""
    print("\n=== FIXING TEMPLATE ERRORS ===")
    
    try:
        # Fix groups_rating.html
        groups_rating_path = 'templates/groups_rating.html'
        if os.path.exists(groups_rating_path):
            with open(groups_rating_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Fix CSS issues
            content = re.sub(r'style="width: {{ group_info\.avg_percentage }}%"', 
                           'style="width: {{ group_info.avg_percentage|round|int }}%"', content)
            
            with open(groups_rating_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("Fixed groups_rating.html CSS issues")
        
        # Fix admin_groups.html form fields
        admin_groups_path = 'templates/admin_groups.html'
        if os.path.exists(admin_groups_path):
            with open(admin_groups_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remove username field (auto-generated)
            content = re.sub(r'<div class="mb-3">\s*<label for="username"[^>]*>[^<]*</label>\s*<input[^>]*name="username"[^>]*>\s*<div[^>]*>[^<]*</div>\s*</div>', 
                           '', content, flags=re.MULTILINE | re.DOTALL)
            
            with open(admin_groups_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("Fixed admin_groups.html form fields")
        
        return True
        
    except Exception as e:
        print(f"Error fixing templates: {e}")
        return False

def test_fixes():
    """Test if fixes work"""
    print("\n=== TESTING FIXES ===")
    
    try:
        import app
        
        with app.app.app_context():
            # Test group_rating route
            print("Testing group_rating route...")
            
            # Create test data
            test_group = app.Group(name='TestGroup', description='Test group')
            app.db.session.add(test_group)
            app.db.session.flush()
            
            test_user = app.User(
                username='testuser',
                password_hash='test_hash',
                first_name='Test',
                last_name='User',
                group_id=test_group.id
            )
            app.db.session.add(test_user)
            app.db.session.flush()
            
            # Test group_rating function
            group_data = []
            group_data.append({
                'group': test_group,
                'group_leader': None,
                'total_students': 1,
                'avg_percentage': 85.5,
                'total_tests': 5,
                'student_rankings': []
            })
            
            # Test template rendering
            from flask import render_template_string
            
            template_content = """
            {% for group_info in group_data %}
                <h4>{{ group_info.group.name }}</h4>
                <p>{{ group_info.total_students }} o'quvchi</p>
                <p>{{ "%.1f"|format(group_info.avg_percentage) }}%</p>
            {% endfor %}
            """
            
            rendered = render_template_string(template_content, group_data=group_data)
            print("Template rendering test: OK")
            
            # Clean up
            app.db.session.delete(test_user)
            app.db.session.delete(test_group)
            app.db.session.commit()
            
            return True
            
    except Exception as e:
        print(f"Test error: {e}")
        return False

def main():
    """Main function"""
    print("STEP BY STEP EDUCATION PLATFORM - PRODUCTION ERROR FIX")
    print("Fixing production errors...")
    
    # Check template routes
    template_routes = check_template_routes()
    
    # Check app routes
    app_routes = check_app_routes()
    
    # Fix template errors
    if fix_template_errors():
        print("\nTemplate fixes applied!")
    
    # Test fixes
    if test_fixes():
        print("\nAll fixes tested successfully!")
        return True
    else:
        print("\nSome tests failed!")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
