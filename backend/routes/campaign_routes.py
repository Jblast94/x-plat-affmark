from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Campaign, Tweet, db
from auth import get_current_user, require_role
from analytics_service import get_analytics
from scheduler_service import get_scheduler
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
campaign_bp = Blueprint('campaigns', __name__)

@campaign_bp.route('/', methods=['GET'])
@jwt_required()
def get_campaigns():
    """Get all campaigns for the current user."""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        
        # Build query
        query = Campaign.query.filter_by(user_id=user.id)
        
        if status:
            query = query.filter_by(status=status)
        
        # Paginate results
        campaigns = query.order_by(Campaign.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Format response
        result = {
            'campaigns': [campaign.to_dict() for campaign in campaigns.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': campaigns.total,
                'pages': campaigns.pages,
                'has_next': campaigns.has_next,
                'has_prev': campaigns.has_prev
            }
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Get campaigns error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@campaign_bp.route('/', methods=['POST'])
@jwt_required()
def create_campaign():
    """Create a new campaign."""
    try:
        user = get_current_user()
        data = request.get_json()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Validate required fields
        required_fields = ['name', 'description']
        for field in required_fields:
            if not data or not data.get(field):
                return jsonify({'error': f'{field.capitalize()} is required'}), 400
        
        # Create campaign
        campaign = Campaign(
            name=data['name'],
            description=data['description'],
            user_id=user.id,
            status=data.get('status', 'draft'),
            schedule=data.get('schedule', {}),
            target_audience=data.get('target_audience', {}),
            budget=data.get('budget', 0.0)
        )
        
        db.session.add(campaign)
        db.session.commit()
        
        # If campaign is active and has schedule, create scheduled tweets
        if campaign.status == 'active' and campaign.schedule:
            scheduler = get_scheduler()
            scheduler.create_campaign_schedule(campaign.id)
        
        return jsonify({
            'message': 'Campaign created successfully',
            'campaign': campaign.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Create campaign error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@campaign_bp.route('/<int:campaign_id>', methods=['GET'])
@jwt_required()
def get_campaign(campaign_id):
    """Get a specific campaign."""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        campaign = Campaign.query.filter_by(id=campaign_id, user_id=user.id).first()
        
        if not campaign:
            return jsonify({'error': 'Campaign not found'}), 404
        
        # Get campaign performance data
        analytics = get_analytics()
        performance = analytics.get_campaign_performance(campaign_id, user.id)
        
        result = campaign.to_dict()
        if performance:
            result['performance'] = performance['metrics']
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Get campaign error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@campaign_bp.route('/<int:campaign_id>', methods=['PUT'])
@jwt_required()
def update_campaign(campaign_id):
    """Update a campaign."""
    try:
        user = get_current_user()
        data = request.get_json()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        campaign = Campaign.query.filter_by(id=campaign_id, user_id=user.id).first()
        
        if not campaign:
            return jsonify({'error': 'Campaign not found'}), 404
        
        # Update allowed fields
        updatable_fields = ['name', 'description', 'status', 'schedule', 'target_audience', 'budget']
        
        for field in updatable_fields:
            if field in data:
                setattr(campaign, field, data[field])
        
        campaign.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Handle status changes
        if 'status' in data:
            if data['status'] == 'active' and campaign.schedule:
                # Create scheduled tweets for active campaign
                scheduler = get_scheduler()
                scheduler.create_campaign_schedule(campaign.id)
            elif data['status'] in ['paused', 'completed']:
                # Cancel scheduled tweets
                scheduled_tweets = Tweet.query.filter_by(
                    campaign_id=campaign.id,
                    status='scheduled'
                ).all()
                
                scheduler = get_scheduler()
                for tweet in scheduled_tweets:
                    scheduler.cancel_tweet(tweet.id)
        
        return jsonify({
            'message': 'Campaign updated successfully',
            'campaign': campaign.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Update campaign error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@campaign_bp.route('/<int:campaign_id>', methods=['DELETE'])
@jwt_required()
def delete_campaign(campaign_id):
    """Delete a campaign."""
    try:
        user = get_current_user()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        campaign = Campaign.query.filter_by(id=campaign_id, user_id=user.id).first()
        
        if not campaign:
            return jsonify({'error': 'Campaign not found'}), 404
        
        # Cancel all scheduled tweets for this campaign
        scheduled_tweets = Tweet.query.filter_by(
            campaign_id=campaign.id,
            status='scheduled'
        ).all()
        
        scheduler = get_scheduler()
        for tweet in scheduled_tweets:
            scheduler.cancel_tweet(tweet.id)
        
        # Delete campaign and associated tweets
        Tweet.query.filter_by(campaign_id=campaign.id).delete()
        db.session.delete(campaign)
        db.session.commit()
        
        return jsonify({'message': 'Campaign deleted successfully'}), 200
        
    except Exception as e:
        logger.error(f"Delete campaign error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@campaign_bp.route('/<int:campaign_id>/tweets', methods=['GET'])
@jwt_required()
def get_campaign_tweets(campaign_id):
    """Get all tweets for a specific campaign."""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        campaign = Campaign.query.filter_by(id=campaign_id, user_id=user.id).first()
        
        if not campaign:
            return jsonify({'error': 'Campaign not found'}), 404
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        
        # Build query
        query = Tweet.query.filter_by(campaign_id=campaign_id)
        
        if status:
            query = query.filter_by(status=status)
        
        # Paginate results
        tweets = query.order_by(Tweet.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Format response
        result = {
            'tweets': [tweet.to_dict() for tweet in tweets.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': tweets.total,
                'pages': tweets.pages,
                'has_next': tweets.has_next,
                'has_prev': tweets.has_prev
            }
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Get campaign tweets error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@campaign_bp.route('/<int:campaign_id>/performance', methods=['GET'])
@jwt_required()
def get_campaign_performance(campaign_id):
    """Get detailed performance metrics for a campaign."""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        campaign = Campaign.query.filter_by(id=campaign_id, user_id=user.id).first()
        
        if not campaign:
            return jsonify({'error': 'Campaign not found'}), 404
        
        analytics = get_analytics()
        performance = analytics.get_campaign_performance(campaign_id, user.id)
        
        if not performance:
            return jsonify({'error': 'Performance data not available'}), 404
        
        return jsonify(performance), 200
        
    except Exception as e:
        logger.error(f"Get campaign performance error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@campaign_bp.route('/<int:campaign_id>/activate', methods=['POST'])
@jwt_required()
def activate_campaign(campaign_id):
    """Activate a campaign and start scheduling tweets."""
    try:
        user = get_current_user()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        campaign = Campaign.query.filter_by(id=campaign_id, user_id=user.id).first()
        
        if not campaign:
            return jsonify({'error': 'Campaign not found'}), 404
        
        if campaign.status == 'active':
            return jsonify({'error': 'Campaign is already active'}), 400
        
        # Activate campaign
        campaign.status = 'active'
        campaign.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Create scheduled tweets if schedule is configured
        if campaign.schedule:
            scheduler = get_scheduler()
            scheduled_times = scheduler.create_campaign_schedule(campaign.id)
            
            return jsonify({
                'message': 'Campaign activated successfully',
                'campaign': campaign.to_dict(),
                'scheduled_times': scheduled_times
            }), 200
        else:
            return jsonify({
                'message': 'Campaign activated successfully',
                'campaign': campaign.to_dict(),
                'note': 'No schedule configured - tweets will need to be scheduled manually'
            }), 200
        
    except Exception as e:
        logger.error(f"Activate campaign error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@campaign_bp.route('/<int:campaign_id>/pause', methods=['POST'])
@jwt_required()
def pause_campaign(campaign_id):
    """Pause a campaign and cancel scheduled tweets."""
    try:
        user = get_current_user()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        campaign = Campaign.query.filter_by(id=campaign_id, user_id=user.id).first()
        
        if not campaign:
            return jsonify({'error': 'Campaign not found'}), 404
        
        if campaign.status != 'active':
            return jsonify({'error': 'Campaign is not active'}), 400
        
        # Pause campaign
        campaign.status = 'paused'
        campaign.updated_at = datetime.utcnow()
        
        # Cancel scheduled tweets
        scheduled_tweets = Tweet.query.filter_by(
            campaign_id=campaign.id,
            status='scheduled'
        ).all()
        
        scheduler = get_scheduler()
        cancelled_count = 0
        
        for tweet in scheduled_tweets:
            if scheduler.cancel_tweet(tweet.id):
                tweet.status = 'cancelled'
                cancelled_count += 1
        
        db.session.commit()
        
        return jsonify({
            'message': 'Campaign paused successfully',
            'campaign': campaign.to_dict(),
            'cancelled_tweets': cancelled_count
        }), 200
        
    except Exception as e:
        logger.error(f"Pause campaign error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500