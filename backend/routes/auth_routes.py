from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import User, db
from auth import authenticate_user, create_tokens, revoke_token, get_current_user
import logging

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint."""
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        user = authenticate_user(data['email'], data['password'])
        
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        tokens = create_tokens(user)
        
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'role': user.role
            },
            'access_token': tokens['access_token'],
            'refresh_token': tokens['refresh_token']
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/register', methods=['POST'])
def register():
    """User registration endpoint."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'username']
        for field in required_fields:
            if not data or not data.get(field):
                return jsonify({'error': f'{field.capitalize()} is required'}), 400
        
        # Check if user already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 409
        
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already taken'}), 409
        
        # Create new user
        user = User(
            email=data['email'],
            username=data['username'],
            role=data.get('role', 'user')
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # Create tokens
        tokens = create_tokens(user)
        
        return jsonify({
            'message': 'Registration successful',
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'role': user.role
            },
            'access_token': tokens['access_token'],
            'refresh_token': tokens['refresh_token']
        }), 201
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token endpoint."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        tokens = create_tokens(user)
        
        return jsonify({
            'access_token': tokens['access_token'],
            'refresh_token': tokens['refresh_token']
        }), 200
        
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """User logout endpoint."""
    try:
        jti = get_jwt()['jti']
        revoke_token(jti)
        
        return jsonify({'message': 'Successfully logged out'}), 200
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile."""
    try:
        user = get_current_user()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'role': user.role,
                'created_at': user.created_at.isoformat(),
                'x_api_configured': bool(user.x_api_key and user.x_api_secret)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Get profile error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile."""
    try:
        user = get_current_user()
        data = request.get_json()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Update allowed fields
        if 'username' in data:
            # Check if username is already taken by another user
            existing_user = User.query.filter(
                User.username == data['username'],
                User.id != user.id
            ).first()
            
            if existing_user:
                return jsonify({'error': 'Username already taken'}), 409
            
            user.username = data['username']
        
        if 'email' in data:
            # Check if email is already taken by another user
            existing_user = User.query.filter(
                User.email == data['email'],
                User.id != user.id
            ).first()
            
            if existing_user:
                return jsonify({'error': 'Email already registered'}), 409
            
            user.email = data['email']
        
        # Update X API credentials
        if 'x_api_key' in data:
            user.x_api_key = data['x_api_key']
        
        if 'x_api_secret' in data:
            user.x_api_secret = data['x_api_secret']
        
        if 'x_access_token' in data:
            user.x_access_token = data['x_access_token']
        
        if 'x_access_token_secret' in data:
            user.x_access_token_secret = data['x_access_token_secret']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'role': user.role,
                'x_api_configured': bool(user.x_api_key and user.x_api_secret)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Update profile error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password."""
    try:
        user = get_current_user()
        data = request.get_json()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if not data or not data.get('current_password') or not data.get('new_password'):
            return jsonify({'error': 'Current password and new password are required'}), 400
        
        # Verify current password
        if not user.check_password(data['current_password']):
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        # Update password
        user.set_password(data['new_password'])
        db.session.commit()
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        logger.error(f"Change password error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/test-x-api', methods=['POST'])
@jwt_required()
def test_x_api():
    """Test X API connection with user credentials."""
    try:
        user = get_current_user()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if not (user.x_api_key and user.x_api_secret):
            return jsonify({'error': 'X API credentials not configured'}), 400
        
        # Test API connection
        x_api = get_x_api()
        result = x_api.test_connection()
        
        if result['success']:
            return jsonify({
                'message': 'X API connection successful',
                'user_info': result.get('user_info')
            }), 200
        else:
            return jsonify({
                'error': 'X API connection failed',
                'details': result.get('error')
            }), 400
        
    except Exception as e:
        logger.error(f"Test X API error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500