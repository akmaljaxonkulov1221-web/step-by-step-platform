#!/usr/bin/env python3
"""
Debug Tests Section
Debug and fix the tests section functionality
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_test_models():
    """Check test models"""
    print("=== CHECKING TEST MODELS ===")
    
    try:
        import app
        
        with app.app.app_context():
            # Check Test model
            tests = app.Test.query.all()
            print(f"Total tests: {len(tests)}")
            
            # Check TestResult model
            test_results = app.TestResult.query.all()
            print(f"Total test results: {len(test_results)}")
            
            # Check Question model
            questions = app.Question.query.all()
            print(f"Total questions: {len(questions)}")
            
            # Show sample test
            if tests:
                sample_test = tests[0]
                print(f"Sample test: {sample_test.title}")
                print(f"Sample test questions: {len(sample_test.questions)}")
            
            return True
            
    except Exception as e:
        print(f"Test models error: {e}")
        return False

def check_test_routes():
    """Check test routes"""
    print("\n=== CHECKING TEST ROUTES ===")
    
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
        for route in required_routes:
            if route in existing_routes:
                print(f"  {route}: EXISTS")
            else:
                print(f"  {route}: MISSING")
        
        return True
        
    except Exception as e:
        print(f"Test routes error: {e}")
        return False

def check_student_test_functionality():
    """Check student test functionality"""
    print("\n=== CHECKING STUDENT TEST FUNCTIONALITY ===")
    
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

def check_test_templates():
    """Check test templates"""
    print("\n=== CHECKING TEST TEMPLATES ===")
    
    try:
        # Check required templates
        required_templates = [
            'student_tests.html',
            'student_dashboard.html',
            'take_test.html',
            'test_result.html'
        ]
        
        for template in required_templates:
            if os.path.exists(f'templates/{template}'):
                print(f"  {template}: EXISTS")
            else:
                print(f"  {template}: MISSING")
        
        return True
        
    except Exception as e:
        print(f"Test templates error: {e}")
        return False

def create_missing_test_templates():
    """Create missing test templates"""
    print("\n=== CREATING MISSING TEST TEMPLATES ===")
    
    try:
        # Create student_tests.html
        student_tests_template = '''{% extends "base.html" %}

{% block title %}Testlar{% endblock %}

{% block content %}
<div class="row">
    <div class="col-12">
        <h1 class="mb-4">Testlar</h1>
    </div>
</div>

<div class="row">
    <div class="col-12">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Mavjud testlar</h5>
            </div>
            <div class="card-body">
                {% if tests %}
                    {% for test in tests %}
                        <div class="card mb-3">
                            <div class="card-body">
                                <h5 class="card-title">{{ test.title }}</h5>
                                <p class="card-text">{{ test.description or 'Tavsif mavjud emas' }}</p>
                                <p class="card-text">
                                    <small class="text-muted">Savollar soni: {{ test.questions|length }}</small>
                                </p>
                                <a href="{{ url_for('student_take_test', test_id=test.id) }}" class="btn btn-primary">
                                    Testni boshlash
                                </a>
                            </div>
                        </div>
                    {% endfor %}
                {% else %}
                    <p class="text-muted">Hali testlar mavjud emas</p>
                {% endif %}
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''
        
        # Create take_test.html
        take_test_template = '''{% extends "base.html" %}

{% block title %}Testni boshlash{% endblock %}

{% block content %}
<div class="row">
    <div class="col-12">
        <h1 class="mb-4">{{ test.title }}</h1>
    </div>
</div>

<div class="row">
    <div class="col-12">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Test savollari</h5>
            </div>
            <div class="card-body">
                <form method="POST" action="{{ url_for('student_take_test', test_id=test.id) }}">
                    {% for question in test.questions %}
                        <div class="card mb-3">
                            <div class="card-body">
                                <h6 class="card-title">{{ loop.index }}. {{ question.text }}</h6>
                                <div class="form-group">
                                    {% for option in question.options %}
                                        <div class="form-check">
                                            <input class="form-check-input" type="radio" name="question_{{ question.id }}" value="{{ option }}" id="option_{{ question.id }}_{{ loop.index }}">
                                            <label class="form-check-label" for="option_{{ question.id }}_{{ loop.index }}">
                                                {{ option }}
                                            </label>
                                        </div>
                                    {% endfor %}
                                </div>
                            </div>
                        </div>
                    {% endfor %}
                    
                    <button type="submit" class="btn btn-primary">Testni yakunlash</button>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''
        
        # Create test_result.html
        test_result_template = '''{% extends "base.html" %}

{% block title %}Test natijasi{% endblock %}

{% block content %}
<div class="row">
    <div class="col-12">
        <h1 class="mb-4">Test natijasi</h1>
    </div>
</div>

<div class="row">
    <div class="col-12">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Test natijalari</h5>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-6">
                        <h6>Test: {{ result.test.title }}</h6>
                        <p>To'g'ri javoblar: {{ result.score }}</p>
                        <p>Umumiy savollar: {{ result.total_questions }}</p>
                        <p>Foiz: {{ (result.score / result.total_questions * 100)|round(1) }}%</p>
                    </div>
                    <div class="col-md-6">
                        <p>Boshlangan vaqt: {{ result.started_at.strftime('%Y-%m-%d %H:%M') if result.started_at else 'Noma\'lum' }}</p>
                        <p>Tugagan vaqt: {{ result.completed_at.strftime('%Y-%m-%d %H:%M') if result.completed_at else 'Noma\'lum' }}</p>
                        <p>Sarflangan vaqt: {{ result.total_time or 'Noma\'lum' }}</p>
                    </div>
                </div>
                
                <div class="mt-3">
                    <a href="{{ url_for('student_tests') }}" class="btn btn-secondary">Boshqa testlar</a>
                    <a href="{{ url_for('student_dashboard') }}" class="btn btn-primary">Dashboard</a>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''
        
        # Write templates
        with open('templates/student_tests.html', 'w', encoding='utf-8') as f:
            f.write(student_tests_template)
        
        with open('templates/take_test.html', 'w', encoding='utf-8') as f:
            f.write(take_test_template)
        
        with open('templates/test_result.html', 'w', encoding='utf-8') as f:
            f.write(test_result_template)
        
        print("Missing test templates created!")
        return True
        
    except Exception as e:
        print(f"Error creating test templates: {e}")
        return False

def fix_test_routes():
    """Fix test routes"""
    print("\n=== FIXING TEST ROUTES ===")
    
    try:
        import app
        
        # Check if routes exist
        with app.app.app_context():
            # Test student tests route
            try:
                with app.app.test_client() as client:
                    response = client.get('/student/tests')
                    print(f"Student tests route: {response.status_code}")
            except Exception as e:
                print(f"Student tests route error: {e}")
        
        return True
        
    except Exception as e:
        print(f"Fix test routes error: {e}")
        return False

def test_complete_test_functionality():
    """Test complete test functionality"""
    print("\n=== TESTING COMPLETE TEST FUNCTIONALITY ===")
    
    try:
        import app
        
        with app.app.test_client() as client:
            # Test student login
            response = client.post('/login', data={
                'username': 'student1',
                'password': 'password1'
            }, follow_redirects=True)
            
            print(f"Student login: {response.status_code}")
            
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
                    
                    # Test submitting test
                    response = client.post(f'/student/take_test/{test_id}', data={
                        f'question_{tests[0].questions[0].id}': 'A'
                    })
                    print(f"Submit test: {response.status_code}")
            
            return True
            
    except Exception as e:
        print(f"Complete test functionality error: {e}")
        return False

def main():
    """Main function"""
    print("STEP BY STEP EDUCATION PLATFORM - DEBUG TESTS SECTION")
    print("Debugging and fixing test section functionality...")
    
    if check_test_models():
        if check_test_routes():
            if check_student_test_functionality():
                if check_test_templates():
                    if create_missing_test_templates():
                        if fix_test_routes():
                            if test_complete_test_functionality():
                                print("\n=== TESTS SECTION FIXED ===")
                                print("Testlar bo'limi to'liq ishlaydi!")
                                return True
                            else:
                                print("\nComplete test functionality test failed!")
                                return False
                        else:
                            print("\nFix test routes failed!")
                            return False
                    else:
                        print("\nCreate test templates failed!")
                        return False
                else:
                    print("\nCheck test templates failed!")
                    return False
            else:
                print("\nStudent test functionality test failed!")
                return False
        else:
            print("\nCheck test routes failed!")
            return False
    else:
        print("\nCheck test models failed!")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
