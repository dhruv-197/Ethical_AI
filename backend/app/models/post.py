from app import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON

class Post(db.Model):
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Post content
    caption = db.Column(db.Text, nullable=True)
    media_type = db.Column(db.String(20), nullable=False)  # photo, video, carousel
    media_url = db.Column(db.String(500), nullable=False)
    thumbnail_url = db.Column(db.String(500), nullable=True)
    
    # Engagement metrics
    like_count = db.Column(db.Integer, default=0)
    comment_count = db.Column(db.Integer, default=0)
    share_count = db.Column(db.Integer, default=0)
    
    # Timestamps
    posted_at = db.Column(db.DateTime, nullable=False)
    scraped_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Additional data
    additional_data = db.Column(JSON, nullable=True)
    
    def __repr__(self):
        return f'<Post {self.post_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'post_id': self.post_id,
            'user_id': self.user_id,
            'caption': self.caption,
            'media_type': self.media_type,
            'media_url': self.media_url,
            'thumbnail_url': self.thumbnail_url,
            'like_count': self.like_count,
            'comment_count': self.comment_count,
            'share_count': self.share_count,
            'posted_at': self.posted_at.isoformat(),
            'scraped_at': self.scraped_at.isoformat(),
            'additional_data': self.additional_data
        }