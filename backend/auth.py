from functools import wraps
from flask import request, jsonify, current_app
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, create_refresh_token, get_jwt_identity, get_jwt
from models import User, db
from datetime import datetime, timedelta

jwt = JWTManager()

# JWT token blacklist for logout functionality
blacklisted_tokens = set()

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    """Check if JWT token is in blacklist."""
    jti = jwt_payload['jti']
    return jti in blacklisted_tokens

def init_auth(app):
    """Initialize JWT authentication."""
    jwt.init_app(app)

def authenticate_user(email, password):
    """Authenticate user with email and password."""
    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        return user
    return None

def create_tokens(user):
    """Create access and refresh tokens for user."""
    additional_claims = {
        'role': user.role,
        'user_id': user.id
    }
    
    access_token = create_access_token(
        identity=user.username,
        additional_claims=additional_claims
    )
    
    refresh_token = create_refresh_token(
        identity=user.username,
        additional_claims=additional_claims
    )
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'expires_in': current_app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds()
    }

def revoke_token(jti):
    """Add token to blacklist."""
    blacklisted_tokens.add(jti)

def require_role(required_role):
    """Decorator to require specific user role."""
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user = get_current_user()
            if not current_user:
                return jsonify({'error': 'User not found'}), 404
            
            if current_user.role != required_role and current_user.role != 'admin':
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_current_user():
    """Get current authenticated user."""
    current_username = get_jwt_identity()
    return User.query.filter_by(username=current_username).first()

def create_admin_user():
    """Create default admin user if none exists."""
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@example.com',
            role='admin'
        )
        admin.set_password('admin123')  # Change this in production
        db.session.add(admin)
        db.session.commit()
        print("Default admin user created: username='admin', email='admin@example.com', password='admin123'")
        return admin
    return admin

def validate_api_key(api_key):
    """Validate API key for external integrations."""
    # For now, just check if it's not empty
    # In production, implement proper API key validation
    return api_key and len(api_key) > 10

def hash_password(password):
    """Hash password using werkzeug."""
    from werkzeug.security import generate_password_hash
    return generate_password_hash(password)

def verify_password(password, password_hash):
    """Verify password against hash."""
    from werkzeug.security import check_password_hash
    return check_password_hash(password_hash, password)