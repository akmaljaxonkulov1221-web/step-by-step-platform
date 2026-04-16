@echo off
REM Production startup script for Education Platform (Windows)

echo Starting Education Platform in Production Mode...

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

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
