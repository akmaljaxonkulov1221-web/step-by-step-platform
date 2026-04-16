# QADAM 9: Testing & Production Deployment

## MAQSAD:
Step by step platformini to'liq test qilish va production deploymentga tayyorlash

## QILINADIGAN ISHLAR:

### 1. Full Testing
- Unit testing
- Integration testing
- Performance testing
- Security testing

### 2. Production Optimization
- Code optimization
- Database optimization
- Caching setup
- Error handling

### 3. Deployment Preparation
- Environment configuration
- Backup systems
- Monitoring setup
- Documentation

## KOD:

### Testing Suite:

```python
import unittest
import requests
from app import app, db, User, Group

class TestEducationPlatform(unittest.TestCase):
    
    def setUp(self):
        """Test setup"""
        self.app = app.test_client()
        self.app.testing = True
        with app.app_context():
            db.create_all()
    
    def tearDown(self):
        """Test cleanup"""
        with app.app_context():
            db.drop_all()
    
    def test_homepage(self):
        """Test homepage loads"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Ta\'lim Platformasi', response.data)
    
    def test_login_page(self):
        """Test login page loads"""
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)
    
    def test_admin_login(self):
        """Test admin login"""
        # Create admin user
        with app.app_context():
            admin = User(
                username='admin',
                first_name='Admin',
                last_name='User',
                is_admin=True,
                is_group_leader=False
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
        
        # Test login
        response = self.app.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        
        self.assertIn(b'Login successful', response.data)
    
    def test_user_creation(self):
        """Test user creation"""
        response = self.app.post('/admin/users/create', data={
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'test123',
            'is_admin': 'on'
        }, follow_redirects=True)
        
        # Check if user was created
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            self.assertIsNotNone(user)
            self.assertEqual(user.first_name, 'Test')
    
    def test_group_creation(self):
        """Test group creation"""
        response = self.app.post('/admin/groups/create', data={
            'name': 'Test Group',
            'description': 'Test group description'
        }, follow_redirects=True)
        
        # Check if group was created
        with app.app_context():
            group = Group.query.filter_by(name='Test Group').first()
            self.assertIsNotNone(group)
            self.assertEqual(group.description, 'Test group description')

if __name__ == '__main__':
    unittest.main()
```

### Performance Monitoring:

```python
import time
import psutil
from functools import wraps

def monitor_performance(func):
    """Performance monitoring decorator"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss
        
        result = func(*args, **kwargs)
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss
        
        execution_time = end_time - start_time
        memory_used = end_memory - start_memory
        
        print(f"Function {func.__name__}:")
        print(f"  Execution time: {execution_time:.4f} seconds")
        print(f"  Memory used: {memory_used / 1024:.2f} KB")
        
        return result
    return wrapper

# Apply to critical routes
@app.route('/admin_dashboard')
@monitor_performance
def admin_dashboard():
    # ... existing code ...
    pass

@app.route('/admin/users')
@monitor_performance
def admin_users():
    # ... existing code ...
    pass
```

### Error Handling & Logging:

```python
import logging
from datetime import datetime
import traceback

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@app.errorhandler(404)
def not_found_error(error):
    logger.error(f"404 Error: {error}")
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 Error: {error}")
    logger.error(traceback.format_exc())
    db.session.rollback()
    return render_template('500.html'), 500

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {e}")
    logger.error(traceback.format_exc())
    return render_template('500.html'), 500

# Add logging to critical operations
@app.route('/admin/users/create', methods=['POST'])
def admin_create_user():
    try:
        logger.info(f"User creation attempt: {request.form.get('username')}")
        # ... existing code ...
        logger.info(f"User created successfully: {username}")
        return redirect(url_for('admin_users'))
    except Exception as e:
        logger.error(f"User creation failed: {e}")
        logger.error(traceback.format_exc())
        flash("User creation failed!", "error")
        return redirect(url_for('admin_users'))
```

### Backup System:

