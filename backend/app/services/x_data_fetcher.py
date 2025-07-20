# import tweepy
# import os
# from datetime import datetime
from typing import Dict, List, Optional
import logging
from app.services.x_scraper import XScraper

# import re


logger = logging.getLogger(__name__)

class XDataFetcher:
    def __init__(self):
        """Initialize with web scraping only"""
        self.scraper = XScraper()
        logger.info("Using web scraping only")
    
    def fetch_user_data(self, username: str) -> Optional[Dict]:
        """Fetch user data including profile and basic info"""
        try:
            profile = self.get_user_profile(username)
            if profile:
                return {
                    'username': username,
                    'display_name': profile.get('display_name', username),
                    'bio': profile.get('bio', ''),
                    'followers_count': profile.get('followers_count', 0),
                    'following_count': profile.get('following_count', 0),
                    'tweet_count': profile.get('tweet_count', 0),
                    'profile_image_url': profile.get('profile_image_url', ''),
                    'verified': profile.get('verified', False),
                    'created_at': profile.get('created_at', ''),
                    'location': profile.get('location', ''),
                    'url': profile.get('url', '')
                }
            return None
        except Exception as e:
            logger.error(f"Error fetching user data for {username}: {e}")
            return None
    
    def get_user_profile(self, username: str) -> Optional[Dict]:
        """Get user profile using web scraping"""
        return self.scraper.get_user_profile(username)
    
    def get_user_tweets(self, username: str, max_tweets: int = 50) -> List[Dict]:
        """Get user tweets using web scraping"""
        return self.scraper.get_user_tweets(username, max_tweets)
    
    def get_user_posts(self, username: str, max_posts: int = 20) -> List[Dict]:
        """Get user posts using web scraping"""
        return self.scraper.get_user_posts(username, max_posts)
    
    def close(self):
        """Close resources"""
        if self.scraper:
            self.scraper.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()