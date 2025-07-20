from app import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON
from .tweet import Tweet

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(100), nullable=True)
    website = db.Column(db.String(200), nullable=True)
    profile_image_url = db.Column(db.String(500), nullable=True)
    banner_image_url = db.Column(db.String(500), nullable=True)
    
    # Counts
    followers_count = db.Column(db.Integer, default=0)
    following_count = db.Column(db.Integer, default=0)
    tweets_count = db.Column(db.Integer, default=0)
    likes_count = db.Column(db.Integer, default=0)
    
    # Verification and status
    verified = db.Column(db.Boolean, default=False)
    protected = db.Column(db.Boolean, default=False)
    
    # Timestamps
    joined_date = db.Column(db.DateTime, nullable=True)
    last_scraped = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Additional data
    additional_data = db.Column(JSON, nullable=True)
    
    # Relationships
    tweets = db.relationship('Tweet', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    posts = db.relationship('Post', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def to_dict(self, include_tweets=False):
        user_data = {
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'bio': self.bio,
            'location': self.location,
            'website': self.website,
            'profile_image_url': self.profile_image_url,
            'banner_image_url': self.banner_image_url,
            'followers_count': self.followers_count,
            'following_count': self.following_count,
            'tweets_count': self.tweets_count,
            'likes_count': self.likes_count,
            'verified': self.verified,
            'protected': self.protected,
            'joined_date': self.joined_date.isoformat() if self.joined_date else None,
            'last_scraped': self.last_scraped.isoformat() if self.last_scraped else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'additional_data': self.additional_data
        }

        if include_tweets:
            user_data['tweets'] = [tweet.to_dict() for tweet in self.tweets.order_by(Tweet.posted_at.desc()).all()]

        return user_data
