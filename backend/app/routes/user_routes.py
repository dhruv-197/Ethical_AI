from flask import Blueprint, request, jsonify
from app.services.x_data_fetcher import XDataFetcher  # Updated import
from app.services.database import DatabaseService
from app.utils.validators import validate_username
from app.models.user import User
from app.utils.decorators import handle_errors
from app.config import Config
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)
from app.utils.multi_models import multimodal_predict
from app import db
import shutil
from  dotenv import  load_dotenv
from requests_oauthlib import OAuth1
load_dotenv()  # Load environment variables from .env file
user_bp = Blueprint('user', __name__)
db_service = DatabaseService()
TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_SECRET_KEY = os.getenv('TWITTER_API_SECRET_KEY')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')
@user_bp.route('/user/get-info', methods=['POST'])
@handle_errors
def get_user_info():
    """
    Get user information, tweets, and posts
    """
    data = request.get_json()
    # breakpoint()
    username = data.get('username')
    max_tweets = data.get('max_tweets',50)

    if not username:
        return jsonify({'error': 'Username is required'}), 400
    
    if not validate_username(username):
        return jsonify({'error': 'Invalid username format'}), 400
    
    # Remove @ if present
    username = username.replace('@', '').strip()
    
    try:
        # Check if user exists in database and was scraped recently
        user_data = db_service.get_user_by_username(username)
        
        if user_data and db_service.is_recently_scraped(user_data, hours=1):
            # Return cached data
            tweets = db_service.get_user_tweets(user_data.id, limit=50)
            # posts = db_service.get_user_posts(user_data.id, limit=20)
            
            return jsonify({
                'success': True,
                'user': user_data.to_dict(),
                'tweets': [tweet.to_dict() for tweet in tweets],
                # 'posts': [post.to_dict() for post in posts],
                'source': 'cache'
            })
        
        # Fetch fresh data using hybrid approach
        data_fetcher = XDataFetcher()

        try:
            # Get profile info
            profile_data = data_fetcher.get_user_profile(username)
            if not profile_data:
                return jsonify({'error': 'User not found or profile is private'}), 404
            
            # Get tweets
            tweets_data = data_fetcher.get_user_tweets(username, max_tweets=max_tweets)
            
            # # Get posts
            # posts_data = data_fetcher.get_user_posts(username, max_posts=Config.MAX_POSTS_PER_REQUEST)
            
        finally:
            # Clean up resources
            data_fetcher.close()
        
        # Save to database
        user_obj = db_service.save_user(profile_data)
        tweet_objs = db_service.save_tweets(user_obj.id, tweets_data)
        
        logger.info(f"Successfully fetched and saved data for {username}")
        
        return jsonify({
            'success': True,
            'user': user_obj.to_dict(),
            'tweets': [tweet.to_dict() for tweet in tweet_objs],
            'source': 'fresh'
        })
        
    except Exception as e:
        logger.error(f"Error getting user info for {username}: {e}")
        return jsonify({'error': 'Failed to fetch user information'}), 500

@user_bp.route('/user/<username>/refresh', methods=['POST'])
@handle_errors
def refresh_user_data(username):
    """
    Force refresh user data
    """
    if not validate_username(username):
        return jsonify({'error': 'Invalid username format'}), 400
    
    username = username.replace('@', '').strip()
    user = db_service.get_user_by_username(username)
    user_folder_path = os.path.join('downloaded_images', username)  # adjust path if needed
    if os.path.exists(user_folder_path):
        shutil.rmtree(user_folder_path)
        logger.info(f"Deleted folder at {user_folder_path}")
    else:
        logger.warning(f"No folder found at {user_folder_path}")
    
    try:
        # Use hybrid data fetcher
        data_fetcher = XDataFetcher()
        
        try:
            # Get fresh profile info
            profile_data = data_fetcher.get_user_profile(username)
            if not profile_data:
                return jsonify({'error': 'User not found or profile is private'}), 404
            
            # Get fresh tweets
            tweets_data = data_fetcher.get_user_tweets(username, max_tweets=Config.MAX_TWEETS_PER_REQUEST)
            
            
        finally:
            # Clean up resources
            data_fetcher.close()
        
        if tweets_data:
            tweets = db_service.get_user_tweets(user.id, limit=10000)  # Get all tweets for count
            posts = db_service.get_user_posts(user.id, limit=10000)   # Get all posts for count
            
            tweets_count = len(tweets)
            posts_count = len(posts)
            
            # Delete user (cascade will handle tweets and posts)
            db.session.delete(user)
            db.session.commit()
           
        
        # Update database
        user_obj = db_service.save_user(profile_data)
        tweet_objs = db_service.save_tweets(user_obj.id, tweets_data)
        
        logger.info(f"Successfully refreshed data for {username}")
        
        return jsonify({
            'success': True,
            'user': user_obj.to_dict(),
            'tweets': [tweet.to_dict() for tweet in tweet_objs],
            'message': 'Data refreshed successfully'
        })
        
    except Exception as e:
        logger.error(f"Error refreshing data for {username}: {e}")
        return jsonify({'error': 'Failed to refresh user data'}), 500

