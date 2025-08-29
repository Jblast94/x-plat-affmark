from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Campaign, Tweet, TweetPerformance, AffiliateLink, Analytics, db
from auth import get_current_user
from analytics_service import get_analytics
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    """Get dashboard statistics for the current user."""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get date range from query parameters
        days = request.args.get('days', 30, type=int)
        
        analytics_service = get_analytics()
        stats = analytics_service.get_dashboard_stats(user.id, days)
        
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"Get dashboard stats error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@analytics_bp.route('/engagement-trends', methods=['GET'])
@jwt_required()
def get_engagement_trends():
    """Get engagement trends over time."""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get parameters
        days = request.args.get('days', 30, type=int)
        granularity = request.args.get('granularity', 'daily')  # daily, weekly, monthly
        
        if granularity not in ['daily', 'weekly', 'monthly']:
            return jsonify({'error': 'Invalid granularity. Use daily, weekly, or monthly'}), 400
        
        analytics_service = get_analytics()
        trends = analytics_service.get_engagement_trends(user.id, days, granularity)
        
        return jsonify({
            'trends': trends,
            'period': f'{days} days',
            'granularity': granularity
        }), 200
        
    except Exception as e:
        logger.error(f"Get engagement trends error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@analytics_bp.route('/top-tweets', methods=['GET'])
@jwt_required()
def get_top_tweets():
    """Get top performing tweets."""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get parameters
        days = request.args.get('days', 30, type=int)
        limit = request.args.get('limit', 10, type=int)
        metric = request.args.get('metric', 'engagement_rate')  # likes, retweets, replies, engagement_rate
        
        valid_metrics = ['likes', 'retweets', 'replies', 'engagement_rate', 'impressions']
        if metric not in valid_metrics:
            return jsonify({'error': f'Invalid metric. Use one of: {", ".join(valid_metrics)}'}), 400
        
        analytics_service = get_analytics()
        top_tweets = analytics_service.get_top_performing_tweets(user.id, days, limit, metric)
        
        return jsonify({
            'top_tweets': top_tweets,
            'metric': metric,
            'period': f'{days} days',
            'limit': limit
        }), 200
        
    except Exception as e:
        logger.error(f"Get top tweets error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@analytics_bp.route('/campaign-performance', methods=['GET'])
@jwt_required()
def get_campaign_performance():
    """Get performance metrics for all campaigns."""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get parameters
        days = request.args.get('days', 30, type=int)
        campaign_id = request.args.get('campaign_id', type=int)
        
        analytics_service = get_analytics_service()
        
        if campaign_id:
            # Get specific campaign performance
            campaign = Campaign.query.filter_by(id=campaign_id, user_id=user.id).first()
            if not campaign:
                return jsonify({'error': 'Campaign not found'}), 404
            
            performance = analytics_service.get_campaign_performance(user.id, days, campaign_id)
            return jsonify({
                'campaign': campaign.to_dict(),
                'performance': performance
            }), 200
        else:
            # Get all campaigns performance
            performance = analytics_service.get_campaign_performance(user.id, days)
            return jsonify({
                'campaigns_performance': performance,
                'period': f'{days} days'
            }), 200
        
    except Exception as e:
        logger.error(f"Get campaign performance error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@analytics_bp.route('/affiliate-performance', methods=['GET'])
@jwt_required()
def get_affiliate_performance():
    """Get performance metrics for affiliate links."""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get parameters
        days = request.args.get('days', 30, type=int)
        affiliate_link_id = request.args.get('affiliate_link_id', type=int)
        
        analytics_service = get_analytics_service()
        
        if affiliate_link_id:
            # Get specific affiliate link performance
            affiliate_link = AffiliateLink.query.get(affiliate_link_id)
            if not affiliate_link:
                return jsonify({'error': 'Affiliate link not found'}), 404
            
            performance = analytics_service.get_affiliate_link_performance(user.id, days, affiliate_link_id)
            return jsonify({
                'affiliate_link': affiliate_link.to_dict(),
                'performance': performance
            }), 200
        else:
            # Get all affiliate links performance
            performance = analytics_service.get_affiliate_link_performance(user.id, days)
            return jsonify({
                'affiliate_links_performance': performance,
                'period': f'{days} days'
            }), 200
        
    except Exception as e:
        logger.error(f"Get affiliate performance error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@analytics_bp.route('/reports', methods=['GET'])
@jwt_required()
def get_analytics_report():
    """Generate comprehensive analytics report."""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get parameters
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        report_type = request.args.get('type', 'summary')  # summary, detailed, campaign, affiliate
        
        # Parse dates
        try:
            if start_date_str:
                start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
            else:
                start_date = datetime.utcnow() - timedelta(days=30)
            
            if end_date_str:
                end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
            else:
                end_date = datetime.utcnow()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use ISO format'}), 400
        
        if start_date >= end_date:
            return jsonify({'error': 'Start date must be before end date'}), 400
        
        analytics_service = get_analytics_service()
        report = analytics_service.generate_analytics_report(user.id, start_date, end_date, report_type)
        
        return jsonify({
            'report': report,
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'type': report_type
        }), 200
        
    except Exception as e:
        logger.error(f"Get analytics report error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@analytics_bp.route('/compare', methods=['GET'])
@jwt_required()
def compare_periods():
    """Compare performance between two time periods."""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get parameters
        period1_start = request.args.get('period1_start')
        period1_end = request.args.get('period1_end')
        period2_start = request.args.get('period2_start')
        period2_end = request.args.get('period2_end')
        
        if not all([period1_start, period1_end, period2_start, period2_end]):
            return jsonify({'error': 'All period dates are required'}), 400
        
        # Parse dates
        try:
            period1_start_date = datetime.fromisoformat(period1_start.replace('Z', '+00:00'))
            period1_end_date = datetime.fromisoformat(period1_end.replace('Z', '+00:00'))
            period2_start_date = datetime.fromisoformat(period2_start.replace('Z', '+00:00'))
            period2_end_date = datetime.fromisoformat(period2_end.replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use ISO format'}), 400
        
        analytics_service = get_analytics_service()
        comparison = analytics_service.compare_periods(
            user.id,
            period1_start_date, period1_end_date,
            period2_start_date, period2_end_date
        )
        
        return jsonify({
            'comparison': comparison,
            'period1': {
                'start': period1_start_date.isoformat(),
                'end': period1_end_date.isoformat()
            },
            'period2': {
                'start': period2_start_date.isoformat(),
                'end': period2_end_date.isoformat()
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Compare periods error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@analytics_bp.route('/export', methods=['POST'])
@jwt_required()
def export_analytics():
    """Export analytics data in various formats."""
    try:
        user = get_current_user()
        data = request.get_json()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get parameters
        export_format = data.get('format', 'json')  # json, csv
        data_type = data.get('data_type', 'summary')  # summary, tweets, campaigns, affiliate_links
        start_date_str = data.get('start_date')
        end_date_str = data.get('end_date')
        
        if export_format not in ['json', 'csv']:
            return jsonify({'error': 'Invalid format. Use json or csv'}), 400
        
        if data_type not in ['summary', 'tweets', 'campaigns', 'affiliate_links']:
            return jsonify({'error': 'Invalid data_type'}), 400
        
        # Parse dates
        try:
            if start_date_str:
                start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
            else:
                start_date = datetime.utcnow() - timedelta(days=30)
            
            if end_date_str:
                end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
            else:
                end_date = datetime.utcnow()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use ISO format'}), 400
        
        analytics_service = get_analytics_service()
        
        # Generate export data based on type
        if data_type == 'summary':
            export_data = analytics_service.generate_analytics_report(user.id, start_date, end_date, 'summary')
        elif data_type == 'tweets':
            # Get tweet performance data
            tweets = Tweet.query.filter(
                Tweet.user_id == user.id,
                Tweet.posted_time >= start_date,
                Tweet.posted_time <= end_date,
                Tweet.status == 'posted'
            ).all()
            
            export_data = []
            for tweet in tweets:
                tweet_data = tweet.to_dict()
                performance = TweetPerformance.query.filter_by(tweet_id=tweet.tweet_id).first()
                if performance:
                    tweet_data['performance'] = performance.to_dict()
                export_data.append(tweet_data)
        
        elif data_type == 'campaigns':
            campaigns = Campaign.query.filter_by(user_id=user.id).all()
            export_data = []
            for campaign in campaigns:
                campaign_data = campaign.to_dict()
                performance = analytics_service.get_campaign_performance(user.id, 30, campaign.id)
                campaign_data['performance'] = performance
                export_data.append(campaign_data)
        
        elif data_type == 'affiliate_links':
            affiliate_links = AffiliateLink.query.all()
            export_data = []
            for link in affiliate_links:
                link_data = link.to_dict()
                performance = analytics_service.get_affiliate_link_performance(user.id, 30, link.id)
                link_data['performance'] = performance
                export_data.append(link_data)
        
        # Format response based on export format
        if export_format == 'json':
            return jsonify({
                'data': export_data,
                'metadata': {
                    'export_date': datetime.utcnow().isoformat(),
                    'data_type': data_type,
                    'period': {
                        'start': start_date.isoformat(),
                        'end': end_date.isoformat()
                    },
                    'total_records': len(export_data) if isinstance(export_data, list) else 1
                }
            }), 200
        
        elif export_format == 'csv':
            # For CSV, we'll return a simplified structure
            # In a real implementation, you'd use pandas or csv module
            return jsonify({
                'message': 'CSV export functionality would be implemented here',
                'data_preview': export_data[:5] if isinstance(export_data, list) else export_data,
                'total_records': len(export_data) if isinstance(export_data, list) else 1
            }), 200
        
    except Exception as e:
        logger.error(f"Export analytics error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@analytics_bp.route('/refresh', methods=['POST'])
@jwt_required()
def refresh_analytics():
    """Refresh analytics data by fetching latest metrics from X API."""
    try:
        user = get_current_user()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check X API configuration
        if not (user.x_api_key and user.x_api_secret):
            return jsonify({'error': 'X API credentials not configured'}), 400
        
        # Get all posted tweets for the user
        posted_tweets = Tweet.query.filter(
            Tweet.user_id == user.id,
            Tweet.status == 'posted',
            Tweet.tweet_id.isnot(None)
        ).all()
        
        if not posted_tweets:
            return jsonify({
                'message': 'No posted tweets found to refresh',
                'updated_count': 0
            }), 200
        
        # Update performance for each tweet
        from x_api_service import get_x_api
        x_api = get_x_api()
        
        updated_count = 0
        failed_count = 0
        
        for tweet in posted_tweets:
            try:
                if x_api.update_tweet_performance(tweet.tweet_id):
                    updated_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                logger.error(f"Failed to update performance for tweet {tweet.tweet_id}: {str(e)}")
                failed_count += 1
        
        return jsonify({
            'message': 'Analytics refresh completed',
            'updated_count': updated_count,
            'failed_count': failed_count,
            'total_tweets': len(posted_tweets)
        }), 200
        
    except Exception as e:
        logger.error(f"Refresh analytics error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@analytics_bp.route('/metrics/summary', methods=['GET'])
@jwt_required()
def get_metrics_summary():
    """Get a quick summary of key metrics."""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get basic counts
        total_campaigns = Campaign.query.filter_by(user_id=user.id).count()
        total_tweets = Tweet.query.filter_by(user_id=user.id).count()
        posted_tweets = Tweet.query.filter_by(user_id=user.id, status='posted').count()
        scheduled_tweets = Tweet.query.filter_by(user_id=user.id, status='scheduled').count()
        
        # Get performance metrics for posted tweets
        performance_query = db.session.query(
            db.func.sum(TweetPerformance.likes).label('total_likes'),
            db.func.sum(TweetPerformance.retweets).label('total_retweets'),
            db.func.sum(TweetPerformance.replies).label('total_replies'),
            db.func.sum(TweetPerformance.impressions).label('total_impressions'),
            db.func.avg(TweetPerformance.engagement_rate).label('avg_engagement_rate')
        ).join(Tweet, TweetPerformance.tweet_id == Tweet.tweet_id).filter(
            Tweet.user_id == user.id
        ).first()
        
        summary = {
            'campaigns': {
                'total': total_campaigns,
                'active': Campaign.query.filter_by(user_id=user.id, status='active').count()
            },
            'tweets': {
                'total': total_tweets,
                'posted': posted_tweets,
                'scheduled': scheduled_tweets,
                'draft': Tweet.query.filter_by(user_id=user.id, status='draft').count()
            },
            'performance': {
                'total_likes': int(performance_query.total_likes or 0),
                'total_retweets': int(performance_query.total_retweets or 0),
                'total_replies': int(performance_query.total_replies or 0),
                'total_impressions': int(performance_query.total_impressions or 0),
                'avg_engagement_rate': float(performance_query.avg_engagement_rate or 0)
            },
            'last_updated': datetime.utcnow().isoformat()
        }
        
        return jsonify(summary), 200
        
    except Exception as e:
        logger.error(f"Get metrics summary error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500