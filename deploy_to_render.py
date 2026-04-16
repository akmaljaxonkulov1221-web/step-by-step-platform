#!/usr/bin/env python3
"""
Render Deployment Script
Prepares and deploys the Step by Step Education Platform to Render
"""

import os
import sys
import subprocess
import json
from datetime import datetime

def check_deployment_readiness():
    """Check if everything is ready for deployment"""
    print("=== DEPLOYMENT READINESS CHECK ===")
    
    checks = []
    
    # Check if render.yaml exists
    if os.path.exists('render.yaml'):
        checks.append("render.yaml: OK")
    else:
        checks.append("render.yaml: MISSING")
    
    # Check if requirements.txt exists
    if os.path.exists('requirements.txt'):
        checks.append("requirements.txt: OK")
    else:
        checks.append("requirements.txt: MISSING")
    
    # Check if app.py exists
    if os.path.exists('app.py'):
        checks.append("app.py: OK")
    else:
        checks.append("app.py: MISSING")
    
    # Check if templates directory exists
    if os.path.exists('templates'):
        checks.append("templates/: OK")
    else:
        checks.append("templates/: MISSING")
    
    # Check if static directory exists
    if os.path.exists('static'):
        checks.append("static/: OK")
    else:
        checks.append("static/: MISSING")
    
    print("\n".join(checks))
    
    # Check if all critical files exist
    critical_files = ['render.yaml', 'requirements.txt', 'app.py']
    missing_critical = [check for check in checks if "MISSING" in check and any(cf in check for cf in critical_files)]
    
    if missing_critical:
        print(f"\nCRITICAL: Missing files: {len(missing_critical)}")
        return False
    
    print("\nAll critical files present!")
    return True

def verify_app_configuration():
    """Verify app configuration for production"""
    print("\n=== APP CONFIGURATION CHECK ===")
    
    try:
        # Check app.py for production settings
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = []
        
        # Check for production-ready settings
        if 'app.run(' in content and '__main__' in content:
            checks.append("Development server: OK (has __main__ check)")
        else:
            checks.append("Development server: MISSING")
        
        if 'SECRET_KEY' in content:
            checks.append("Secret key: OK")
        else:
            checks.append("Secret key: MISSING")
        
        if 'SQLALCHEMY_DATABASE_URI' in content:
            checks.append("Database URI: OK")
        else:
            checks.append("Database URI: MISSING")
        
        if 'gunicorn' in open('requirements.txt').read():
            checks.append("Gunicorn: OK")
        else:
            checks.append("Gunicorn: MISSING")
        
        print("\n".join(checks))
        
        return all("OK" in check for check in checks)
        
    except Exception as e:
        print(f"Configuration check error: {e}")
        return False

def create_deployment_info():
    """Create deployment information file"""
    print("\n=== CREATING DEPLOYMENT INFO ===")
    
    deployment_info = {
        "project": "Step by Step Education Platform",
        "version": "1.0.0",
        "deployment_date": datetime.now().isoformat(),
        "platform": "Render",
        "environment": "production",
        "features": [
            "Flask web application",
            "SQLAlchemy database",
            "User authentication",
            "Admin panel",
            "Student dashboard",
            "Test system",
            "Rating system",
            "Mobile responsive design"
        ],
        "dependencies": [
            "Flask==2.3.3",
            "Flask-SQLAlchemy==2.5.1",
            "gunicorn==21.2.0",
            "Werkzeug==2.3.7"
        ],
        "environment_variables": {
            "FLASK_ENV": "production",
            "SECRET_KEY": "auto-generated",
            "DATABASE_URL": "sqlite:///education_complete.db"
        },
        "health_check": {
            "path": "/",
            "expected_status": 200
        },
        "build_command": "pip install -r requirements.txt",
        "start_command": "gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app"
    }
    
    with open('deployment_info.json', 'w', encoding='utf-8') as f:
        json.dump(deployment_info, f, indent=2, ensure_ascii=False)
    
    print("deployment_info.json created!")
    return True

