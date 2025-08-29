from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    """User model for authentication and authorization."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='admin', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # X API credentials
    x_api_key = db.Column(db.String(255))
    x_api_secret = db.Column(db.String(255))
    x_access_token = db.Column(db.String(255))
    x_access_token_secret = db.Column(db.String(255))
    
    # Relationships
    campaigns = db.relationship('Campaign', backref='user', lazy=True)
    
    def set_password(self, password):
        """Hash and set password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash."""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat()
        }

class Campaign(db.Model):
    """Campaign model for organizing marketing campaigns."""
    __tablename__ = 'campaigns'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    niche = db.Column(db.String(50), nullable=False)
    schedule_config = db.Column(db.Text, nullable=False)  # JSON string
    status = db.Column(db.String(20), default='active', nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tweets = db.relationship('Tweet', backref='campaign', lazy=True, cascade='all, delete-orphan')
    analytics = db.relationship('Analytics', backref='campaign', lazy=True, cascade='all, delete-orphan')
    
    @property
    def schedule(self):
        """Parse schedule configuration from JSON."""
        try:
            return json.loads(self.schedule_config)
        except (json.JSONDecodeError, TypeError):
            return {}
    
    @schedule.setter
    def schedule(self, value):
        """Set schedule configuration as JSON."""
        self.schedule_config = json.dumps(value)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'niche': self.niche,
            'schedule': self.schedule,
            'status': self.status,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class AffiliateLink(db.Model):
    """Affiliate link model for tracking and UTM parameters."""
    __tablename__ = 'affiliate_links'
    
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.Text, nullable=False)
    utm_source = db.Column(db.String(50), default='x_ads')
    utm_medium = db.Column(db.String(50), default='social')
    utm_campaign = db.Column(db.String(100))
    tracked_url = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    tweets = db.relationship('Tweet', backref='affiliate_link', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'original_url': self.original_url,
            'utm_source': self.utm_source,
            'utm_medium': self.utm_medium,
            'utm_campaign': self.utm_campaign,
            'tracked_url': self.tracked_url,
            'created_at': self.created_at.isoformat()
        }

class Tweet(db.Model):
    """Tweet model for scheduled and posted content."""
    __tablename__ = 'tweets'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    media_urls = db.Column(db.Text)  # JSON array of media URLs
    scheduled_time = db.Column(db.DateTime, nullable=False)
    posted_time = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='scheduled', nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)
    affiliate_link_id = db.Column(db.Integer, db.ForeignKey('affiliate_links.id'))
    tweet_id = db.Column(db.String(50))  # X tweet ID after posting
    
    # Relationships
    performance = db.relationship('TweetPerformance', backref='tweet', lazy=True, cascade='all, delete-orphan')
    
    @property
    def media(self):
        """Parse media URLs from JSON."""
        try:
            return json.loads(self.media_urls) if self.media_urls else []
        except (json.JSONDecodeError, TypeError):
            return []
    
    @media.setter
    def media(self, value):
        """Set media URLs as JSON."""
        self.media_urls = json.dumps(value) if value else None
    
    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'media': self.media,
            'scheduled_time': self.scheduled_time.isoformat(),
            'posted_time': self.posted_time.isoformat() if self.posted_time else None,
            'status': self.status,
            'campaign_id': self.campaign_id,
            'affiliate_link_id': self.affiliate_link_id,
            'tweet_id': self.tweet_id
        }

class TweetPerformance(db.Model):
    """Tweet performance metrics model."""
    __tablename__ = 'tweet_performance'
    
    id = db.Column(db.Integer, primary_key=True)
    tweet_id = db.Column(db.Integer, db.ForeignKey('tweets.id'), nullable=False)
    impressions = db.Column(db.Integer, default=0)
    clicks = db.Column(db.Integer, default=0)
    retweets = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)
    replies = db.Column(db.Integer, default=0)
    engagement_rate = db.Column(db.Float, default=0.0)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'tweet_id': self.tweet_id,
            'impressions': self.impressions,
            'clicks': self.clicks,
            'retweets': self.retweets,
            'likes': self.likes,
            'replies': self.replies,
            'engagement_rate': self.engagement_rate,
            'recorded_at': self.recorded_at.isoformat()
        }

class Analytics(db.Model):
    """Daily analytics aggregation model."""
    __tablename__ = 'analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)
    analytics_date = db.Column(db.Date, nullable=False)
    total_impressions = db.Column(db.Integer, default=0)
    total_clicks = db.Column(db.Integer, default=0)
    total_revenue = db.Column(db.Float, default=0.0)
    conversion_rate = db.Column(db.Float, default=0.0)
    
    __table_args__ = (db.UniqueConstraint('campaign_id', 'analytics_date'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'analytics_date': self.analytics_date.isoformat(),
            'total_impressions': self.total_impressions,
            'total_clicks': self.total_clicks,
            'total_revenue': self.total_revenue,
            'conversion_rate': self.conversion_rate
        }