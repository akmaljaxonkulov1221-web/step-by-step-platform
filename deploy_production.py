#!/usr/bin/env python3
"""
Production deployment script for education platform
Final deployment with all features ready
"""

import os
import sys
import subprocess
import json
from datetime import datetime

def create_production_files():
    """Create all necessary files for production deployment"""
    
    print("=== CREATING PRODUCTION DEPLOYMENT FILES ===")
    
    # 1. Create render.yaml for Render.com
    render_yaml = """services:
  # Web Service
  - type: web
    name: education-platform
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt && python restore_full_previous_state.py
    startCommand: gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app
    autoDeploy: true
    
    # Environment variables
    envVars:
      - key: FLASK_ENV
        value: production
      - key: SECRET_KEY
        generateValue: true
      - key: PYTHON_VERSION
        value: 3.9.0
    
    # Health check
    healthCheckPath: /health
    
    # Disk space for uploads and database
    disk:
      name: education-platform-disk
      mountPath: /app
      sizeGB: 10

# Addons for database
databases:
  - name: education-platform-db
    databaseName: education_platform
    user: education_platform_user
    plan: free
"""
    
    with open('render.yaml', 'w', encoding='utf-8') as f:
        f.write(render_yaml)
    
    print("render.yaml created!")
    
    # 2. Create Dockerfile for Docker deployment
    dockerfile = """FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads

# Run data restoration
RUN python restore_full_previous_state.py

# Create health check endpoint
RUN echo "from flask import Flask, jsonify\\napp = Flask(__name__)\\n@app.route('/health')\\ndef health():\\n    return jsonify({'status': 'healthy', 'timestamp': '2024-04-16'})\\nif __name__ == '__main__':\\n    app.run(host='0.0.0.0', port=5000)" > health_check.py

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \\
    CMD curl -f http://localhost:5000/health || exit 1

# Start the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"]
"""
    
    with open('Dockerfile', 'w', encoding='utf-8') as f:
        f.write(dockerfile)
    
    print("Dockerfile created!")
    
    # 3. Create docker-compose.yml for local development
    docker_compose = """version: '3.8'

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

  # Optional: Add nginx for reverse proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - education-platform
    restart: unless-stopped
"""
    
    with open('docker-compose.yml', 'w', encoding='utf-8') as f:
        f.write(docker_compose)
    
    print("docker-compose.yml created!")
    
    # 4. Create nginx.conf for reverse proxy
    nginx_conf = """events {
    worker_connections 1024;
}

http {
    upstream education_platform {
        server education-platform:5000;
    }

    server {
        listen 80;
        server_name localhost;

        location / {
            proxy_pass http://education_platform;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /uploads/ {
            proxy_pass http://education_platform;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /health {
            proxy_pass http://education_platform;
            access_log off;
        }
    }
}
"""
    
    with open('nginx.conf', 'w', encoding='utf-8') as f:
        f.write(nginx_conf)
    
    print("nginx.conf created!")
    
    # 5. Create .dockerignore
    dockerignore = """__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis
.DS_Store
.vscode
.idea
*.swp
*.swo
*~
"""
    
    with open('.dockerignore', 'w', encoding='utf-8') as f:
        f.write(dockerignore)
    
    print(".dockerignore created!")
    
    # 6. Create production startup script
    startup_script = """#!/bin/bash
# Production startup script for Education Platform

echo "Starting Education Platform in Production Mode..."

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
echo "Restoring database data..."
python restore_full_previous_state.py

# Set environment variables
export FLASK_ENV=production
export SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')

# Start the application
echo "Starting application..."
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app
"""
    
    with open('start_production.sh', 'w', encoding='utf-8') as f:
        f.write(startup_script)
    
    os.chmod('start_production.sh', 0o755)
    print("start_production.sh created!")
    
    # 7. Create Windows startup script
    windows_startup = """@echo off
REM Production startup script for Education Platform (Windows)

echo Starting Education Platform in Production Mode...

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
echo Restoring database data...
python restore_full_previous_state.py

REM Set environment variables
set FLASK_ENV=production
for /f "tokens=*" %%i in ('python -c "import secrets; print(secrets.token_hex(32))"') do set SECRET_KEY=%%i

REM Start the application
echo Starting application...
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app

pause
"""
    
    with open('start_production.bat', 'w', encoding='utf-8') as f:
        f.write(windows_startup)
    
    print("start_production.bat created!")
    
    # 8. Create production deployment guide
    deployment_guide = """# Production Deployment Guide

## Quick Deploy Options

### 1. Render.com (Recommended)
1. Push code to GitHub
2. Connect Render.com to your GitHub repository
3. Use `render.yaml` configuration
4. Deploy automatically

### 2. Docker Deployment
```bash
# Build and run
docker-compose up --build

# Background mode
docker-compose up -d

# View logs
docker-compose logs -f
```

### 3. Manual Deployment
```bash
# Linux/Mac
chmod +x start_production.sh
./start_production.sh

# Windows
start_production.bat
```

## Environment Variables
- `FLASK_ENV=production`
- `SECRET_KEY=your-secret-key`
- `PYTHONPATH=/app`

## Health Check
- Endpoint: `/health`
- Returns: `{"status": "healthy", "timestamp": "..."}`

## Database
- SQLite database: `education_complete.db`
- Auto-created on first run
- Data restoration: `restore_full_previous_state.py`

## File Structure
```
step-by-step/
|-- app.py                    # Main application
|-- requirements.txt          # Dependencies
|-- restore_full_previous_state.py  # Data restoration
|-- render.yaml              # Render.com config
|-- Dockerfile               # Docker config
|-- docker-compose.yml       # Docker Compose
|-- nginx.conf               # Nginx config
|-- start_production.sh      # Linux/Mac startup
|-- start_production.bat     # Windows startup
|-- uploads/                 # File uploads
|-- education_complete.db   # SQLite database
```

## Features Ready
- Complete Admin Panel
- Student Dashboard
- AI Assistant Integration
- 7-day Test Schedule
- 90-question Tests
- DTM Tests
- 8 Groups (101-108)
- PDF Upload Management
- Topic Management
- Real-time Updates

## Admin Credentials
- Username: `admin`
- Password: `admin123`

## Support
- Health check endpoint available
- Comprehensive logging
- Error handling
- Automatic data restoration
"""
    
    with open('PRODUCTION_DEPLOYMENT.md', 'w', encoding='utf-8') as f:
        f.write(deployment_guide)
    
    print("PRODUCTION_DEPLOYMENT.md created!")
    
    return True