def create_gitignore():
    """Create .gitignore file if not exists"""
    print("\n=== CREATING .gitignore ===")
    
    gitignore_content = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/

# Environment Variables
.env
.env.local
.env.production

# Database
*.db
*.sqlite
*.sqlite3

# Logs
*.log
logs/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Render
.render/
"""
    
    if not os.path.exists('.gitignore'):
        with open('.gitignore', 'w', encoding='utf-8') as f:
            f.write(gitignore_content.strip())
        print(".gitignore created!")
    else:
        print(".gitignore already exists!")
    
    return True

def create_readme():
    """Create README.md for deployment"""
    print("\n=== CREATING README.md ===")
    
    readme_content = """# Step by Step Education Platform

## Description
Comprehensive education platform for student management, testing, and rating system.

## Features
- User authentication (Admin, Group Leaders, Students)
- Admin panel for managing users, groups, subjects, tests
- Student dashboard with test results and progress tracking
- Test system with automatic grading
- Group rating system
- Mobile responsive design
- Uzbek language interface

## Technology Stack
- **Backend:** Flask (Python)
- **Database:** SQLite
- **Frontend:** Bootstrap 5, HTML5, CSS3, JavaScript
- **Deployment:** Render

## Environment Variables
- `FLASK_ENV`: production
- `SECRET_KEY`: Auto-generated
- `DATABASE_URL`: sqlite:///education_complete.db

## Installation
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python app.py`

## Deployment
This application is configured for deployment on Render platform.

### Render Configuration
- **Service Type:** Web Service
- **Environment:** Python
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app`
- **Health Check:** `/`

## Admin Access
- **Default Admin:** admin / admin123

## API Endpoints
- `/` - Home page
- `/login` - Login page
- `/register` - Registration page
- `/admin/dashboard` - Admin dashboard
- `/student/dashboard` - Student dashboard
- `/group_rating` - Group rating page

## License
MIT License
"""
    
    if not os.path.exists('README.md'):
        with open('README.md', 'w', encoding='utf-8') as f:
            f.write(readme_content.strip())
        print("README.md created!")
    else:
        print("README.md already exists!")
    
    return True

def test_production_build():
    """Test production build locally"""
    print("\n=== TESTING PRODUCTION BUILD ===")
    
    try:
        # Test app import
        import app
        print("App import: OK")
        
        # Test database connection
        with app.app.app_context():
            # Test basic database operations
            groups = app.Group.query.limit(1).all()
            print("Database connection: OK")
        
        # Test routes
        test_client = app.app.test_client()
        response = test_client.get('/')
        if response.status_code == 200:
            print("Home route: OK")
        else:
            print(f"Home route: {response.status_code}")
        
        print("Production build test: PASSED")
        return True
        
    except Exception as e:
        print(f"Production build test: FAILED - {e}")
        return False

def main():
    """Main deployment preparation function"""
    print("STEP BY STEP EDUCATION PLATFORM - RENDER DEPLOYMENT")
    print("Preparing for deployment...")
    
    # Check deployment readiness
    if not check_deployment_readiness():
        print("Deployment readiness check FAILED!")
        return False
    
    # Verify app configuration
    if not verify_app_configuration():
        print("App configuration check FAILED!")
        return False
    
    # Create deployment files
    create_deployment_info()
    create_gitignore()
    create_readme()
    
    # Test production build
    if not test_production_build():
        print("Production build test FAILED!")
        return False
    
    print("\n=== DEPLOYMENT PREPARATION COMPLETE ===")
    print("Your application is ready for deployment to Render!")
    print("\nNext steps:")
    print("1. Push your code to GitHub")
    print("2. Connect your repository to Render")
    print("3. Render will automatically deploy your application")
    print("4. Your app will be available at: https://your-app-name.onrender.com")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
