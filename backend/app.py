from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from datetime import datetime
import os
import logging

# Import configuration
from config import Config

# Import services
from auth import init_auth, create_admin_user
from scheduler_service import get_scheduler
from analytics_service import get_analytics
from x_api_service import get_x_api

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    CORS(app)
    
    # Initialize database
    from models import db
    db.init_app(app)
    
    # Initialize JWT
    init_auth(app)
    
    # Register blueprints
    from routes.auth_routes import auth_bp
    from routes.campaign_routes import campaign_bp
    from routes.tweet_routes import tweet_bp
    from routes.analytics_routes import analytics_bp
    from routes.affiliate_routes import affiliate_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(campaign_bp, url_prefix='/api/campaigns')
    app.register_blueprint(tweet_bp, url_prefix='/api/tweets')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(affiliate_bp, url_prefix='/api/affiliate-links')
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})
    
    # Initialize database and create tables
    with app.app_context():
        db.create_all()
        create_admin_user()
        
        # Start scheduler
        scheduler = get_scheduler()
        scheduler.start()
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)