```python
import shutil
import json
from datetime import datetime

def backup_database():
    """Create database backup"""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = f'backups/education_complete_{timestamp}.db'
        
        # Create backups directory if it doesn't exist
        os.makedirs('backups', exist_ok=True)
        
        # Copy database file
        shutil.copy2('education_complete.db', backup_path)
        
        # Log backup
        logger.info(f"Database backup created: {backup_path}")
        
        # Keep only last 10 backups
        backups = sorted([f for f in os.listdir('backups') if f.endswith('.db')])
        if len(backups) > 10:
            for old_backup in backups[:-10]:
                os.remove(f'backups/{old_backup}')
                logger.info(f"Old backup removed: {old_backup}")
        
        return True
    except Exception as e:
        logger.error(f"Backup failed: {e}")
        return False

def export_data():
    """Export data to JSON"""
    try:
        data = {
            'users': [],
            'groups': [],
            'subjects': [],
            'export_date': datetime.now().isoformat()
        }
        
        # Export users
        for user in User.query.all():
            data['users'].append({
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_admin': user.is_admin,
                'is_group_leader': user.is_group_leader,
                'group_id': user.group_id
            })
        
        # Export groups
        for group in Group.query.all():
            data['groups'].append({
                'name': group.name,
                'description': group.description
            })
        
        # Save to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        export_path = f'exports/data_export_{timestamp}.json'
        os.makedirs('exports', exist_ok=True)
        
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Data exported: {export_path}")
        return export_path
    except Exception as e:
        logger.error(f"Export failed: {e}")
        return None
```

### Production Configuration:

```python
# Production settings
if os.getenv('FLASK_ENV') == 'production':
    # Disable debug mode
    app.debug = False
    
    # Security settings
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    # Rate limiting
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    
    limiter = Limiter(
        app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"]
    )
    
    @app.before_request
    def before_request():
        # Log all requests
        logger.info(f"Request: {request.method} {request.url} from {request.remote_addr}")
    
    @app.after_request
    def after_request(response):
        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response
```

### Health Check:

```python
@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        db.session.execute('SELECT 1')
        
        # Check basic functionality
        user_count = User.query.count()
        group_count = Group.query.count()
        
        health_data = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'database': 'connected',
            'users': user_count,
            'groups': group_count,
            'version': '1.0.0'
        }
        
        return health_data, 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {'status': 'unhealthy', 'error': str(e)}, 500

@app.route('/metrics')
def metrics():
    """Metrics endpoint for monitoring"""
    try:
        import psutil
        
        metrics_data = {
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'active_connections': len(db.session.registry()),
            'total_users': User.query.count(),
            'total_groups': Group.query.count()
        }
        
        return metrics_data, 200
    except Exception as e:
        logger.error(f"Metrics failed: {e}")
        return {'error': str(e)}, 500
```

## DEPLOYMENT CHECKLIST:

### Pre-deployment:
- [ ] All tests pass
- [ ] Database backup created
- [ ] Environment variables configured
- [ ] Security settings applied
- [ ] Performance monitoring enabled

### Production Deployment:
- [ ] Code deployed to production
- [ ] Database migrations run
- [ ] Health checks passing
- [ ] Monitoring active
- [ ] Backup systems working

### Post-deployment:
- [ ] Load testing performed
- [ ] Security audit completed
- [ ] Performance benchmarks set
- [ ] Monitoring alerts configured
- [ ] Documentation updated

## TESTING COMMANDS:

```bash
# Run unit tests
python -m pytest tests/

# Run performance tests
python performance_test.py

# Run security scan
python security_scan.py

# Check health
curl https://your-domain.com/health

# View metrics
curl https://your-domain.com/metrics
```

## NATIJA:
- Full test coverage
- Production ready
- Monitoring enabled
- Backup systems active
- Security hardened

## STATUS:
- [ ] Unit tests written
- [ ] Performance monitoring added
- [ ] Error handling improved
- [ ] Backup system created
- [ ] Production config ready
- [ ] Health checks added
- [ ] Security features enabled

## SERVER STATUS:
- [x] Server ishlaydi
- [x] Login ishlaydi
- [x] Admin dashboard ishlaydi
- [x] User management ishlaydi
- [ ] Testing complete
- [ ] Production deployment ready

## KEYINGI QADAM:
QADAM 10: Final Launch & Maintenance
