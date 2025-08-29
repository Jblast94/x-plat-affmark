from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import AffiliateLink, Tweet, TweetPerformance, db
from auth import get_current_user, require_role
import logging
from datetime import datetime
from urllib.parse import urlparse
import re

logger = logging.getLogger(__name__)
affiliate_bp = Blueprint('affiliate_links', __name__)

@affiliate_bp.route('/', methods=['GET'])
@jwt_required()
def get_affiliate_links():
    """Get all affiliate links."""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        category = request.args.get('category')
        active_only = request.args.get('active_only', 'false').lower() == 'true'
        search = request.args.get('search')
        
        # Build query
        query = AffiliateLink.query
        
        if category:
            query = query.filter_by(category=category)
        
        if active_only:
            query = query.filter_by(is_active=True)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                db.or_(
                    AffiliateLink.product_name.ilike(search_term),
                    AffiliateLink.brand.ilike(search_term),
                    AffiliateLink.description.ilike(search_term)
                )
            )
        
        # Paginate results
        affiliate_links = query.order_by(AffiliateLink.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Format response
        result = {
            'affiliate_links': [link.to_dict() for link in affiliate_links.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': affiliate_links.total,
                'pages': affiliate_links.pages,
                'has_next': affiliate_links.has_next,
                'has_prev': affiliate_links.has_prev
            }
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Get affiliate links error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@affiliate_bp.route('/', methods=['POST'])
@jwt_required()
@require_role('admin')
def create_affiliate_link():
    """Create a new affiliate link (admin only)."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request data is required'}), 400
        
        # Validate required fields
        required_fields = ['product_name', 'affiliate_url', 'commission_rate']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate URL format
        try:
            parsed_url = urlparse(data['affiliate_url'])
            if not all([parsed_url.scheme, parsed_url.netloc]):
                return jsonify({'error': 'Invalid affiliate URL format'}), 400
        except Exception:
            return jsonify({'error': 'Invalid affiliate URL format'}), 400
        
        # Validate commission rate
        try:
            commission_rate = float(data['commission_rate'])
            if commission_rate < 0 or commission_rate > 100:
                return jsonify({'error': 'Commission rate must be between 0 and 100'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid commission rate format'}), 400
        
        # Check for duplicate affiliate URL
        existing_link = AffiliateLink.query.filter_by(affiliate_url=data['affiliate_url']).first()
        if existing_link:
            return jsonify({'error': 'Affiliate link with this URL already exists'}), 409
        
        # Create affiliate link
        affiliate_link = AffiliateLink(
            product_name=data['product_name'],
            brand=data.get('brand', ''),
            category=data.get('category', 'general'),
            affiliate_url=data['affiliate_url'],
            commission_rate=commission_rate,
            description=data.get('description', ''),
            image_url=data.get('image_url', ''),
            price=data.get('price'),
            currency=data.get('currency', 'USD'),
            tags=data.get('tags', []),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(affiliate_link)
        db.session.commit()
        
        return jsonify({
            'message': 'Affiliate link created successfully',
            'affiliate_link': affiliate_link.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Create affiliate link error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@affiliate_bp.route('/<int:link_id>', methods=['GET'])
@jwt_required()
def get_affiliate_link(link_id):
    """Get a specific affiliate link."""
    try:
        affiliate_link = AffiliateLink.query.get(link_id)
        
        if not affiliate_link:
            return jsonify({'error': 'Affiliate link not found'}), 404
        
        # Get usage statistics
        user = get_current_user()
        if user:
            # Get tweets using this affiliate link by current user
            user_tweets = Tweet.query.filter_by(
                user_id=user.id,
                affiliate_link_id=link_id
            ).all()
            
            usage_stats = {
                'total_tweets': len(user_tweets),
                'posted_tweets': len([t for t in user_tweets if t.status == 'posted']),
                'scheduled_tweets': len([t for t in user_tweets if t.status == 'scheduled'])
            }
        else:
            usage_stats = None
        
        result = affiliate_link.to_dict()
        if usage_stats:
            result['usage_stats'] = usage_stats
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Get affiliate link error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@affiliate_bp.route('/<int:link_id>', methods=['PUT'])
@jwt_required()
@require_role('admin')
def update_affiliate_link(link_id):
    """Update an affiliate link (admin only)."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request data is required'}), 400
        
        affiliate_link = AffiliateLink.query.get(link_id)
        
        if not affiliate_link:
            return jsonify({'error': 'Affiliate link not found'}), 404
        
        # Update allowed fields
        if 'product_name' in data:
            affiliate_link.product_name = data['product_name']
        
        if 'brand' in data:
            affiliate_link.brand = data['brand']
        
        if 'category' in data:
            affiliate_link.category = data['category']
        
        if 'affiliate_url' in data:
            # Validate URL format
            try:
                parsed_url = urlparse(data['affiliate_url'])
                if not all([parsed_url.scheme, parsed_url.netloc]):
                    return jsonify({'error': 'Invalid affiliate URL format'}), 400
            except Exception:
                return jsonify({'error': 'Invalid affiliate URL format'}), 400
            
            # Check for duplicate URL (excluding current link)
            existing_link = AffiliateLink.query.filter(
                AffiliateLink.affiliate_url == data['affiliate_url'],
                AffiliateLink.id != link_id
            ).first()
            if existing_link:
                return jsonify({'error': 'Affiliate link with this URL already exists'}), 409
            
            affiliate_link.affiliate_url = data['affiliate_url']
        
        if 'commission_rate' in data:
            try:
                commission_rate = float(data['commission_rate'])
                if commission_rate < 0 or commission_rate > 100:
                    return jsonify({'error': 'Commission rate must be between 0 and 100'}), 400
                affiliate_link.commission_rate = commission_rate
            except (ValueError, TypeError):
                return jsonify({'error': 'Invalid commission rate format'}), 400
        
        if 'description' in data:
            affiliate_link.description = data['description']
        
        if 'image_url' in data:
            affiliate_link.image_url = data['image_url']
        
        if 'price' in data:
            affiliate_link.price = data['price']
        
        if 'currency' in data:
            affiliate_link.currency = data['currency']
        
        if 'tags' in data:
            affiliate_link.tags = data['tags']
        
        if 'is_active' in data:
            affiliate_link.is_active = data['is_active']
        
        affiliate_link.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Affiliate link updated successfully',
            'affiliate_link': affiliate_link.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Update affiliate link error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@affiliate_bp.route('/<int:link_id>', methods=['DELETE'])
@jwt_required()
@require_role('admin')
def delete_affiliate_link(link_id):
    """Delete an affiliate link (admin only)."""
    try:
        affiliate_link = AffiliateLink.query.get(link_id)
        
        if not affiliate_link:
            return jsonify({'error': 'Affiliate link not found'}), 404
        
        # Check if link is being used in any tweets
        tweets_using_link = Tweet.query.filter_by(affiliate_link_id=link_id).count()
        
        if tweets_using_link > 0:
            return jsonify({
                'error': f'Cannot delete affiliate link. It is being used in {tweets_using_link} tweet(s)'
            }), 409
        
        db.session.delete(affiliate_link)
        db.session.commit()
        
        return jsonify({'message': 'Affiliate link deleted successfully'}), 200
        
    except Exception as e:
        logger.error(f"Delete affiliate link error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@affiliate_bp.route('/<int:link_id>/toggle-status', methods=['POST'])
@jwt_required()
@require_role('admin')
def toggle_affiliate_link_status(link_id):
    """Toggle the active status of an affiliate link (admin only)."""
    try:
        affiliate_link = AffiliateLink.query.get(link_id)
        
        if not affiliate_link:
            return jsonify({'error': 'Affiliate link not found'}), 404
        
        affiliate_link.is_active = not affiliate_link.is_active
        affiliate_link.updated_at = datetime.utcnow()
        db.session.commit()
        
        status = 'activated' if affiliate_link.is_active else 'deactivated'
        
        return jsonify({
            'message': f'Affiliate link {status} successfully',
            'affiliate_link': affiliate_link.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Toggle affiliate link status error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@affiliate_bp.route('/<int:link_id>/performance', methods=['GET'])
@jwt_required()
def get_affiliate_link_performance(link_id):
    """Get performance metrics for a specific affiliate link."""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        affiliate_link = AffiliateLink.query.get(link_id)
        
        if not affiliate_link:
            return jsonify({'error': 'Affiliate link not found'}), 404
        
        # Get date range from query parameters
        days = request.args.get('days', 30, type=int)
        
        # Get tweets using this affiliate link by current user
        tweets = Tweet.query.filter_by(
            user_id=user.id,
            affiliate_link_id=link_id,
            status='posted'
        ).filter(
            Tweet.posted_time >= datetime.utcnow() - timedelta(days=days)
        ).all()
        
        if not tweets:
            return jsonify({
                'affiliate_link': affiliate_link.to_dict(),
                'performance': {
                    'total_tweets': 0,
                    'total_likes': 0,
                    'total_retweets': 0,
                    'total_replies': 0,
                    'total_impressions': 0,
                    'avg_engagement_rate': 0,
                    'estimated_clicks': 0,
                    'estimated_revenue': 0
                },
                'period_days': days
            }), 200
        
        # Calculate performance metrics
        total_tweets = len(tweets)
        total_likes = 0
        total_retweets = 0
        total_replies = 0
        total_impressions = 0
        engagement_rates = []
        
        for tweet in tweets:
            if tweet.tweet_id:
                performance = TweetPerformance.query.filter_by(tweet_id=tweet.tweet_id).first()
                if performance:
                    total_likes += performance.likes
                    total_retweets += performance.retweets
                    total_replies += performance.replies
                    total_impressions += performance.impressions
                    if performance.engagement_rate:
                        engagement_rates.append(performance.engagement_rate)
        
        avg_engagement_rate = sum(engagement_rates) / len(engagement_rates) if engagement_rates else 0
        
        # Estimate clicks (assuming 2% click-through rate on impressions)
        estimated_clicks = int(total_impressions * 0.02)
        
        # Estimate revenue (clicks * commission rate * average order value)
        # Assuming average order value of $50 for estimation
        estimated_revenue = estimated_clicks * (affiliate_link.commission_rate / 100) * 50
        
        performance_data = {
            'total_tweets': total_tweets,
            'total_likes': total_likes,
            'total_retweets': total_retweets,
            'total_replies': total_replies,
            'total_impressions': total_impressions,
            'avg_engagement_rate': round(avg_engagement_rate, 2),
            'estimated_clicks': estimated_clicks,
            'estimated_revenue': round(estimated_revenue, 2)
        }
        
        return jsonify({
            'affiliate_link': affiliate_link.to_dict(),
            'performance': performance_data,
            'period_days': days
        }), 200
        
    except Exception as e:
        logger.error(f"Get affiliate link performance error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@affiliate_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    """Get all available affiliate link categories."""
    try:
        # Get distinct categories from existing affiliate links
        categories = db.session.query(AffiliateLink.category).distinct().all()
        category_list = [cat[0] for cat in categories if cat[0]]
        
        # Add some default categories if none exist
        default_categories = [
            'technology', 'fashion', 'health', 'fitness', 'beauty',
            'home', 'books', 'electronics', 'travel', 'food',
            'automotive', 'sports', 'gaming', 'education', 'general'
        ]
        
        # Combine and deduplicate
        all_categories = list(set(category_list + default_categories))
        all_categories.sort()
        
        return jsonify({
            'categories': all_categories,
            'total': len(all_categories)
        }), 200
        
    except Exception as e:
        logger.error(f"Get categories error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@affiliate_bp.route('/search', methods=['GET'])
@jwt_required()
def search_affiliate_links():
    """Search affiliate links by various criteria."""
    try:
        # Get search parameters
        query_text = request.args.get('q', '')
        category = request.args.get('category')
        min_commission = request.args.get('min_commission', type=float)
        max_commission = request.args.get('max_commission', type=float)
        brand = request.args.get('brand')
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        limit = request.args.get('limit', 20, type=int)
        
        # Build query
        query = AffiliateLink.query
        
        if active_only:
            query = query.filter_by(is_active=True)
        
        if query_text:
            search_term = f"%{query_text}%"
            query = query.filter(
                db.or_(
                    AffiliateLink.product_name.ilike(search_term),
                    AffiliateLink.brand.ilike(search_term),
                    AffiliateLink.description.ilike(search_term),
                    AffiliateLink.tags.contains([query_text.lower()])
                )
            )
        
        if category:
            query = query.filter_by(category=category)
        
        if brand:
            query = query.filter(AffiliateLink.brand.ilike(f"%{brand}%"))
        
        if min_commission is not None:
            query = query.filter(AffiliateLink.commission_rate >= min_commission)
        
        if max_commission is not None:
            query = query.filter(AffiliateLink.commission_rate <= max_commission)
        
        # Execute query with limit
        results = query.order_by(AffiliateLink.commission_rate.desc()).limit(limit).all()
        
        return jsonify({
            'results': [link.to_dict() for link in results],
            'total_found': len(results),
            'search_params': {
                'query': query_text,
                'category': category,
                'brand': brand,
                'min_commission': min_commission,
                'max_commission': max_commission,
                'active_only': active_only
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Search affiliate links error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@affiliate_bp.route('/bulk-import', methods=['POST'])
@jwt_required()
@require_role('admin')
def bulk_import_affiliate_links():
    """Bulk import affiliate links (admin only)."""
    try:
        data = request.get_json()
        
        if not data or not data.get('links'):
            return jsonify({'error': 'Links data is required'}), 400
        
        links_data = data['links']
        if not isinstance(links_data, list):
            return jsonify({'error': 'Links must be an array'}), 400
        
        created_links = []
        failed_links = []
        
        for i, link_data in enumerate(links_data):
            try:
                # Validate required fields
                required_fields = ['product_name', 'affiliate_url', 'commission_rate']
                for field in required_fields:
                    if not link_data.get(field):
                        failed_links.append({
                            'index': i,
                            'data': link_data,
                            'error': f'{field} is required'
                        })
                        continue
                
                # Validate URL format
                try:
                    parsed_url = urlparse(link_data['affiliate_url'])
                    if not all([parsed_url.scheme, parsed_url.netloc]):
                        failed_links.append({
                            'index': i,
                            'data': link_data,
                            'error': 'Invalid affiliate URL format'
                        })
                        continue
                except Exception:
                    failed_links.append({
                        'index': i,
                        'data': link_data,
                        'error': 'Invalid affiliate URL format'
                    })
                    continue
                
                # Validate commission rate
                try:
                    commission_rate = float(link_data['commission_rate'])
                    if commission_rate < 0 or commission_rate > 100:
                        failed_links.append({
                            'index': i,
                            'data': link_data,
                            'error': 'Commission rate must be between 0 and 100'
                        })
                        continue
                except (ValueError, TypeError):
                    failed_links.append({
                        'index': i,
                        'data': link_data,
                        'error': 'Invalid commission rate format'
                    })
                    continue
                
                # Check for duplicate URL
                existing_link = AffiliateLink.query.filter_by(
                    affiliate_url=link_data['affiliate_url']
                ).first()
                if existing_link:
                    failed_links.append({
                        'index': i,
                        'data': link_data,
                        'error': 'Affiliate link with this URL already exists'
                    })
                    continue
                
                # Create affiliate link
                affiliate_link = AffiliateLink(
                    product_name=link_data['product_name'],
                    brand=link_data.get('brand', ''),
                    category=link_data.get('category', 'general'),
                    affiliate_url=link_data['affiliate_url'],
                    commission_rate=commission_rate,
                    description=link_data.get('description', ''),
                    image_url=link_data.get('image_url', ''),
                    price=link_data.get('price'),
                    currency=link_data.get('currency', 'USD'),
                    tags=link_data.get('tags', []),
                    is_active=link_data.get('is_active', True)
                )
                
                db.session.add(affiliate_link)
                created_links.append(affiliate_link)
                
            except Exception as e:
                failed_links.append({
                    'index': i,
                    'data': link_data,
                    'error': str(e)
                })
        
        # Commit all successful creations
        if created_links:
            db.session.commit()
        
        return jsonify({
            'message': f'Bulk import completed: {len(created_links)} created, {len(failed_links)} failed',
            'created_count': len(created_links),
            'failed_count': len(failed_links),
            'created_links': [link.to_dict() for link in created_links],
            'failed_links': failed_links
        }), 200
        
    except Exception as e:
        logger.error(f"Bulk import affiliate links error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500