import tweepy
import os
from datetime import datetime
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class XAPIClient:
    def __init__(self):
        """Initialize Twitter API client"""
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret = os.getenv('TWITTER_API_SECRET')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        
        if not all([self.api_key, self.api_secret, self.bearer_token]):
            raise ValueError("Twitter API credentials not found")
        
        # Initialize API client
        self.client = tweepy.Client(
            bearer_token=self.bearer_token,
            consumer_key=self.api_key,
            consumer_secret=self.api_secret,
            access_token=self.access_token,
            access_token_secret=self.access_token_secret,
            wait_on_rate_limit=True
        )
    
    def get_user_profile(self, username: str) -> Optional[Dict]:
        """Get user profile using API"""
        try:
            user = self.client.get_user(
                username=username,
                user_fields=['created_at', 'description', 'location', 'profile_image_url', 'public_metrics', 'url', 'verified']
            )
            
            if not user.data:
                return None
            
            user_data = user.data
            metrics = user_data.public_metrics
            
            return {
                'username': user_data.username,
                'name': user_data.name,
                'bio': user_data.description,
                'location': user_data.location,
                'website': user_data.url,
                'joined_date': user_data.created_at,
                'followers_count': metrics['followers_count'],
                'following_count': metrics['following_count'],
                'tweets_count': metrics['tweet_count'],
                'verified': user_data.verified,
                'profile_image_url': user_data.profile_image_url,
                'user_id': user_data.id
            }
            
        except tweepy.NotFound:
            logger.error(f"User {username} not found")
            return None
        except tweepy.TooManyRequests:
            logger.error("Rate limit exceeded")
            raise
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            return None
    
    def get_user_tweets(self, username: str, max_tweets: int = 50) -> List[Dict]:
        """Get user tweets using API"""
        try:
            # First get user ID
            user = self.client.get_user(username=username)
            if not user.data:
                return []
            
            user_id = user.data.id
            
            # Get tweets
            tweets = tweepy.Paginator(
                self.client.get_users_tweets,
                id=user_id,
                tweet_fields=['created_at', 'public_metrics', 'context_annotations', 'entities'],
                max_results=100,
                limit=max_tweets
            ).flatten(limit=max_tweets)
            
            tweet_data = []
            for tweet in tweets:
                metrics = tweet.public_metrics
                
                # Extract media URLs
                media_urls = []
                if tweet.entities and 'urls' in tweet.entities:
                    media_urls = [url['expanded_url'] for url in tweet.entities['urls'] if 'media' in url.get('expanded_url', '')]
                
                tweet_data.append({
                    'tweet_id': tweet.id,
                    'text': tweet.text,
                    'created_at': tweet.created_at,
                    'retweet_count': metrics['retweet_count'],
                    'like_count': metrics['like_count'],
                    'reply_count': metrics['reply_count'],
                    'quote_count': metrics['quote_count'],
                    'media_urls': media_urls,
                    'hashtags': self._extract_hashtags(tweet.text),
                    'mentions': self._extract_mentions(tweet.text),
                })
            
            return tweet_data
            
        except tweepy.NotFound:
            logger.error(f"User {username} not found")
            return []
        except tweepy.TooManyRequests:
            logger.error("Rate limit exceeded")
            raise
        except Exception as e:
            logger.error(f"Error getting tweets: {e}")
            return []
    
    def _extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text"""
        import re
        return re.findall(r'#\w+', text)
    
    def _extract_mentions(self, text: str) -> List[str]:
        """Extract mentions from text"""
        import re
        return re.findall(r'@\w+', text)