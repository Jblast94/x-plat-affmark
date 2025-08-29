from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
from models import Tweet, Campaign, AffiliateLink, TweetPerformance, Analytics, db
from flask import current_app
import logging
import json

logger = logging.getLogger(__name__)

class AnalyticsService:
    """Service for analytics data processing and reporting."""
    
    def __init__(self):
        pass
    
    def get_dashboard_stats(self, user_id=None, days=30):
        """Get dashboard statistics for the specified period."""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Base query filters
            base_filters = [Tweet.created_at >= start_date]
            if user_id:
                base_filters.append(Tweet.user_id == user_id)
            
            # Total tweets
            total_tweets = Tweet.query.filter(*base_filters).count()
            
            # Posted tweets
            posted_tweets = Tweet.query.filter(
                *base_filters,
                Tweet.status == 'posted'
            ).count()
            
            # Active campaigns
            campaign_filters = [Campaign.created_at >= start_date]
            if user_id:
                campaign_filters.append(Campaign.user_id == user_id)
            
            active_campaigns = Campaign.query.filter(
                *campaign_filters,
                Campaign.status == 'active'
            ).count()
            
            # Total engagement (from performance data)
            engagement_query = db.session.query(
                func.sum(TweetPerformance.likes + TweetPerformance.retweets + TweetPerformance.replies).label('total_engagement')
            ).join(Tweet).filter(*base_filters)
            
            total_engagement = engagement_query.scalar() or 0
            
            # Click-through rate calculation
            clicks_query = db.session.query(
                func.sum(TweetPerformance.url_clicks).label('total_clicks')
            ).join(Tweet).filter(*base_filters)
            
            total_clicks = clicks_query.scalar() or 0
            ctr = (total_clicks / total_tweets * 100) if total_tweets > 0 else 0
            
            return {
                'total_tweets': total_tweets,
                'posted_tweets': posted_tweets,
                'active_campaigns': active_campaigns,
                'total_engagement': int(total_engagement),
                'click_through_rate': round(ctr, 2),
                'period_days': days
            }
            
        except Exception as e:
            logger.error(f"Failed to get dashboard stats: {str(e)}")
            return {
                'total_tweets': 0,
                'posted_tweets': 0,
                'active_campaigns': 0,
                'total_engagement': 0,
                'click_through_rate': 0,
                'period_days': days
            }
    
    def get_engagement_trends(self, user_id=None, days=30):
        """Get engagement trends over time."""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Base query filters
            base_filters = [Tweet.posted_time >= start_date, Tweet.status == 'posted']
            if user_id:
                base_filters.append(Tweet.user_id == user_id)
            
            # Daily engagement data
            daily_engagement = db.session.query(
                func.date(Tweet.posted_time).label('date'),
                func.sum(TweetPerformance.likes).label('likes'),
                func.sum(TweetPerformance.retweets).label('retweets'),
                func.sum(TweetPerformance.replies).label('replies'),
                func.sum(TweetPerformance.impressions).label('impressions'),
                func.count(Tweet.id).label('tweet_count')
            ).join(TweetPerformance).filter(*base_filters).group_by(
                func.date(Tweet.posted_time)
            ).order_by(func.date(Tweet.posted_time)).all()
            
            # Format data for frontend
            trends = []
            for row in daily_engagement:
                trends.append({
                    'date': row.date.isoformat(),
                    'likes': int(row.likes or 0),
                    'retweets': int(row.retweets or 0),
                    'replies': int(row.replies or 0),
                    'impressions': int(row.impressions or 0),
                    'tweet_count': int(row.tweet_count or 0),
                    'total_engagement': int((row.likes or 0) + (row.retweets or 0) + (row.replies or 0))
                })
            
            return trends
            
        except Exception as e:
            logger.error(f"Failed to get engagement trends: {str(e)}")
            return []
    
    def get_top_performing_tweets(self, user_id=None, limit=10, days=30):
        """Get top performing tweets by engagement."""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Base query filters
            base_filters = [
                Tweet.posted_time >= start_date,
                Tweet.status == 'posted',
                Tweet.tweet_id.isnot(None)
            ]
            if user_id:
                base_filters.append(Tweet.user_id == user_id)
            
            # Query top tweets by total engagement
            top_tweets = db.session.query(
                Tweet,
                TweetPerformance,
                (TweetPerformance.likes + TweetPerformance.retweets + TweetPerformance.replies).label('total_engagement')
            ).join(TweetPerformance).filter(*base_filters).order_by(
                (TweetPerformance.likes + TweetPerformance.retweets + TweetPerformance.replies).desc()
            ).limit(limit).all()
            
            # Format data
            result = []
            for tweet, performance, total_engagement in top_tweets:
                result.append({
                    'id': tweet.id,
                    'content': tweet.content[:100] + '...' if len(tweet.content) > 100 else tweet.content,
                    'posted_time': tweet.posted_time.isoformat(),
                    'tweet_id': tweet.tweet_id,
                    'campaign_id': tweet.campaign_id,
                    'likes': performance.likes,
                    'retweets': performance.retweets,
                    'replies': performance.replies,
                    'impressions': performance.impressions,
                    'url_clicks': performance.url_clicks,
                    'total_engagement': int(total_engagement)
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get top performing tweets: {str(e)}")
            return []
    
    def get_campaign_performance(self, campaign_id, user_id=None):
        """Get detailed performance metrics for a specific campaign."""
        try:
            # Verify campaign access
            campaign_filters = [Campaign.id == campaign_id]
            if user_id:
                campaign_filters.append(Campaign.user_id == user_id)
            
            campaign = Campaign.query.filter(*campaign_filters).first()
            if not campaign:
                return None
            
            # Get campaign tweets
            tweets = Tweet.query.filter_by(campaign_id=campaign_id).all()
            
            # Calculate metrics
            total_tweets = len(tweets)
            posted_tweets = len([t for t in tweets if t.status == 'posted'])
            scheduled_tweets = len([t for t in tweets if t.status == 'scheduled'])
            
            # Get performance data for posted tweets
            performance_data = db.session.query(
                func.sum(TweetPerformance.likes).label('total_likes'),
                func.sum(TweetPerformance.retweets).label('total_retweets'),
                func.sum(TweetPerformance.replies).label('total_replies'),
                func.sum(TweetPerformance.impressions).label('total_impressions'),
                func.sum(TweetPerformance.url_clicks).label('total_clicks'),
                func.avg(TweetPerformance.likes).label('avg_likes'),
                func.avg(TweetPerformance.retweets).label('avg_retweets'),
                func.avg(TweetPerformance.replies).label('avg_replies')
            ).join(Tweet).filter(
                Tweet.campaign_id == campaign_id,
                Tweet.status == 'posted'
            ).first()
            
            # Calculate engagement rate
            total_engagement = (performance_data.total_likes or 0) + (performance_data.total_retweets or 0) + (performance_data.total_replies or 0)
            total_impressions = performance_data.total_impressions or 0
            engagement_rate = (total_engagement / total_impressions * 100) if total_impressions > 0 else 0
            
            # Calculate click-through rate
            total_clicks = performance_data.total_clicks or 0
            ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            
            return {
                'campaign': {
                    'id': campaign.id,
                    'name': campaign.name,
                    'status': campaign.status,
                    'created_at': campaign.created_at.isoformat(),
                    'description': campaign.description
                },
                'metrics': {
                    'total_tweets': total_tweets,
                    'posted_tweets': posted_tweets,
                    'scheduled_tweets': scheduled_tweets,
                    'total_likes': int(performance_data.total_likes or 0),
                    'total_retweets': int(performance_data.total_retweets or 0),
                    'total_replies': int(performance_data.total_replies or 0),
                    'total_impressions': int(performance_data.total_impressions or 0),
                    'total_clicks': int(performance_data.total_clicks or 0),
                    'total_engagement': int(total_engagement),
                    'avg_likes': round(float(performance_data.avg_likes or 0), 2),
                    'avg_retweets': round(float(performance_data.avg_retweets or 0), 2),
                    'avg_replies': round(float(performance_data.avg_replies or 0), 2),
                    'engagement_rate': round(engagement_rate, 2),
                    'click_through_rate': round(ctr, 2)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get campaign performance: {str(e)}")
            return None
    
    def get_affiliate_link_performance(self, user_id=None, days=30):
        """Get performance metrics for affiliate links."""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Base query filters
            base_filters = [Tweet.posted_time >= start_date, Tweet.status == 'posted']
            if user_id:
                base_filters.append(Tweet.user_id == user_id)
            
            # Get affiliate link performance
            link_performance = db.session.query(
                AffiliateLink.id,
                AffiliateLink.url,
                AffiliateLink.product_name,
                AffiliateLink.commission_rate,
                func.count(Tweet.id).label('tweet_count'),
                func.sum(TweetPerformance.url_clicks).label('total_clicks'),
                func.sum(TweetPerformance.impressions).label('total_impressions')
            ).join(Tweet, Tweet.affiliate_link_id == AffiliateLink.id)\
             .join(TweetPerformance)\
             .filter(*base_filters)\
             .group_by(AffiliateLink.id)\
             .order_by(func.sum(TweetPerformance.url_clicks).desc()).all()
            
            # Format data
            result = []
            for row in link_performance:
                clicks = int(row.total_clicks or 0)
                impressions = int(row.total_impressions or 0)
                ctr = (clicks / impressions * 100) if impressions > 0 else 0
                
                result.append({
                    'id': row.id,
                    'url': row.url,
                    'product_name': row.product_name,
                    'commission_rate': float(row.commission_rate),
                    'tweet_count': int(row.tweet_count),
                    'total_clicks': clicks,
                    'total_impressions': impressions,
                    'click_through_rate': round(ctr, 2)
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get affiliate link performance: {str(e)}")
            return []
    
    def generate_analytics_report(self, user_id=None, days=30):
        """Generate a comprehensive analytics report."""
        try:
            report = {
                'period': {
                    'days': days,
                    'start_date': (datetime.utcnow() - timedelta(days=days)).isoformat(),
                    'end_date': datetime.utcnow().isoformat()
                },
                'dashboard_stats': self.get_dashboard_stats(user_id, days),
                'engagement_trends': self.get_engagement_trends(user_id, days),
                'top_tweets': self.get_top_performing_tweets(user_id, 5, days),
                'affiliate_performance': self.get_affiliate_link_performance(user_id, days)
            }
            
            # Store report in analytics table
            analytics_record = Analytics(
                user_id=user_id,
                report_type='comprehensive',
                data=report,
                generated_at=datetime.utcnow()
            )
            
            db.session.add(analytics_record)
            db.session.commit()
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate analytics report: {str(e)}")
            return None
    
    def get_performance_comparison(self, user_id=None, current_days=30, previous_days=30):
        """Compare performance between two periods."""
        try:
            # Current period stats
            current_stats = self.get_dashboard_stats(user_id, current_days)
            
            # Previous period stats
            end_date = datetime.utcnow() - timedelta(days=current_days)
            start_date = end_date - timedelta(days=previous_days)
            
            base_filters = [Tweet.created_at >= start_date, Tweet.created_at < end_date]
            if user_id:
                base_filters.append(Tweet.user_id == user_id)
            
            # Previous period calculations
            prev_total_tweets = Tweet.query.filter(*base_filters).count()
            prev_posted_tweets = Tweet.query.filter(
                *base_filters,
                Tweet.status == 'posted'
            ).count()
            
            prev_engagement_query = db.session.query(
                func.sum(TweetPerformance.likes + TweetPerformance.retweets + TweetPerformance.replies).label('total_engagement')
            ).join(Tweet).filter(*base_filters)
            
            prev_total_engagement = prev_engagement_query.scalar() or 0
            
            # Calculate percentage changes
            def calc_change(current, previous):
                if previous == 0:
                    return 100 if current > 0 else 0
                return ((current - previous) / previous) * 100
            
            comparison = {
                'current_period': current_stats,
                'previous_period': {
                    'total_tweets': prev_total_tweets,
                    'posted_tweets': prev_posted_tweets,
                    'total_engagement': int(prev_total_engagement)
                },
                'changes': {
                    'tweets_change': round(calc_change(current_stats['total_tweets'], prev_total_tweets), 2),
                    'posted_change': round(calc_change(current_stats['posted_tweets'], prev_posted_tweets), 2),
                    'engagement_change': round(calc_change(current_stats['total_engagement'], prev_total_engagement), 2)
                }
            }
            
            return comparison
            
        except Exception as e:
            logger.error(f"Failed to get performance comparison: {str(e)}")
            return None

# Global instance
analytics_service = AnalyticsService()

def get_analytics():
    """Get the global analytics service instance."""
    return analytics_service