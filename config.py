# Configuration file for Step by Step Education Platform
import os
from datetime import timedelta

class Config:
    """Base configuration"""
    
    # Basic Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'super-secret-key-for-sessions-to-work-step-by-step-platform')
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///education_complete.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', 'False').lower() == 'true'
    
    # Server configuration
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Application configuration
    APP_NAME = os.getenv('APP_NAME', 'Step by Step Education Platform')
    APP_VERSION = os.getenv('APP_VERSION', '1.0.0')
    APP_DESCRIPTION = os.getenv('APP_DESCRIPTION', 'Complete education platform with step-by-step development')
    
    # Security configuration
    SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', 3600))  # 1 hour
    PASSWORD_MIN_LENGTH = int(os.getenv('PASSWORD_MIN_LENGTH', 6))
    MAX_LOGIN_ATTEMPTS = int(os.getenv('MAX_LOGIN_ATTEMPTS', 5))
    
    # Email configuration
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@stepbystep.com')
    
    # Redis configuration (optional)
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Celery configuration (optional)
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    
    # File upload configuration
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    ALLOWED_EXTENSIONS = os.getenv('ALLOWED_EXTENSIONS', 'txt,pdf,png,jpg,jpeg,gif').split(',')
    
    # Pagination configuration
    ITEMS_PER_PAGE = int(os.getenv('ITEMS_PER_PAGE', 20))
    MAX_SEARCH_RESULTS = int(os.getenv('MAX_SEARCH_RESULTS', 100))
    
    # Cache configuration
    CACHE_TYPE = os.getenv('CACHE_TYPE', 'simple')
    CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_DEFAULT_TIMEOUT', 300))
    
    # Logging configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'app.log')
    LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES', 1024 * 1024))  # 1MB
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', 5))
    
    # API configuration
    API_VERSION = os.getenv('API_VERSION', 'v1')
    API_RATE_LIMIT = os.getenv('API_RATE_LIMIT', '100 per hour')
    
    # Maintenance configuration
    MAINTENANCE_MODE = os.getenv('MAINTENANCE_MODE', 'False').lower() == 'true'
    BACKUP_SCHEDULE = os.getenv('BACKUP_SCHEDULE', '0 2 * * *')  # Daily at 2 AM
    
    # Feature flags
    ENABLE_REGISTRATION = os.getenv('ENABLE_REGISTRATION', 'True').lower() == 'true'
    ENABLE_EMAIL_VERIFICATION = os.getenv('ENABLE_EMAIL_VERIFICATION', 'False').lower() == 'true'
    ENABLE_PASSWORD_RESET = os.getenv('ENABLE_PASSWORD_RESET', 'True').lower() == 'true'
    ENABLE_USER_PROFILES = os.getenv('ENABLE_USER_PROFILES', 'True').lower() == 'true'
    ENABLE_NOTIFICATIONS = os.getenv('ENABLE_NOTIFICATIONS', 'True').lower() == 'true'
    
    # Default admin configuration
    DEFAULT_ADMIN_USERNAME = os.getenv('DEFAULT_ADMIN_USERNAME', 'admin')
    DEFAULT_ADMIN_PASSWORD = os.getenv('DEFAULT_ADMIN_PASSWORD', 'admin123')
    DEFAULT_ADMIN_EMAIL = os.getenv('DEFAULT_ADMIN_EMAIL', 'admin@stepbystep.com')
    
    # Test configuration
    TESTING = os.getenv('TESTING', 'False').lower() == 'true'
    WTF_CSRF_ENABLED = os.getenv('WTF_CSRF_ENABLED', 'True').lower() == 'true'
    
    # Development configuration
    TEMPLATES_AUTO_RELOAD = os.getenv('TEMPLATES_AUTO_RELOAD', 'True').lower() == 'true'
    
    @staticmethod
    def init_app(app):
        """Initialize application with this configuration"""
        pass

class DevelopmentConfig(Config):
    """Development configuration"""
    
    DEBUG = True
    TEMPLATES_AUTO_RELOAD = True
    
    # Development database
    SQLALCHEMY_DATABASE_URI = os.getenv('DEV_DATABASE_URL', 'sqlite:///education_dev.db')
    
    # Development logging
    LOG_LEVEL = 'DEBUG'
    
    # Development features
    ENABLE_REGISTRATION = True
    ENABLE_EMAIL_VERIFICATION = False
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Development specific initialization
        import logging
        logging.basicConfig(level=logging.DEBUG)

class TestingConfig(Config):
    """Testing configuration"""
    
    TESTING = True
    DEBUG = True
    WTF_CSRF_ENABLED = False
    
    # Testing database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Testing settings
    ITEMS_PER_PAGE = 5
    SESSION_TIMEOUT = 60  # 1 minute for testing
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Testing specific initialization
        import logging
        logging.basicConfig(level=logging.CRITICAL)

class ProductionConfig(Config):
    """Production configuration"""
    
    DEBUG = False
    TEMPLATES_AUTO_RELOAD = False
    
    # Production database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///education_complete.db')
    
    # Production security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Production logging
    LOG_LEVEL = 'WARNING'
    
    # Production features
    ENABLE_EMAIL_VERIFICATION = True
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Production specific initialization
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not app.debug:
            file_handler = RotatingFileHandler(
                cls.LOG_FILE,
                maxBytes=cls.LOG_MAX_BYTES,
                backupCount=cls.LOG_BACKUP_COUNT
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            
            app.logger.setLevel(logging.INFO)
            app.logger.info('Step by Step Education Platform startup')

class StagingConfig(Config):
    """Staging configuration - similar to production but with debug enabled"""
    
    DEBUG = True
    
    # Staging database
    SQLALCHEMY_DATABASE_URI = os.getenv('STAGING_DATABASE_URL', 'sqlite:///education_staging.db')
    
    # Staging features
    ENABLE_EMAIL_VERIFICATION = False
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Staging specific initialization
        import logging
        logging.basicConfig(level=logging.INFO)

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'staging': StagingConfig,
    'default': DevelopmentConfig
}

def get_config(config_name=None):
    """Get configuration class by name"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'default')
    
    return config.get(config_name, config['default'])

# Environment-specific settings
def get_env_variable(var_name, default_value=None, cast_type=str):
    """Get environment variable with type casting"""
    value = os.getenv(var_name, default_value)
    
    if cast_type == bool:
        return value.lower() in ('true', '1', 'yes', 'on')
    elif cast_type == int:
        return int(value) if value else default_value
    elif cast_type == float:
        return float(value) if value else default_value
    elif cast_type == list:
        return value.split(',') if value else []
    else:
        return value

# Validation functions
def validate_config():
    """Validate configuration settings"""
    errors = []
    
    # Check required environment variables in production
    if os.getenv('FLASK_ENV') == 'production':
        required_vars = ['SECRET_KEY', 'DATABASE_URL']
        for var in required_vars:
            if not os.getenv(var):
                errors.append(f"Required environment variable {var} is missing")
    
    # Validate numeric values
    numeric_vars = {
        'PORT': (1, 65535),
        'SESSION_TIMEOUT': (60, 86400),
        'PASSWORD_MIN_LENGTH': (4, 128),
        'MAX_CONTENT_LENGTH': (1024, 1024*1024*100),  # 1KB to 100MB
        'ITEMS_PER_PAGE': (5, 100)
    }
    
    for var, (min_val, max_val) in numeric_vars.items():
        value = get_env_variable(var, cast_type=int)
        if value < min_val or value > max_val:
            errors.append(f"{var} must be between {min_val} and {max_val}")
    
    return errors
