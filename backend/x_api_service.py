import tweepy
import os
from datetime import datetime
from flask import current_app
from models import Tweet, TweetPerformance, db
import logging

logger = logging.getLogger(__name__)

class XAPIService:
    """Service for X (Twitter) API integration using Tweepy."""
    
    def __init__(self):
        self.api = None
        self.client = None
        self._initialize_api()
    
    def _initialize_api(self):
        """Initialize Tweepy API clients."""
        try:
            # Get credentials from config
            api_key = current_app.config.get('X_API_KEY')
            api_secret = current_app.config.get('X_API_SECRET')
            access_token = current_app.config.get('X_ACCESS_TOKEN')
            access_token_secret = current_app.config.get('X_ACCESS_TOKEN_SECRET')
            
            if not all([api_key, api_secret, access_token, access_token_secret]):
                logger.warning("X API credentials not configured")
                return
            
            # Initialize OAuth 1.0a authentication
            auth = tweepy.OAuthHandler(api_key, api_secret)
            auth.set_access_token(access_token, access_token_secret)
            
            # Initialize API v1.1 client (for media upload)
            self.api = tweepy.API(auth, wait_on_rate_limit=True)
            
            # Initialize API v2 client (for posting tweets)
            self.client = tweepy.Client(
                consumer_key=api_key,
                consumer_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_token_secret,
                wait_on_rate_limit=True
            )
            
            logger.info("X API clients initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize X API: {str(e)}")
            self.api = None
            self.client = None
    
    def is_configured(self):
        """Check if X API is properly configured."""
        return self.api is not None and self.client is not None
    
    def post_tweet(self, content, media_urls=None):
        """Post a tweet with optional media."""
        if not self.is_configured():
            raise Exception("X API not configured")
        
        try:
            media_ids = []
            
            # Upload media if provided
            if media_urls:
                for media_url in media_urls:
                    try:
                        # Download and upload media
                        media_id = self._upload_media(media_url)
                        if media_id:
                            media_ids.append(media_id)
                    except Exception as e:
                        logger.warning(f"Failed to upload media {media_url}: {str(e)}")
            
            # Post tweet
            response = self.client.create_tweet(
                text=content,
                media_ids=media_ids if media_ids else None
            )
            
            if response.data:
                tweet_id = response.data['id']
                logger.info(f"Tweet posted successfully: {tweet_id}")
                return {
                    'success': True,
                    'tweet_id': tweet_id,
                    'url': f"https://twitter.com/user/status/{tweet_id}"
                }
            else:
                raise Exception("Failed to post tweet - no response data")
                
        except Exception as e:
            logger.error(f"Failed to post tweet: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _upload_media(self, media_url):
        """Upload media to X and return media ID."""
        try:
            import requests
            
            # Download media
            response = requests.get(media_url, timeout=30)
            response.raise_for_status()
            
            # Create temporary file
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(response.content)
                temp_file_path = temp_file.name
            
            try:
                # Upload to X
                media = self.api.media_upload(temp_file_path)
                return media.media_id
            finally:
                # Clean up temporary file
                os.unlink(temp_file_path)
                
        except Exception as e:
            logger.error(f"Failed to upload media: {str(e)}")
            return None
    
    def get_tweet_metrics(self, tweet_id):
        """Get metrics for a specific tweet."""
        if not self.is_configured():
            return None
        
        try:
            # Get tweet with metrics
            tweet = self.client.get_tweet(
                tweet_id,
                tweet_fields=['public_metrics', 'created_at'],
                expansions=['author_id']
            )
            
            if tweet.data:
                metrics = tweet.data.public_metrics
                return {
                    'impressions': metrics.get('impression_count', 0),
                    'retweets': metrics.get('retweet_count', 0),
                    'likes': metrics.get('like_count', 0),
                    'replies': metrics.get('reply_count', 0),
                    'quotes': metrics.get('quote_count', 0)
                }
            
        except Exception as e:
            logger.error(f"Failed to get tweet metrics for {tweet_id}: {str(e)}")
        
        return None
    
    def update_tweet_performance(self, tweet_id):
        """Update performance metrics for a tweet in database."""
        tweet = Tweet.query.filter_by(tweet_id=str(tweet_id)).first()
        if not tweet:
            logger.warning(f"Tweet {tweet_id} not found in database")
            return False
        
        metrics = self.get_tweet_metrics(tweet_id)
        if not metrics:
            return False
        
        try:
            # Calculate engagement rate
            total_engagements = metrics['retweets'] + metrics['likes'] + metrics['replies']
            engagement_rate = (total_engagements / max(metrics['impressions'], 1)) * 100
            
            # Create or update performance record
            performance = TweetPerformance.query.filter_by(tweet_id=tweet.id).first()
            if not performance:
                performance = TweetPerformance(tweet_id=tweet.id)
                db.session.add(performance)
            
            performance.impressions = metrics['impressions']
            performance.retweets = metrics['retweets']
            performance.likes = metrics['likes']
            performance.replies = metrics['replies']
            performance.engagement_rate = engagement_rate
            performance.recorded_at = datetime.utcnow()
            
            db.session.commit()
            logger.info(f"Updated performance for tweet {tweet_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update tweet performance: {str(e)}")
            db.session.rollback()
            return False
    
    def test_connection(self):
        """Test X API connection."""
        if not self.is_configured():
            return {'success': False, 'error': 'API not configured'}
        
        try:
            # Test by getting user info
            user = self.client.get_me()
            if user.data:
                return {
                    'success': True,
                    'username': user.data.username,
                    'user_id': user.data.id
                }
            else:
                return {'success': False, 'error': 'Failed to get user info'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}

# Global instance
x_api = XAPIService()

def get_x_api():
    """Get the global X API service instance."""
    return x_api