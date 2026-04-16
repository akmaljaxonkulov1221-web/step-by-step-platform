# Production Deployment Guide

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
