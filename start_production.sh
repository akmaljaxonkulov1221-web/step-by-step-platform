#!/bin/bash
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
