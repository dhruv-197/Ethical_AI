import sqlite3
import os
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AnalysisCache:
    """Cache for analysis results to prevent redundant scraping and analysis"""
    
    def __init__(self):
        self.db_path = os.path.join('instance', 'x_sentiment.db')
    
    def _get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def get_cached_analysis(self, username, analysis_type):
        """Get cached analysis for a user and analysis type"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT user_profile, tweets_data, analysis_results, is_dynamic, updated_at
                FROM analysis_cache 
                WHERE username = ? AND analysis_type = ?
            ''', (username, analysis_type))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                user_profile, tweets_data, analysis_results, is_dynamic, updated_at = row
                return {
                    'user_profile': json.loads(user_profile) if user_profile else None,
                    'tweets_data': json.loads(tweets_data) if tweets_data else None,
                    'analysis_results': json.loads(analysis_results) if analysis_results else None,
                    'is_dynamic': bool(is_dynamic),
                    'updated_at': datetime.fromisoformat(updated_at) if updated_at else datetime.utcnow()
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting cached analysis: {e}")
            return None
    
    def cache_analysis(self, username, analysis_type, user_profile, tweets_data, analysis_results, is_dynamic=False):
        """Cache analysis results"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Check if entry exists
            cursor.execute('''
                SELECT id FROM analysis_cache 
                WHERE username = ? AND analysis_type = ?
            ''', (username, analysis_type))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing entry
                cursor.execute('''
                    UPDATE analysis_cache 
                    SET user_profile = ?, tweets_data = ?, analysis_results = ?, 
                        is_dynamic = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE username = ? AND analysis_type = ?
                ''', (
                    json.dumps(user_profile) if user_profile else None,
                    json.dumps(tweets_data) if tweets_data else None,
                    json.dumps(analysis_results) if analysis_results else None,
                    is_dynamic,
                    username, analysis_type
                ))
            else:
                # Create new entry
                cursor.execute('''
                    INSERT INTO analysis_cache 
                    (username, analysis_type, user_profile, tweets_data, analysis_results, is_dynamic)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    username, analysis_type,
                    json.dumps(user_profile) if user_profile else None,
                    json.dumps(tweets_data) if tweets_data else None,
                    json.dumps(analysis_results) if analysis_results else None,
                    is_dynamic
                ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Cached analysis for {username}:{analysis_type}")
            return True
            
        except Exception as e:
            logger.error(f"Error caching analysis: {e}")
            return False
    
    def clear_cache_for_user(self, username):
        """Clear all cache entries for a user"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM analysis_cache WHERE username = ?', (username,))
            deleted_count = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            logger.info(f"Cleared {deleted_count} cache entries for {username}")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return 0
    
    def is_cache_fresh(self, cache_entry, max_age_hours=24):
        """Check if cache is fresh (less than max_age_hours old)"""
        if not cache_entry:
            return False
        
        try:
            age = datetime.utcnow() - cache_entry['updated_at']
            return age.total_seconds() < (max_age_hours * 3600)
        except Exception as e:
            logger.error(f"Error checking cache freshness: {e}")
            return False 