def create_github_actions():
    """Create GitHub Actions workflow for CI/CD"""
    
    print("=== CREATING GITHUB ACTIONS WORKFLOW ===")
    
    workflow = """name: Deploy to Production

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  test:
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
      run: python restore_full_previous_state.py
    
    - name: Test application
      run: |
        python -c "import app; print('Application test passed')"

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Deploy to Render
      run: |
        curl -X POST "https://api.render.com/v1/services" \\
          -H "Authorization: Bearer ${{ secrets.RENDER_API_KEY }}" \\
          -H "Content-Type: application/json" \\
          -d @render.yaml
"""
    
    os.makedirs('.github/workflows', exist_ok=True)
    with open('.github/workflows/deploy.yml', 'w', encoding='utf-8') as f:
        f.write(workflow)
    
    print(".github/workflows/deploy.yml created!")
    
    return True

def main():
    """Main deployment function"""
    
    print("=== PRODUCTION DEPLOYMENT PREPARATION ===")
    print("Preparing Education Platform for production deployment...")
    print()
    
    # Create production files
    if not create_production_files():
        print("Deployment failed: Could not create production files")
        return False
    
    # Create GitHub Actions
    if not create_github_actions():
        print("Deployment failed: Could not create GitHub Actions")
        return False
    
    print()
    print("=== PRODUCTION DEPLOYMENT PREPARATION COMPLETED! ===")
    print()
    print("Files created for deployment:")
    print("1. render.yaml - Render.com configuration")
    print("2. Dockerfile - Docker configuration")
    print("3. docker-compose.yml - Docker Compose")
    print("4. nginx.conf - Nginx reverse proxy")
    print("5. start_production.sh - Linux/Mac startup")
    print("6. start_production.bat - Windows startup")
    print("7. PRODUCTION_DEPLOYMENT.md - Deployment guide")
    print("8. .github/workflows/deploy.yml - GitHub Actions")
    print()
    print("Deployment options:")
    print("1. Render.com - Easiest (render.yaml)")
    print("2. Docker - docker-compose up")
    print("3. Manual - start_production.sh/.bat")
    print("4. GitHub Actions - CI/CD")
    print()
    print("Platform features ready:")
    print("- Complete Admin Panel")
    print("- Student Dashboard")
    print("- 7-day Test Schedule")
    print("- 90-question Tests")
    print("- DTM Tests")
    print("- 8 Groups (101-108)")
    print("- PDF Upload Management")
    print("- AI Assistant Integration")
    print("- Real-time Updates")
    print()
    print("Next steps:")
    print("1. Commit and push to GitHub")
    print("2. Choose deployment method")
    print("3. Configure environment variables")
    print("4. Deploy!")
    print()
    print("Platform is ready for production deployment!")
    
    return True

if __name__ == '__main__':
    success = main()
    if success:
        print("\\n=== PRODUCTION DEPLOYMENT PREPARATION COMPLETED! ===")
        sys.exit(0)
    else:
        print("\\n=== PRODUCTION DEPLOYMENT PREPARATION FAILED! ===")
        sys.exit(1)
