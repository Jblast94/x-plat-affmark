import os
from datetime import timedelta

class Config:
    """Base configuration class."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///affiliate_marketing.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # X API Configuration
    X_API_KEY = os.environ.get('X_API_KEY')
    X_API_SECRET = os.environ.get('X_API_SECRET')
    X_ACCESS_TOKEN = os.environ.get('X_ACCESS_TOKEN')
    X_ACCESS_TOKEN_SECRET = os.environ.get('X_ACCESS_TOKEN_SECRET')
    
    # Scheduler Configuration
    SCHEDULER_API_ENABLED = True
    SCHEDULER_TIMEZONE = 'UTC'
    
    # Analytics Configuration
    ANALYTICS_UPDATE_INTERVAL = 300  # 5 minutes
    
class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_ECHO = True
    
class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_ECHO = False
    
class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}