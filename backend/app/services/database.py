from app import db
from app.models.user import User
from app.models.tweet import Tweet
from app.models.post import Post
from datetime import datetime, timedelta
from typing import List, Optional, Tuple, Dict
import logging
import json

logger = logging.getLogger(__name__)

class DatabaseService:
    def save_user(self, user_data: dict) -> User:
        """Save or update user data"""
        try:
            user = User.query.filter_by(username=user_data['username']).first()
            
            if user:
                # Update existing user
                for key, value in user_data.items():
                    if hasattr(user, key):
                        setattr(user, key, value)
                user.updated_at = datetime.utcnow()
                if hasattr(user, 'last_scraped'):
                    user.last_scraped = datetime.utcnow()
            else:
                # Create new user
                user = User(**user_data)
                if hasattr(user, 'last_scraped'):
                    user.last_scraped = datetime.utcnow()
            
            db.session.add(user)
            db.session.commit()
            
            logger.info(f"Saved user: {user.username}")
            return user
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error saving user: {e}")
            raise
    
    def save_tweets(self, user_id: int, tweets_data: List[Dict]) -> List[Tweet]:
        """Save tweets to database with simplified structure"""
        try:
            tweet_objects = []
            
            for tweet_data in tweets_data:
                existing_tweet = Tweet.query.filter_by(
                    user_id=user_id,
                    tweet_id=tweet_data['tweet_id']
                ).first()
                
                if existing_tweet:
                    # Update existing tweet
                    existing_tweet.text = tweet_data.get('text', '')
                    existing_tweet.language = tweet_data.get('language', 'en')
                    existing_tweet.media_urls = json.dumps(tweet_data.get('media_urls', []))
                    existing_tweet.local_media_paths = json.dumps(tweet_data.get('local_media_paths', []))
                    existing_tweet.urls = tweet_data.get('urls', [])
                    existing_tweet.hashtags = tweet_data.get('hashtags', [])
                    existing_tweet.posted_at = tweet_data.get('posted_at', datetime.utcnow())
                    
                    tweet_objects.append(existing_tweet)
                else:
                    # Create new tweet
                    tweet = Tweet(
                        user_id=user_id,
                        tweet_id=tweet_data['tweet_id'],
                        text=tweet_data.get('text', ''),
                        language=tweet_data.get('language', 'en'),
                        media_urls=json.dumps(tweet_data.get('media_urls', [])),
                        local_media_paths=json.dumps(tweet_data.get('local_media_paths', [])),
                        urls=tweet_data.get('urls', []),
                        hashtags=tweet_data.get('hashtags', []),
                        posted_at=tweet_data.get('posted_at', datetime.utcnow())
                    )
                    
                    db.session.add(tweet)
                    tweet_objects.append(tweet)
            
            db.session.commit()
            logger.info(f"Saved {len(tweet_objects)} tweets for user_id: {user_id}")
            return tweet_objects
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error saving tweets: {e}")
            raise
    
    def save_posts(self, user_id: int, posts_data: List[dict]) -> List[Post]:
        """Save posts for a user"""
        try:
            post_objs = []
            
            for post_data in posts_data:
                # Check if post already exists
                existing_post = Post.query.filter_by(post_id=post_data['post_id']).first()
                
                if existing_post:
                    # Update existing post
                    for key, value in post_data.items():
                        if hasattr(existing_post, key):
                            setattr(existing_post, key, value)
                    if hasattr(existing_post, 'updated_at'):
                        existing_post.updated_at = datetime.utcnow()
                    post_objs.append(existing_post)
                else:
                    # Create new post
                    post_data['user_id'] = user_id
                    post = Post(**post_data)
                    post_objs.append(post)
                    db.session.add(post)
            
            db.session.commit()
            
            logger.info(f"Saved {len(post_objs)} posts for user_id: {user_id}")
            return post_objs
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error saving posts: {e}")
            raise
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return User.query.filter_by(username=username).first()
    
    def get_user_tweets(self, user_id: int, limit: int = 50) -> List[Tweet]:
        """Get user tweets"""
        return Tweet.query.filter_by(user_id=user_id).order_by(Tweet.posted_at.desc()).limit(limit).all()
    
    def get_user_posts(self, user_id: int, limit: int = 20) -> List[Post]:
        """Get user posts"""
        return Post.query.filter_by(user_id=user_id).order_by(Post.posted_at.desc()).limit(limit).all()
    
    def get_user_tweets_paginated(self, user_id: int, page: int, per_page: int) -> Tuple[List[Tweet], int]:
        """Get user tweets with pagination"""
        query = Tweet.query.filter_by(user_id=user_id).order_by(Tweet.posted_at.desc())
        total = query.count()
        tweets = query.offset((page - 1) * per_page).limit(per_page).all()
        return tweets, total
    
    def get_user_posts_paginated(self, user_id: int, page: int, per_page: int) -> Tuple[List[Post], int]:
        """Get user posts with pagination"""
        query = Post.query.filter_by(user_id=user_id).order_by(Post.posted_at.desc())
        total = query.count()
        posts = query.offset((page - 1) * per_page).limit(per_page).all()
        return posts, total
    
    def is_recently_scraped(self, user: User, hours: int = 1) -> bool:
        """Check if user was scraped recently"""
        if not hasattr(user, 'last_scraped') or not user.last_scraped:
            return False
        
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        return user.last_scraped > time_threshold