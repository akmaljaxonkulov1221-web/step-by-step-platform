#!/usr/bin/env python3
"""
Fix Server Errors
Fix all identified server errors
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def fix_database_queries():
    """Fix database SQL text() issues"""
    print("=== FIXING DATABASE QUERIES ===")
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix SQL queries to use text()
        content = content.replace(
            "db.session.execute('SELECT 1')",
            "db.session.execute(text('SELECT 1'))"
        )
        
        # Fix other common SQL queries
        sql_fixes = [
            ("SELECT name FROM sqlite_master", "SELECT name FROM sqlite_master"),
            ("WHERE type='table'", "WHERE type='table'"),
            ("DELETE FROM test_registration", "DELETE FROM test_registration"),
            ("DELETE FROM test_result", "DELETE FROM test_result"),
            ("DELETE FROM certificate", "DELETE FROM certificate")
        ]
        
        for old_sql, new_sql in sql_fixes:
            if old_sql in content and "text(" not in content.split(old_sql)[1].split('\n')[0]:
                # Fix this SQL query
                lines = content.split('\n')
                new_lines = []
                
                for line in lines:
                    if old_sql in line and "text(" not in line:
                        # Add text() wrapper
                        line = line.replace(old_sql, f"text('{old_sql}')")
                    new_lines.append(line)
                
                content = '\n'.join(new_lines)
        
        # Write back
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("Database queries fixed!")
        return True
        
    except Exception as e:
        print(f"Error fixing database queries: {e}")
        return False

def add_student_dashboard_route():
    """Add missing student_dashboard route"""
    print("=== ADDING STUDENT DASHBOARD ROUTE ===")
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if student_dashboard route exists
        if 'def student_dashboard():' not in content:
            # Add the route before the last route
            student_dashboard_code = '''
@app.route('/student/dashboard')
def student_dashboard():
    if not session.get('logged_in', False):
        return redirect(url_for('login'))
    
    if session.get('is_admin', False):
        return redirect(url_for('admin_dashboard'))
    
    try:
        # Get recent test results
        recent_results = TestResult.query.filter_by(user_id=session['user_id'])\\
            .order_by(TestResult.taken_at.desc())\\
            .limit(5).all()
        
        # Get certificates
        certificates = Certificate.query.filter_by(user_id=session['user_id']).all()
        
        # Get difficult topics
        difficult_topics = DifficultTopic.query.filter_by(user_id=session['user_id']).all()
        
        # Get user's group and group ranking
        user = User.query.get(session['user_id'])
        group_students = User.query.filter_by(group_id=user.group_id, is_admin=False, is_group_leader=False).all()
        
        # Calculate user's rank in group
        user_scores = {}
        for student in group_students:
            total_score = TestResult.query.filter_by(user_id=student.id)\\
                .with_entities(db.func.sum(TestResult.points_earned)).scalar() or 0
            user_scores[student.id] = total_score
        
        sorted_users = sorted(user_scores.items(), key=lambda x: x[1], reverse=True)
        user_rank = next((i+1 for i, (uid, score) in enumerate(sorted_users) if uid == user.id), 0)
        
        return render_template('student_dashboard.html',
                             recent_results=recent_results,
                             certificates=certificates,
                             difficult_topics=difficult_topics,
                             user=user,
                             group_rank=user_rank,
                             total_group_students=len(group_students))
                             
    except Exception as e:
        app.logger.error(f"Student dashboard error: {str(e)}")
        return render_template('student_dashboard.html', error="Dashboard yuklashda xatolik")

'''
            
            # Find a good place to insert (before the last @app.route)
            last_route_pos = content.rfind('@app.route')
            if last_route_pos != -1:
                content = content[:last_route_pos] + student_dashboard_code + '\n' + content[last_route_pos:]
            
            # Write back
            with open('app.py', 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("Student dashboard route added!")
            return True
        else:
            print("Student dashboard route already exists")
            return True
            
    except Exception as e:
        print(f"Error adding student dashboard route: {e}")
        return False

def add_check_password_hash():
    """Add missing check_password_hash function"""
    print("=== ADDING CHECK_PASSWORD_HASH FUNCTION ===")
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'def check_password_hash(' not in content:
            # Add the function
            check_password_hash_code = '''
def check_password_hash(pw_hash, password):
    """Check if password matches hash"""
    return werkzeug.security.check_password_hash(pw_hash, password)

'''
            
            # Find where to insert (after imports)
            import_end = content.find('from datetime import datetime')
            if import_end != -1:
                # Find end of this import line
                end_of_line = content.find('\n', import_end) + 1
                content = content[:end_of_line] + check_password_hash_code + '\n' + content[end_of_line:]
            
            # Write back
            with open('app.py', 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("check_password_hash function added!")
            return True
        else:
            print("check_password_hash function already exists")
            return True
            
    except Exception as e:
        print(f"Error adding check_password_hash function: {e}")
        return False

def test_fixed_app():
    """Test the fixed app"""
    print("\n=== TESTING FIXED APP ===")
    
    try:
        import app
        
        with app.app.app_context():
            # Test database connection
            from sqlalchemy import text
            result = app.db.session.execute(text('SELECT 1')).fetchone()
            print(f"Database connection: OK")
            
            # Test routes
            routes = list(app.app.url_map.iter_rules())
            route_rules = [route.rule for route in routes]
            
            essential_routes = ['/', '/login', '/register', '/admin/dashboard', '/student_dashboard']
            missing_routes = [route for route in essential_routes if route not in route_rules]
            
            if missing_routes:
                print(f"Missing routes: {missing_routes}")
                return False
            else:
                print("All essential routes found")
            
            # Test helper functions
            if hasattr(app, 'check_password_hash'):
                print("check_password_hash function: OK")
            else:
                print("check_password_hash function: MISSING")
                return False
            
            return True
            
    except Exception as e:
        print(f"Test error: {e}")
        return False

def main():
    """Main fix function"""
    print("STEP BY STEP EDUCATION PLATFORM - FIX SERVER ERRORS")
    print("Fixing all identified server errors...")
    
    fixes = [
        ("Database Queries", fix_database_queries),
        ("Student Dashboard Route", add_student_dashboard_route),
        ("Check Password Hash", add_check_password_hash)
    ]
    
    results = []
    for fix_name, fix_func in fixes:
        print(f"\n{'='*50}")
        print(f"Applying: {fix_name}")
        print('='*50)
        
        try:
            result = fix_func()
            results.append((fix_name, result))
        except Exception as e:
            print(f"Fix {fix_name} failed: {e}")
            results.append((fix_name, False))
    
    # Test the fixed app
    print(f"\n{'='*50}")
    print("TESTING FIXED APP")
    print('='*50)
    
    if test_fixed_app():
        print("\n=== ALL FIXES SUCCESSFUL ===")
        print("Server errors fixed successfully!")
        return True
    else:
        print("\nSome fixes failed!")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
