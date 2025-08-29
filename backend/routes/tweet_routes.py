from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Tweet, Campaign, AffiliateLink, TweetPerformance, db
from auth import get_current_user
from scheduler_service import get_scheduler
from x_api_service import get_x_api
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
tweet_bp = Blueprint('tweets', __name__)

@tweet_bp.route('/', methods=['GET'])
@jwt_required()
def get_tweets():
    """Get all tweets for the current user."""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        campaign_id = request.args.get('campaign_id', type=int)
        
        # Build query
        query = Tweet.query.filter_by(user_id=user.id)
        
        if status:
            query = query.filter_by(status=status)
        
        if campaign_id:
            query = query.filter_by(campaign_id=campaign_id)
        
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
        logger.error(f"Get tweets error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@tweet_bp.route('/', methods=['POST'])
@jwt_required()
def create_tweet():
    """Create a new tweet."""
    try:
        user = get_current_user()
        data = request.get_json()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Validate required fields
        if not data or not data.get('content'):
            return jsonify({'error': 'Tweet content is required'}), 400
        
        # Validate tweet length
        if len(data['content']) > 280:
            return jsonify({'error': 'Tweet content exceeds 280 characters'}), 400
        
        # Validate campaign if provided
        campaign_id = data.get('campaign_id')
        if campaign_id:
            campaign = Campaign.query.filter_by(id=campaign_id, user_id=user.id).first()
            if not campaign:
                return jsonify({'error': 'Campaign not found'}), 404
        
        # Validate affiliate link if provided
        affiliate_link_id = data.get('affiliate_link_id')
        if affiliate_link_id:
            affiliate_link = AffiliateLink.query.get(affiliate_link_id)
            if not affiliate_link:
                return jsonify({'error': 'Affiliate link not found'}), 404
        
        # Create tweet
        tweet = Tweet(
            content=data['content'],
            user_id=user.id,
            campaign_id=campaign_id,
            affiliate_link_id=affiliate_link_id,
            status=data.get('status', 'draft'),
            media=data.get('media', []),
            hashtags=data.get('hashtags', []),
            mentions=data.get('mentions', [])
        )
        
        # Handle scheduling
        scheduled_time = data.get('scheduled_time')
        if scheduled_time:
            try:
                tweet.scheduled_time = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
                tweet.status = 'scheduled'
            except ValueError:
                return jsonify({'error': 'Invalid scheduled_time format'}), 400
        
        db.session.add(tweet)
        db.session.commit()
        
        # Schedule tweet if needed
        if tweet.status == 'scheduled' and tweet.scheduled_time:
            scheduler = get_scheduler()
            if scheduler.schedule_tweet(tweet.id, tweet.scheduled_time):
                logger.info(f"Tweet {tweet.id} scheduled for {tweet.scheduled_time}")
            else:
                logger.error(f"Failed to schedule tweet {tweet.id}")
        
        return jsonify({
            'message': 'Tweet created successfully',
            'tweet': tweet.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Create tweet error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@tweet_bp.route('/<int:tweet_id>', methods=['GET'])
@jwt_required()
def get_tweet(tweet_id):
    """Get a specific tweet."""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        tweet = Tweet.query.filter_by(id=tweet_id, user_id=user.id).first()
        
        if not tweet:
            return jsonify({'error': 'Tweet not found'}), 404
        
        # Include performance data if available
        result = tweet.to_dict()
        
        if tweet.tweet_id:  # Tweet has been posted
            performance = TweetPerformance.query.filter_by(tweet_id=tweet.tweet_id).first()
            if performance:
                result['performance'] = performance.to_dict()
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Get tweet error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@tweet_bp.route('/<int:tweet_id>', methods=['PUT'])
@jwt_required()
def update_tweet(tweet_id):
    """Update a tweet."""
    try:
        user = get_current_user()
        data = request.get_json()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        tweet = Tweet.query.filter_by(id=tweet_id, user_id=user.id).first()
        
        if not tweet:
            return jsonify({'error': 'Tweet not found'}), 404
        
        # Can't update posted tweets
        if tweet.status == 'posted':
            return jsonify({'error': 'Cannot update posted tweets'}), 400
        
        # Update allowed fields
        if 'content' in data:
            if len(data['content']) > 280:
                return jsonify({'error': 'Tweet content exceeds 280 characters'}), 400
            tweet.content = data['content']
        
        if 'media' in data:
            tweet.media = data['media']
        
        if 'hashtags' in data:
            tweet.hashtags = data['hashtags']
        
        if 'mentions' in data:
            tweet.mentions = data['mentions']
        
        if 'affiliate_link_id' in data:
            if data['affiliate_link_id']:
                affiliate_link = AffiliateLink.query.get(data['affiliate_link_id'])
                if not affiliate_link:
                    return jsonify({'error': 'Affiliate link not found'}), 404
            tweet.affiliate_link_id = data['affiliate_link_id']
        
        # Handle scheduling changes
        if 'scheduled_time' in data:
            old_scheduled_time = tweet.scheduled_time
            
            if data['scheduled_time']:
                try:
                    new_scheduled_time = datetime.fromisoformat(data['scheduled_time'].replace('Z', '+00:00'))
                    tweet.scheduled_time = new_scheduled_time
                    tweet.status = 'scheduled'
                    
                    # Reschedule if time changed
                    if old_scheduled_time != new_scheduled_time:
                        scheduler = get_scheduler()
                        scheduler.schedule_tweet(tweet.id, new_scheduled_time)
                        
                except ValueError:
                    return jsonify({'error': 'Invalid scheduled_time format'}), 400
            else:
                # Remove scheduling
                tweet.scheduled_time = None
                tweet.status = 'draft'
                
                # Cancel scheduled job
                scheduler = get_scheduler()
                scheduler.cancel_tweet(tweet.id)
        
        tweet.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Tweet updated successfully',
            'tweet': tweet.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Update tweet error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@tweet_bp.route('/<int:tweet_id>', methods=['DELETE'])
@jwt_required()
def delete_tweet(tweet_id):
    """Delete a tweet."""
    try:
        user = get_current_user()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        tweet = Tweet.query.filter_by(id=tweet_id, user_id=user.id).first()
        
        if not tweet:
            return jsonify({'error': 'Tweet not found'}), 404
        
        # Can't delete posted tweets
        if tweet.status == 'posted':
            return jsonify({'error': 'Cannot delete posted tweets'}), 400
        
        # Cancel scheduled job if exists
        if tweet.status == 'scheduled':
            scheduler = get_scheduler()
            scheduler.cancel_tweet(tweet.id)
        
        # Delete performance data if exists
        if tweet.tweet_id:
            TweetPerformance.query.filter_by(tweet_id=tweet.tweet_id).delete()
        
        db.session.delete(tweet)
        db.session.commit()
        
        return jsonify({'message': 'Tweet deleted successfully'}), 200
        
    except Exception as e:
        logger.error(f"Delete tweet error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@tweet_bp.route('/<int:tweet_id>/post', methods=['POST'])
@jwt_required()
def post_tweet_now(tweet_id):
    """Post a tweet immediately."""
    try:
        user = get_current_user()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        tweet = Tweet.query.filter_by(id=tweet_id, user_id=user.id).first()
        
        if not tweet:
            return jsonify({'error': 'Tweet not found'}), 404
        
        if tweet.status == 'posted':
            return jsonify({'error': 'Tweet already posted'}), 400
        
        # Check X API configuration
        if not (user.x_api_key and user.x_api_secret):
            return jsonify({'error': 'X API credentials not configured'}), 400
        
        # Cancel scheduled job if exists
        if tweet.status == 'scheduled':
            scheduler = get_scheduler()
            scheduler.cancel_tweet(tweet.id)
        
        # Post tweet
        x_api = get_x_api()
        result = x_api.post_tweet(tweet.content, tweet.media)
        
        if result['success']:
            tweet.status = 'posted'
            tweet.posted_time = datetime.utcnow()
            tweet.tweet_id = result['tweet_id']
            db.session.commit()
            
            return jsonify({
                'message': 'Tweet posted successfully',
                'tweet': tweet.to_dict(),
                'x_tweet_id': result['tweet_id']
            }), 200
        else:
            tweet.status = 'failed'
            db.session.commit()
            
            return jsonify({
                'error': 'Failed to post tweet',
                'details': result.get('error')
            }), 400
        
    except Exception as e:
        logger.error(f"Post tweet error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@tweet_bp.route('/<int:tweet_id>/schedule', methods=['POST'])
@jwt_required()
def schedule_tweet(tweet_id):
    """Schedule a tweet for later posting."""
    try:
        user = get_current_user()
        data = request.get_json()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        tweet = Tweet.query.filter_by(id=tweet_id, user_id=user.id).first()
        
        if not tweet:
            return jsonify({'error': 'Tweet not found'}), 404
        
        if tweet.status == 'posted':
            return jsonify({'error': 'Tweet already posted'}), 400
        
        if not data or not data.get('scheduled_time'):
            return jsonify({'error': 'Scheduled time is required'}), 400
        
        try:
            scheduled_time = datetime.fromisoformat(data['scheduled_time'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': 'Invalid scheduled_time format'}), 400
        
        if scheduled_time <= datetime.utcnow():
            return jsonify({'error': 'Scheduled time must be in the future'}), 400
        
        # Update tweet
        tweet.scheduled_time = scheduled_time
        tweet.status = 'scheduled'
        tweet.updated_at = datetime.utcnow()
        
        # Schedule the tweet
        scheduler = get_scheduler()
        if scheduler.schedule_tweet(tweet.id, scheduled_time):
            db.session.commit()
            
            return jsonify({
                'message': 'Tweet scheduled successfully',
                'tweet': tweet.to_dict()
            }), 200
        else:
            db.session.rollback()
            return jsonify({'error': 'Failed to schedule tweet'}), 500
        
    except Exception as e:
        logger.error(f"Schedule tweet error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@tweet_bp.route('/<int:tweet_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_tweet(tweet_id):
    """Cancel a scheduled tweet."""
    try:
        user = get_current_user()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        tweet = Tweet.query.filter_by(id=tweet_id, user_id=user.id).first()
        
        if not tweet:
            return jsonify({'error': 'Tweet not found'}), 404
        
        if tweet.status != 'scheduled':
            return jsonify({'error': 'Tweet is not scheduled'}), 400
        
        # Cancel scheduled job
        scheduler = get_scheduler()
        if scheduler.cancel_tweet(tweet.id):
            tweet.status = 'cancelled'
            tweet.updated_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'message': 'Tweet cancelled successfully',
                'tweet': tweet.to_dict()
            }), 200
        else:
            return jsonify({'error': 'Failed to cancel tweet'}), 500
        
    except Exception as e:
        logger.error(f"Cancel tweet error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@tweet_bp.route('/<int:tweet_id>/performance', methods=['GET'])
@jwt_required()
def get_tweet_performance(tweet_id):
    """Get performance metrics for a specific tweet."""
    try:
        user = get_current_user()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        tweet = Tweet.query.filter_by(id=tweet_id, user_id=user.id).first()
        
        if not tweet:
            return jsonify({'error': 'Tweet not found'}), 404
        
        if not tweet.tweet_id:
            return jsonify({'error': 'Tweet not posted yet'}), 400
        
        # Get performance data
        performance = TweetPerformance.query.filter_by(tweet_id=tweet.tweet_id).first()
        
        if not performance:
            # Try to fetch fresh data from X API
            x_api = get_x_api()
            if x_api.update_tweet_performance(tweet.tweet_id):
                performance = TweetPerformance.query.filter_by(tweet_id=tweet.tweet_id).first()
        
        if performance:
            return jsonify({
                'tweet': tweet.to_dict(),
                'performance': performance.to_dict()
            }), 200
        else:
            return jsonify({
                'tweet': tweet.to_dict(),
                'performance': None,
                'message': 'Performance data not available'
            }), 200
        
    except Exception as e:
        logger.error(f"Get tweet performance error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@tweet_bp.route('/bulk-schedule', methods=['POST'])
@jwt_required()
def bulk_schedule_tweets():
    """Schedule multiple tweets at once."""
    try:
        user = get_current_user()
        data = request.get_json()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if not data or not data.get('tweets'):
            return jsonify({'error': 'Tweets data is required'}), 400
        
        scheduled_tweets = []
        failed_tweets = []
        
        scheduler = get_scheduler()
        
        for tweet_data in data['tweets']:
            try:
                tweet_id = tweet_data.get('tweet_id')
                scheduled_time_str = tweet_data.get('scheduled_time')
                
                if not tweet_id or not scheduled_time_str:
                    failed_tweets.append({
                        'tweet_id': tweet_id,
                        'error': 'Tweet ID and scheduled time are required'
                    })
                    continue
                
                tweet = Tweet.query.filter_by(id=tweet_id, user_id=user.id).first()
                
                if not tweet:
                    failed_tweets.append({
                        'tweet_id': tweet_id,
                        'error': 'Tweet not found'
                    })
                    continue
                
                if tweet.status == 'posted':
                    failed_tweets.append({
                        'tweet_id': tweet_id,
                        'error': 'Tweet already posted'
                    })
                    continue
                
                try:
                    scheduled_time = datetime.fromisoformat(scheduled_time_str.replace('Z', '+00:00'))
                except ValueError:
                    failed_tweets.append({
                        'tweet_id': tweet_id,
                        'error': 'Invalid scheduled time format'
                    })
                    continue
                
                if scheduled_time <= datetime.utcnow():
                    failed_tweets.append({
                        'tweet_id': tweet_id,
                        'error': 'Scheduled time must be in the future'
                    })
                    continue
                
                # Update tweet
                tweet.scheduled_time = scheduled_time
                tweet.status = 'scheduled'
                tweet.updated_at = datetime.utcnow()
                
                # Schedule the tweet
                if scheduler.schedule_tweet(tweet.id, scheduled_time):
                    scheduled_tweets.append(tweet.to_dict())
                else:
                    failed_tweets.append({
                        'tweet_id': tweet_id,
                        'error': 'Failed to schedule tweet'
                    })
                
            except Exception as e:
                failed_tweets.append({
                    'tweet_id': tweet_data.get('tweet_id'),
                    'error': str(e)
                })
        
        db.session.commit()
        
        return jsonify({
            'message': f'Bulk scheduling completed: {len(scheduled_tweets)} scheduled, {len(failed_tweets)} failed',
            'scheduled_tweets': scheduled_tweets,
            'failed_tweets': failed_tweets
        }), 200
        
    except Exception as e:
        logger.error(f"Bulk schedule tweets error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500