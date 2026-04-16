#!/usr/bin/env python3
"""
Fix Student Test Routes
Add missing student test routes
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def add_student_test_routes():
    """Add missing student test routes"""
    print("=== ADDING STUDENT TEST ROUTES ===")
    
    try:
        # Read current app.py
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find where to insert routes (after logout route)
        logout_route_pos = content.find("@app.route('/logout', methods=['GET', 'POST'])")
        if logout_route_pos == -1:
            print("Logout route not found!")
            return False
        
        # Find the end of logout route
        logout_end = content.find("\n\n", logout_route_pos)
        if logout_end == -1:
            logout_end = content.find("\n@", logout_route_pos)
        
        # Student test routes to add
        student_routes = '''

# Student Test Routes
@app.route('/student/tests', methods=['GET'])
@login_required
def student_tests():
    """Student tests page"""
    if session.get('is_admin', False):
        flash('Bu sahifa faqat o\\'quvchilar uchun', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    tests = Test.query.all()
    results = TestResult.query.filter_by(user_id=session.get('user_id')).all()
    
    return render_template('student_tests.html', tests=tests, results=results)

@app.route('/student/take_test/<int:test_id>', methods=['GET', 'POST'])
@login_required
def student_take_test(test_id):
    """Take a test"""
    if session.get('is_admin', False):
        flash('Bu sahifa faqat o\\'quvchilar uchun', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    test = Test.query.get_or_404(test_id)
    user_id = session.get('user_id')
    
    # Check if user already took this test
    existing_result = TestResult.query.filter_by(user_id=user_id, test_id=test_id).first()
    if existing_result:
        flash('Siz bu testni allaqachon topshirgansiz', 'info')
        return redirect(url_for('student_test_result', result_id=existing_result.id))
    
    if request.method == 'POST':
        # Process test submission
        score = 0
        total_questions = len(test.questions)
        
        for question in test.questions:
            selected_answer = request.form.get(f'question_{question.id}')
            if selected_answer == question.correct_answer:
                score += 1
        
        # Create test result
        result = TestResult(
            user_id=user_id,
            test_id=test_id,
            score=score,
            total_questions=total_questions,
            completed_at=datetime.utcnow()
        )
        db.session.add(result)
        db.session.commit()
        
        flash(f'Test muvaffaqiyatli yakunlandi! To\\'g\\'ri javoblar: {score}/{total_questions}', 'success')
        return redirect(url_for('student_test_result', result_id=result.id))
    
    return render_template('take_test.html', test=test)

@app.route('/student/test_result/<int:result_id>', methods=['GET'])
@login_required
def student_test_result(result_id):
    """View test result"""
    if session.get('is_admin', False):
        flash('Bu sahifa faqat o\\'quvchilar uchun', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    result = TestResult.query.get_or_404(result_id)
    
    # Check if result belongs to current user
    if result.user_id != session.get('user_id'):
        flash('Bu natijani ko\\'rishga huquqingiz yo\\'q', 'danger')
        return redirect(url_for('student_tests'))
    
    return render_template('test_result.html', result=result)

'''
        
        # Insert routes after logout route
        new_content = content[:logout_end] + student_routes + content[logout_end:]
        
        # Write back
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("Student test routes added!")
        return True
        
    except Exception as e:
        print(f"Error adding student test routes: {e}")
        return False

def fix_student_dashboard():
    """Fix student dashboard"""
    print("\n=== FIXING STUDENT DASHBOARD ===")
    
    try:
        # Read current app.py
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find student dashboard route
        dashboard_pos = content.find("@app.route('/student/dashboard', methods=['GET'])")
        if dashboard_pos == -1:
            print("Student dashboard route not found!")
            return False
        
        # Find the function
        function_start = content.find("def student_dashboard():", dashboard_pos)
        function_end = content.find("\n@", function_start)
        if function_end == -1:
            function_end = content.find("\n\n", function_start)
        
        # New dashboard function
        new_function = """def student_dashboard():
    \"\"\"Student dashboard\"\"\"
    if session.get('is_admin', False):
        flash('Bu sahifa faqat o\'quvchilar uchun', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    user_id = session.get('user_id')
    tests = Test.query.all()
    results = TestResult.query.filter_by(user_id=user_id).all()
    
    return render_template('student_dashboard.html', tests=tests, results=results)
"""
        
        # Replace the function
        new_content = content[:function_start] + new_function + content[function_end:]
        
        # Write back
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("Student dashboard fixed!")
        return True
        
    except Exception as e:
        print(f"Error fixing student dashboard: {e}")
        return False

def fix_imports():
    """Fix missing imports"""
    print("\n=== FIXING IMPORTS ===")
    
    try:
        # Read current app.py
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if datetime is imported
        if 'from datetime import datetime' not in content:
            # Find import section
            import_pos = content.find("from flask import")
            if import_pos != -1:
                import_end = content.find("\n", import_pos)
                new_import = content[:import_end] + "\nfrom datetime import datetime" + content[import_end:]
                
                # Write back
                with open('app.py', 'w', encoding='utf-8') as f:
                    f.write(new_import)
                
                print("Datetime import added!")
            else:
                print("Import section not found!")
                return False
        else:
            print("Datetime import already exists!")
        
        return True
        
    except Exception as e:
        print(f"Error fixing imports: {e}")
        return False

def test_fixed_routes():
    """Test fixed routes"""
    print("\n=== TESTING FIXED ROUTES ===")
    
    try:
        import app
        
        # Get all routes
        routes = list(app.app.url_map.iter_rules())
        
        # Check student test routes
        required_routes = [
            '/student/tests',
            '/student/take_test/<int:test_id>',
            '/student/test_result/<int:result_id>',
            '/student/dashboard'
        ]
        
        existing_routes = [route.rule for route in routes]
        
        print("Student test routes:")
        all_exist = True
        for route in required_routes:
            if route in existing_routes:
                print(f"  {route}: EXISTS")
            else:
                print(f"  {route}: MISSING")
                all_exist = False
        
        return all_exist
        
    except Exception as e:
        print(f"Test routes error: {e}")
        return False

def test_student_test_functionality():
    """Test student test functionality"""
    print("\n=== TESTING STUDENT TEST FUNCTIONALITY ===")
    
    try:
        import app
        
        with app.app.test_client() as client:
            # Test student login
            response = client.post('/login', data={
                'username': 'student1',
                'password': 'password1'
            }, follow_redirects=True)
            
            print(f"Student login: {response.status_code}")
            
            if response.status_code != 200:
                print("Student login failed!")
                return False
            
            # Test student tests page
            response = client.get('/student/tests')
            print(f"Student tests page: {response.status_code}")
            
            # Test student dashboard
            response = client.get('/student/dashboard')
            print(f"Student dashboard: {response.status_code}")
            
            # Get available tests
            with app.app.app_context():
                tests = app.Test.query.all()
                if tests:
                    test_id = tests[0].id
                    # Test take test page
                    response = client.get(f'/student/take_test/{test_id}')
                    print(f"Take test page: {response.status_code}")
            
            return True
            
    except Exception as e:
        print(f"Student test functionality error: {e}")
        return False

def main():
    """Main function"""
    print("STEP BY STEP EDUCATION PLATFORM - FIX STUDENT TEST ROUTES")
    print("Adding missing student test routes...")
    
    if fix_imports():
        if add_student_test_routes():
            if fix_student_dashboard():
                if test_fixed_routes():
                    if test_student_test_functionality():
                        print("\n=== STUDENT TEST ROUTES FIXED ===")
                        print("Testlar bo'limi to'liq ishlaydi!")
                        return True
                    else:
                        print("\nStudent test functionality test failed!")
                        return False
                else:
                    print("\nTest fixed routes failed!")
                    return False
            else:
                print("\nFix student dashboard failed!")
                return False
        else:
            print("\nAdd student test routes failed!")
            return False
    else:
        print("\nFix imports failed!")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
