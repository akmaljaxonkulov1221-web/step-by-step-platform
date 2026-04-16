#!/usr/bin/env python3
"""
Add Student Dashboard Route
Add missing student_dashboard route
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def add_student_dashboard_route():
    """Add missing student_dashboard route"""
    print("=== ADDING STUDENT DASHBOARD ROUTE ===")
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find where to insert the route (before the last route)
        last_route_pos = content.rfind('@app.route')
        if last_route_pos == -1:
            print("No routes found!")
            return False
        
        # Create the student dashboard route
        student_dashboard_code = '''@app.route('/student/dashboard')
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
        
        # Insert the route
        content = content[:last_route_pos] + student_dashboard_code + '\n' + content[last_route_pos:]
        
        # Write back
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("Student dashboard route added successfully!")
        return True
        
    except Exception as e:
        print(f"Error adding student dashboard route: {e}")
        return False

def test_student_dashboard_route():
    """Test if student dashboard route exists"""
    print("\n=== TESTING STUDENT DASHBOARD ROUTE ===")
    
    try:
        import app
        
        # Check if route exists
        routes = list(app.app.url_map.iter_rules())
        route_rules = [route.rule for route in routes]
        
        if '/student/dashboard' in route_rules:
            print("Student dashboard route: EXISTS")
            return True
        else:
            print("Student dashboard route: MISSING")
            return False
            
    except Exception as e:
        print(f"Error testing student dashboard route: {e}")
        return False

def main():
    """Main function"""
    print("STEP BY STEP EDUCATION PLATFORM - ADD STUDENT DASHBOARD")
    print("Adding missing student dashboard route...")
    
    if add_student_dashboard_route():
        if test_student_dashboard_route():
            print("\n=== STUDENT DASHBOARD ADDED SUCCESSFULLY ===")
            return True
        else:
            print("\nStudent dashboard test failed!")
            return False
    else:
        print("\nFailed to add student dashboard!")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
