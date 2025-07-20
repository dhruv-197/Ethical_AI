from app import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON
import json

class Tweet(db.Model):
    __tablename__ = 'tweets'
    
    id = db.Column(db.Integer, primary_key=True)
    tweet_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Tweet content
    text = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(10), nullable=True)
    
    # Media and URLs
    media_urls = db.Column(db.Text)  # JSON string of URLs
    local_media_paths = db.Column(db.Text)  # JSON string of local file paths
    urls = db.Column(db.JSON, nullable=True)  # Array of expanded URLs
    hashtags = db.Column(db.JSON, nullable=True)  # Array of hashtags
    
    # Timestamp
    posted_at = db.Column(db.DateTime, nullable=False)
    
    def __repr__(self):
        return f'<Tweet {self.tweet_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'tweet_id': self.tweet_id,
            'user_id': self.user_id,
            'text': self.text,
            'language': self.language,
            'urls': self.urls,
            'hashtags': self.hashtags,
            'posted_at': self.posted_at.isoformat() if self.posted_at else None,
            'media_urls': json.loads(self.media_urls) if self.media_urls else [],
            'local_media_paths': json.loads(self.local_media_paths) if self.local_media_paths else [],
        }