from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from datetime import datetime, timedelta
from flask import current_app
from models import Tweet, Campaign, db
from x_api_service import get_x_api
import logging
import json
import pytz

logger = logging.getLogger(__name__)

class SchedulerService:
    """Service for scheduling and managing automated tweet posting."""
    
    def __init__(self):
        self.scheduler = None
        self._initialize_scheduler()
    
    def _initialize_scheduler(self):
        """Initialize APScheduler with database job store."""
        try:
            # Configure job store
            jobstores = {
                'default': SQLAlchemyJobStore(url=current_app.config['SQLALCHEMY_DATABASE_URI'])
            }
            
            # Configure executors
            executors = {
                'default': ThreadPoolExecutor(20)
            }
            
            # Job defaults
            job_defaults = {
                'coalesce': False,
                'max_instances': 3
            }
            
            # Initialize scheduler
            self.scheduler = BackgroundScheduler(
                jobstores=jobstores,
                executors=executors,
                job_defaults=job_defaults,
                timezone=pytz.UTC
            )
            
            logger.info("Scheduler initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize scheduler: {str(e)}")
            self.scheduler = None
    
    def start(self):
        """Start the scheduler."""
        if self.scheduler and not self.scheduler.running:
            try:
                self.scheduler.start()
                logger.info("Scheduler started")
                
                # Schedule pending tweets
                self._schedule_pending_tweets()
                
                # Schedule performance updates
                self._schedule_performance_updates()
                
            except Exception as e:
                logger.error(f"Failed to start scheduler: {str(e)}")
    
    def stop(self):
        """Stop the scheduler."""
        if self.scheduler and self.scheduler.running:
            try:
                self.scheduler.shutdown()
                logger.info("Scheduler stopped")
            except Exception as e:
                logger.error(f"Failed to stop scheduler: {str(e)}")
    
    def schedule_tweet(self, tweet_id, scheduled_time):
        """Schedule a specific tweet for posting."""
        if not self.scheduler:
            logger.error("Scheduler not initialized")
            return False
        
        try:
            job_id = f"tweet_{tweet_id}"
            
            # Remove existing job if it exists
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)
            
            # Schedule new job
            self.scheduler.add_job(
                func=self._post_scheduled_tweet,
                trigger='date',
                run_date=scheduled_time,
                args=[tweet_id],
                id=job_id,
                replace_existing=True
            )
            
            logger.info(f"Tweet {tweet_id} scheduled for {scheduled_time}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to schedule tweet {tweet_id}: {str(e)}")
            return False
    
    def cancel_tweet(self, tweet_id):
        """Cancel a scheduled tweet."""
        if not self.scheduler:
            return False
        
        try:
            job_id = f"tweet_{tweet_id}"
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)
                logger.info(f"Cancelled scheduled tweet {tweet_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to cancel tweet {tweet_id}: {str(e)}")
        
        return False
    
    def _post_scheduled_tweet(self, tweet_id):
        """Post a scheduled tweet."""
        with current_app.app_context():
            try:
                tweet = Tweet.query.get(tweet_id)
                if not tweet:
                    logger.error(f"Tweet {tweet_id} not found")
                    return
                
                if tweet.status != 'scheduled':
                    logger.warning(f"Tweet {tweet_id} is not in scheduled status: {tweet.status}")
                    return
                
                # Get X API service
                x_api = get_x_api()
                if not x_api.is_configured():
                    logger.error("X API not configured")
                    tweet.status = 'failed'
                    db.session.commit()
                    return
                
                # Post tweet
                result = x_api.post_tweet(tweet.content, tweet.media)
                
                if result['success']:
                    tweet.status = 'posted'
                    tweet.posted_time = datetime.utcnow()
                    tweet.tweet_id = result['tweet_id']
                    logger.info(f"Successfully posted tweet {tweet_id}: {result['tweet_id']}")
                else:
                    tweet.status = 'failed'
                    logger.error(f"Failed to post tweet {tweet_id}: {result.get('error')}")
                
                db.session.commit()
                
            except Exception as e:
                logger.error(f"Error posting scheduled tweet {tweet_id}: {str(e)}")
                try:
                    tweet = Tweet.query.get(tweet_id)
                    if tweet:
                        tweet.status = 'failed'
                        db.session.commit()
                except:
                    pass
    
    def _schedule_pending_tweets(self):
        """Schedule all pending tweets in the database."""
        try:
            pending_tweets = Tweet.query.filter_by(status='scheduled').all()
            
            for tweet in pending_tweets:
                if tweet.scheduled_time > datetime.utcnow():
                    self.schedule_tweet(tweet.id, tweet.scheduled_time)
                else:
                    # Tweet is overdue, mark as failed
                    tweet.status = 'failed'
            
            db.session.commit()
            logger.info(f"Scheduled {len(pending_tweets)} pending tweets")
            
        except Exception as e:
            logger.error(f"Failed to schedule pending tweets: {str(e)}")
    
    def _schedule_performance_updates(self):
        """Schedule regular performance metric updates."""
        if not self.scheduler:
            return
        
        try:
            # Schedule performance updates every 30 minutes
            self.scheduler.add_job(
                func=self._update_all_performance,
                trigger='interval',
                minutes=30,
                id='performance_updates',
                replace_existing=True
            )
            
            logger.info("Performance update job scheduled")
            
        except Exception as e:
            logger.error(f"Failed to schedule performance updates: {str(e)}")
    
    def _update_all_performance(self):
        """Update performance metrics for all posted tweets."""
        with current_app.app_context():
            try:
                # Get tweets posted in the last 7 days
                cutoff_date = datetime.utcnow() - timedelta(days=7)
                recent_tweets = Tweet.query.filter(
                    Tweet.status == 'posted',
                    Tweet.posted_time >= cutoff_date,
                    Tweet.tweet_id.isnot(None)
                ).all()
                
                x_api = get_x_api()
                if not x_api.is_configured():
                    logger.warning("X API not configured for performance updates")
                    return
                
                updated_count = 0
                for tweet in recent_tweets:
                    if x_api.update_tweet_performance(tweet.tweet_id):
                        updated_count += 1
                
                logger.info(f"Updated performance for {updated_count} tweets")
                
            except Exception as e:
                logger.error(f"Failed to update performance metrics: {str(e)}")
    
    def get_scheduled_jobs(self):
        """Get list of all scheduled jobs."""
        if not self.scheduler:
            return []
        
        try:
            jobs = []
            for job in self.scheduler.get_jobs():
                jobs.append({
                    'id': job.id,
                    'name': job.name,
                    'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                    'trigger': str(job.trigger)
                })
            return jobs
        except Exception as e:
            logger.error(f"Failed to get scheduled jobs: {str(e)}")
            return []
    
    def create_campaign_schedule(self, campaign_id):
        """Create scheduled tweets for a campaign based on its schedule configuration."""
        try:
            campaign = Campaign.query.get(campaign_id)
            if not campaign:
                logger.error(f"Campaign {campaign_id} not found")
                return False
            
            schedule_config = campaign.schedule
            if not schedule_config:
                logger.error(f"No schedule configuration for campaign {campaign_id}")
                return False
            
            # Parse schedule configuration
            frequency = schedule_config.get('frequency', 'daily')
            times = schedule_config.get('times', ['09:00'])
            
            # Generate scheduled times for the next 7 days
            base_date = datetime.utcnow().date()
            scheduled_times = []
            
            for day_offset in range(7):
                current_date = base_date + timedelta(days=day_offset)
                
                for time_str in times:
                    try:
                        hour, minute = map(int, time_str.split(':'))
                        scheduled_time = datetime.combine(current_date, datetime.min.time().replace(hour=hour, minute=minute))
                        
                        # Only schedule future times
                        if scheduled_time > datetime.utcnow():
                            scheduled_times.append(scheduled_time)
                    except ValueError:
                        logger.warning(f"Invalid time format: {time_str}")
            
            logger.info(f"Generated {len(scheduled_times)} scheduled times for campaign {campaign_id}")
            return scheduled_times
            
        except Exception as e:
            logger.error(f"Failed to create campaign schedule: {str(e)}")
            return False

# Global instance
scheduler_service = SchedulerService()

def get_scheduler():
    """Get the global scheduler service instance."""
    return scheduler_service