# Keep the existing pagination routes as they are
@user_bp.route('/user/<username>/tweets', methods=['GET'])
@handle_errors
def get_user_tweets(username):
    """
    Get user tweets with pagination
    """
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), Config.MAX_PAGE_SIZE)
    
    if not validate_username(username):
        return jsonify({'error': 'Invalid username format'}), 400
    
    try:
        user_data = db_service.get_user_by_username(username)
        if not user_data:
            return jsonify({'error': 'User not found'}), 404
        
        tweets, total = db_service.get_user_tweets_paginated(user_data.id, page, per_page)
        
        return jsonify({
            'success': True,
            'tweets': [tweet.to_dict() for tweet in tweets],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting tweets for {username}: {e}")
        return jsonify({'error': 'Failed to fetch tweets'}), 500

@user_bp.route('/profiles', methods=['GET'])
@handle_errors
def get_all_profiles():
    """Get all user profiles with pagination and filtering - USER INFO ONLY"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '', type=str)
        sort_by = request.args.get('sort_by', 'created_at', type=str)
        sort_order = request.args.get('sort_order', 'desc', type=str)

        per_page = min(per_page, 100)

        query = User.query

        if search:
            query = query.filter(
                db.or_(
                    User.username.ilike(f'%{search}%'),
                    User.name.ilike(f'%{search}%')
                )
            )

        if sort_by == 'followers_count':
            order_column = User.followers_count
        elif sort_by == 'following_count':
            order_column = User.following_count
        elif sort_by == 'tweets_count':
            order_column = User.tweets_count
        elif sort_by == 'last_scraped':
            order_column = User.last_scraped
        else:
            order_column = User.created_at

        if sort_order == 'desc':
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        users = pagination.items

        # Only return basic user information without tweets
        users_data = []
        for user in users:
            user_dict = user.to_dict(include_tweets=False)
            
            # Add basic tweet count from database
            tweets_count = db_service.get_user_tweets(user.id, limit=1000)  # Get count only
            user_dict['scraped_tweets_count'] = len(tweets_count)
            user_dict['scraped_media_count'] = len([t for t in tweets_count if t.media_urls])
            
            users_data.append(user_dict)

        response_data = {
            'success': True,
            'users': users_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_prev': pagination.has_prev,
                'has_next': pagination.has_next,
                'prev_num': pagination.prev_num,
                'next_num': pagination.next_num
            }
        }

        return jsonify(response_data), 200

    except Exception as e:
        logger.error(f"Error getting profiles: {e}")
        return jsonify({'error': 'Failed to fetch profiles'}), 500

@user_bp.route('/profile/<username>', methods=['GET'])
@handle_errors
def get_user_profile(username):
    """Get a specific user profile by username WITH TWEETS DATA"""
    try:
        user = db_service.get_user_by_username(username)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get all tweets for this user
        tweets = db_service.get_user_tweets(user.id, limit=1000)
        
        # Get recent tweets
        recent_tweets = db_service.get_user_tweets(user.id, limit=50)
        
        # Separate tweets with and without media
        tweets_with_media = [tweet for tweet in tweets if tweet.media_urls]
        tweets_without_media = [tweet for tweet in tweets if not tweet.media_urls]
        
        user_data = user.to_dict(include_tweets=False)
        user_data.update({
            'success': True,
            'tweets': [tweet.to_dict() for tweet in recent_tweets],  # All tweets for TweetList component
            'posts': [tweet.to_dict() for tweet in tweets_with_media[:20]],  # Posts with media
            'stats': {
                'tweets_in_db': len(tweets),
                'tweets_with_media': len(tweets_with_media),
                'tweets_without_media': len(tweets_without_media),
                'last_tweet_date': recent_tweets[0].posted_at.isoformat() if recent_tweets else None,
            }
        })
        
        return jsonify(user_data), 200
        
    except Exception as e:
        logger.error(f"Error getting profile for {username}: {e}")
        return jsonify({'error': 'Failed to fetch profile'}), 500

@user_bp.route('/profile/<username>', methods=['DELETE'])
@handle_errors
def delete_user_profile(username):
    """Delete a user profile and all associated data"""
    try:
        user = db_service.get_user_by_username(username)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        
        # Get counts before deletion for response
        tweets = db_service.get_user_tweets(user.id, limit=10000)  # Get all tweets for count
        posts = db_service.get_user_posts(user.id, limit=10000)   # Get all posts for count
        
        tweets_count = len(tweets)
        posts_count = len(posts)
        
        # Delete user (cascade will handle tweets and posts)
        db.session.delete(user)
        db.session.commit()
        user_folder_path = os.path.join('downloaded_images', username)  # adjust path if needed
        if os.path.exists(user_folder_path):
            shutil.rmtree(user_folder_path)
            logger.info(f"Deleted folder at {user_folder_path}")
        else:
            logger.warning(f"No folder found at {user_folder_path}")

        
        logger.info(f"Deleted user {username} with {tweets_count} tweets and {posts_count} posts")
        
        return jsonify({
            'success': True,
            'message': f'User {username} and all associated data deleted successfully',
            'deleted': {
                'username': username,
                'tweets_count': tweets_count,
                'posts_count': posts_count
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error deleting profile for {username}: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to delete profile'}), 500

@user_bp.route('/profiles/bulk-delete', methods=['DELETE'])
@handle_errors
def bulk_delete_profiles():
    """Delete multiple user profiles"""
    try:
        data = request.get_json()
        usernames = data.get('usernames', [])
        
        if not usernames:
            return jsonify({'error': 'No usernames provided'}), 400
        
        deleted_users = []
        not_found_users = []
        
        for username in usernames:
            user = db_service.get_user_by_username(username)
            
            if user:
                tweets = db_service.get_user_tweets(user.id, limit=10000)
                posts = db_service.get_user_posts(user.id, limit=10000)
                
                tweets_count = len(tweets)
                posts_count = len(posts)
                
                db.session.delete(user)
                deleted_users.append({
                    'username': username,
                    'tweets_count': tweets_count,
                    'posts_count': posts_count
                })
            else:
                not_found_users.append(username)
        
        db.session.commit()
        
        logger.info(f"Bulk deleted {len(deleted_users)} users")
        
        return jsonify({
            'success': True,
            'message': f'Successfully deleted {len(deleted_users)} users',
            'deleted': deleted_users,
            'not_found': not_found_users
        }), 200
        
    except Exception as e:
        logger.error(f"Error in bulk delete: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to bulk delete profiles'}), 500

@user_bp.route('/user/<username>/analyze', methods=['POST'])
@handle_errors
def analyze_user_profile(username):
    """
    Analyze user profile using multimodal classification
    """
    if not validate_username(username):
        return jsonify({'error': 'Invalid username format'}), 400
    
    username = username.replace('@', '').strip()
    data = request.get_json()
    image_model_names = data.get('image_model', ['clip'])
    text_model_names = data.get('text_model', ['xlnet'])
    fusion_technique = data.get('fusion_technique', 'weighted_average')
    alpha = data.get('alpha', 0.5)
    try:
        # Get user data from database
        user_data = db_service.get_user_by_username(username)
        if not user_data:
            return jsonify({'error': 'User not found. Please fetch user data first.'}), 404
        
        # Get user tweets for analysis
        tweets = db_service.get_user_tweets(user_data.id, limit=100)
        if not tweets:
            return jsonify({'error': 'No tweets found for analysis'}), 404
        
        # Extract tweet texts and LOCAL media paths
        tweet_texts = [tweet.text for tweet in tweets if tweet.text]
        local_media_paths = []
        for tweet in tweets:
            # Check if tweet has local_media_paths field
            if hasattr(tweet, 'local_media_paths') and tweet.local_media_paths:
                if isinstance(tweet.local_media_paths, list):
                    local_media_paths.extend(tweet.local_media_paths)
                else:
                    # If it's a string (JSON), parse it
                    try:
                        import json
                        paths = json.loads(tweet.local_media_paths)
                        if isinstance(paths, list):
                            local_media_paths.extend(paths)
                    except:
                        pass
            

        # Remove duplicates and filter existing files
        local_media_paths = list(set(local_media_paths))

        
        # Import and use multimodal classifier
        try:
            
            # Get analysis results
            analysis_results = multimodal_predict(
                texts=tweet_texts,
                images=local_media_paths,
                text_models=text_model_names,
                image_models=image_model_names,
                fusion_technique=fusion_technique,
                alpha=alpha,
                username=username

            )

            # Structure the response
            response_data = {
                'success': True,
                'username': username,
                'analysis': analysis_results,
                'analyzed_at': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Successfully analyzed profile for {username}")
            return jsonify(response_data)
            
        except ImportError as e:
            logger.error(f"Failed to import multimodal classifier: {e}")
            return jsonify({'error': 'Analysis service not available'}), 503
        
    except Exception as e:
        logger.error(f"Error analyzing profile for {username}: {e}")
        return jsonify({'error': 'Failed to analyze user profile'}), 500