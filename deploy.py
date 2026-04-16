#!/usr/bin/env python3
"""
Auto-deployment script for education platform
Prepares and deploys the platform to production
"""

import os
import sys
import subprocess
import requests
import json
from datetime import datetime

def check_requirements():
    """Check if all requirements are met"""
    print("=== CHECKING REQUIREMENTS ===")
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("ERROR: app.py not found. Please run from project root.")
        return False
    
    # Check if requirements.txt exists
    if not os.path.exists('requirements.txt'):
        print("ERROR: requirements.txt not found.")
        return False
    
    # Check if restore_data.py exists
    if not os.path.exists('restore_data.py'):
        print("ERROR: restore_data.py not found.")
        return False
    
    print("All requirements met!")
    return True

def run_data_restoration():
    """Run the data restoration script"""
    print("=== RUNNING DATA RESTORATION ===")
    
    try:
        result = subprocess.run([sys.executable, 'restore_data.py'], 
                              capture_output=True, text=True, cwd='.')
        
        if result.returncode == 0:
            print("Data restoration completed successfully!")
            print(result.stdout)
            return True
        else:
            print(f"Data restoration failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"Error running data restoration: {e}")
        return False

def create_deploy_info():
    """Create deployment information file"""
    print("=== CREATING DEPLOYMENT INFO ===")
    
    deploy_info = {
        'deployment_time': datetime.now().isoformat(),
        'version': '1.0.0',
        'features': [
            'Complete Admin Panel',
            'Student Dashboard', 
            'AI Assistant Integration',
            'Test System',
            'PDF Upload Management',
            'Subject Management',
            'Topic Management',
            'Real-time Updates',
            'Access Control',
            'Responsive Design'
        ],
        'database_status': 'clean_and_ready',
        'admin_credentials': {
            'username': 'admin',
            'password': 'admin123'
        },
        'default_data': {
            'subjects': 5,
            'groups': 5,
            'tests': 15,
            'questions': 45
        }
    }
    
    with open('deploy_info.json', 'w', encoding='utf-8') as f:
        json.dump(deploy_info, f, indent=2, ensure_ascii=False)
    
    print("Deployment info created!")
    return True

def create_startup_script():
    """Create startup script for production"""
    print("=== CREATING STARTUP SCRIPT ===")
    
    startup_script = '''#!/bin/bash
# Production startup script for Education Platform

echo "Starting Education Platform..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Run data restoration
python restore_data.py

# Start the application
echo "Starting application..."
export FLASK_ENV=production
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app
'''
    
    with open('start_production.sh', 'w', encoding='utf-8') as f:
        f.write(startup_script)
    
    # Make executable
    os.chmod('start_production.sh', 0o755)
    
    print("Startup script created!")
    return True

def create_windows_startup():
    """Create Windows startup script"""
    print("=== CREATING WINDOWS STARTUP SCRIPT ===")
    
    startup_script = '''@echo off
REM Production startup script for Education Platform

echo Starting Education Platform...

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\\Scripts\\activate.bat

REM Install requirements
pip install -r requirements.txt

REM Run data restoration
python restore_data.py

REM Start the application
echo Starting application...
set FLASK_ENV=production
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app

pause
'''
    
    with open('start_production.bat', 'w', encoding='utf-8') as f:
        f.write(startup_script)
    
    print("Windows startup script created!")
    return True

def create_docker_files():
    """Create Docker configuration files"""
    print("=== CREATING DOCKER FILES ===")
    
    # Dockerfile
    dockerfile = '''FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Run data restoration
RUN python restore_data.py

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Start the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"]
'''
    
    with open('Dockerfile', 'w', encoding='utf-8') as f:
        f.write(dockerfile)
    
    # docker-compose.yml
    docker_compose = '''version: '3.8'

services:
  education-platform:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=your-secret-key-here
    volumes:
      - ./uploads:/app/uploads
      - ./education_complete.db:/app/education_complete.db
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
'''
    
    with open('docker-compose.yml', 'w', encoding='utf-8') as f:
        f.write(docker_compose)
    
    print("Docker files created!")
    return True

def create_github_workflow():
    """Create GitHub Actions workflow for auto-deployment"""
    print("=== CREATING GITHUB WORKFLOW ===")
    
    workflow = '''name: Deploy to Production

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run data restoration
      run: python restore_data.py
    
    - name: Deploy to Render
      run: |
        curl -X POST "https://api.render.com/v1/services" \\
          -H "Authorization: Bearer ${{ secrets.RENDER_API_KEY }}" \\
          -H "Content-Type: application/json" \\
          -d '{
            "type": "web",
            "name": "education-platform",
            "repo": "https://github.com/your-username/education-platform",
            "branch": "main",
            "buildCommand": "pip install -r requirements.txt && python restore_data.py",
            "startCommand": "gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app",
            "envVars": [
              {"key": "FLASK_ENV", "value": "production"},
              {"key": "SECRET_KEY", "value": "${{ secrets.SECRET_KEY }}"}
            ]
          }'
'''
    
    os.makedirs('.github/workflows', exist_ok=True)
    with open('.github/workflows/deploy.yml', 'w', encoding='utf-8') as f:
        f.write(workflow)
    
    print("GitHub workflow created!")
    return True

def main():
    """Main deployment function"""
    print("=== AUTO-DEPLOYMENT SCRIPT ===")
    print("Preparing Education Platform for deployment...")
    print()
    
    # Check requirements
    if not check_requirements():
        print("Deployment failed: Requirements not met")
        return False
    
    # Run data restoration
    if not run_data_restoration():
        print("Deployment failed: Data restoration failed")
        return False
    
    # Create deployment files
    if not create_deploy_info():
        print("Deployment failed: Could not create deploy info")
        return False
    
    if not create_startup_script():
        print("Deployment failed: Could not create startup script")
        return False
    
    if not create_windows_startup():
        print("Deployment failed: Could not create Windows startup script")
        return False
    
    if not create_docker_files():
        print("Deployment failed: Could not create Docker files")
        return False
    
    if not create_github_workflow():
        print("Deployment failed: Could not create GitHub workflow")
        return False
    
    print()
    print("=== DEPLOYMENT PREPARATION COMPLETED! ===")
    print()
    print("Files created:")
    print("- deploy_info.json (deployment information)")
    print("- start_production.sh (Linux/Mac startup)")
    print("- start_production.bat (Windows startup)")
    print("- Dockerfile (Docker configuration)")
    print("- docker-compose.yml (Docker Compose)")
    print("- .github/workflows/deploy.yml (GitHub Actions)")
    print()
    print("Next steps:")
    print("1. Commit and push to GitHub")
    print("2. Set up Render.com service")
    print("3. Configure environment variables")
    print("4. Deploy!")
    print()
    print("Platform is ready for production deployment!")
    
    return True

if __name__ == '__main__':
    success = main()
    if success:
        print("\\n=== AUTO-DEPLOYMENT COMPLETED SUCCESSFULLY! ===")
        sys.exit(0)
    else:
        print("\\n=== AUTO-DEPLOYMENT FAILED! ===")
        sys.exit(1)
