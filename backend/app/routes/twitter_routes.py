
from flask import Blueprint, request, jsonify
from app.services.x_data_fetcher import XDataFetcher
from app.services.x_scraper import XScraper
from app.utils.models import load_models, analyze_text, analyze_image
from app.utils.bias_detection import detect_bias, calculate_fairness_metrics
from app.utils.social_impact import calculate_social_impact, get_protected_groups
from app.utils.community_outreach import get_community_metrics
import logging

twitter_routes = Blueprint('twitter_routes', __name__)

# Initialize models and services
models = load_models()
x_fetcher = XDataFetcher()
x_scraper = XScraper()

@twitter_routes.route('/analyze', methods=['POST'])
def analyze_user():
    """Analyze user profile with social justice considerations"""
    try:
        data = request.get_json()
        username = data.get('username')
        image_model = data.get('image_model', ['vgg16'])
        text_model = data.get('text_model', ['xlnet'])
        fusion_technique = data.get('fusion_technique', 'weighted_average')
        alpha = data.get('alpha', 0.5)

        if not username:
            return jsonify({'error': 'Username is required'}), 400

        # Fetch user data
        user_data = x_fetcher.fetch_user_data(username)
        if not user_data:
            return jsonify({'error': 'User not found or data unavailable'}), 404

        # Scrape tweets and media
        tweets = x_scraper.scrape_user_tweets(username)
        
        # Analyze text content
        text_analysis = analyze_text(tweets, text_model, models)
        
        # Analyze images if available
        image_analysis = None
        if user_data.get('profile_image_url'):
            image_analysis = analyze_image(user_data['profile_image_url'], image_model, models)
        
        # Perform bias detection
        bias_results = detect_bias(text_analysis, user_data)
        
        # Calculate social impact
        social_impact = calculate_social_impact(text_analysis, user_data)
        
        # Get community metrics
        community_metrics = get_community_metrics()
        
        # Combine results
        analysis_result = {
            'username': username,
            'text_analysis': text_analysis,
            'image_analysis': image_analysis,
            'fusion_technique': fusion_technique,
            'alpha': alpha,
            'bias_detection': bias_results,
            'social_impact': social_impact,
            'community_metrics': community_metrics,
            'success': True
        }

        return jsonify(analysis_result)

    except Exception as e:
        logging.error(f"Error in analyze_user: {str(e)}")
        return jsonify({'error': 'Analysis failed', 'details': str(e)}), 500

@twitter_routes.route('/bias-detection', methods=['GET'])
def get_bias_detection():
    """Get bias detection metrics"""
    try:
        # This would typically get data from a database or cache
        bias_metrics = {
            'gender_bias': {
                'score': 0.15,
                'status': 'low',
                'description': 'Minimal gender bias detected in analysis'
            },
            'racial_bias': {
                'score': 0.08,
                'status': 'very-low',
                'description': 'Very low racial bias detected'
            },
            'age_bias': {
                'score': 0.22,
                'status': 'moderate',
                'description': 'Moderate age bias detected - requires attention'
            },
            'socioeconomic_bias': {
                'score': 0.12,
                'status': 'low',
                'description': 'Low socioeconomic bias detected'
            }
        }

        fairness_metrics = {
            'equalized_odds': 0.89,
            'demographic_parity': 0.92,
            'predictive_rate_parity': 0.88,
            'overall_fairness': 0.90
        }

        return jsonify({
            'bias_metrics': bias_metrics,
            'fairness_metrics': fairness_metrics,
            'success': True
        })

    except Exception as e:
        logging.error(f"Error in get_bias_detection: {str(e)}")
        return jsonify({'error': 'Failed to get bias detection data'}), 500

@twitter_routes.route('/social-impact', methods=['GET'])
def get_social_impact():
    """Get social justice impact metrics"""
    try:
        impact_metrics = {
            'marginalized_groups': {
                'total_analyzed': 1250,
                'protected_users': 342,
                'bias_detected': 23,
                'interventions_applied': 15
            },
            'social_justice_score': {
                'overall': 0.87,
                'representation': 0.82,
                'fairness': 0.91,
                'inclusivity': 0.85
            },
            'community_impact': {
                'positive_interventions': 89,
                'bias_reduction': 0.23,
                'protected_groups_supported': 4,
                'social_justice_initiatives': 12
            }
        }

        marginalized_groups = [
            {'name': 'Women', 'count': 156, 'bias_score': 0.12, 'status': 'protected'},
            {'name': 'People of Color', 'count': 203, 'bias_score': 0.08, 'status': 'protected'},
            {'name': 'LGBTQ+', 'count': 89, 'bias_score': 0.15, 'status': 'protected'},
            {'name': 'People with Disabilities', 'count': 67, 'bias_score': 0.18, 'status': 'protected'},
            {'name': 'Religious Minorities', 'count': 134, 'bias_score': 0.11, 'status': 'protected'},
            {'name': 'Economic Disadvantaged', 'count': 245, 'bias_score': 0.22, 'status': 'protected'}
        ]

        return jsonify({
            'impact_metrics': impact_metrics,
            'marginalized_groups': marginalized_groups,
            'success': True
        })

    except Exception as e:
        logging.error(f"Error in get_social_impact: {str(e)}")
        return jsonify({'error': 'Failed to get social impact data'}), 500

@twitter_routes.route('/community-outreach', methods=['GET'])
def get_community_outreach():
    """Get community outreach metrics"""
    try:
        educational_programs = [
            {
                'name': 'AI Ethics Workshop',
                'description': 'Interactive workshops on responsible AI development',
                'participants': 156,
                'impact': '85% reported improved understanding',
                'status': 'ongoing',
                'category': 'education'
            },
            {
                'name': 'Bias Detection Training',
                'description': 'Training sessions on identifying and mitigating AI bias',
                'participants': 89,
                'impact': '92% can now detect bias patterns',
                'status': 'completed',
                'category': 'training'
            },
            {
                'name': 'Community AI Lab',
                'description': 'Hands-on experience with ethical AI tools',
                'participants': 234,
                'impact': '67% implemented ethical practices',
                'status': 'ongoing',
                'category': 'hands-on'
            },
            {
                'name': 'Youth AI Mentorship',
                'description': 'Mentoring program for underrepresented youth in AI',
                'participants': 45,
                'impact': '78% pursued AI-related education',
                'status': 'ongoing',
                'category': 'mentorship'
            }
        ]

        community_initiatives = [
            {
                'name': 'Digital Literacy Program',
                'target': 'Underserved Communities',
                'participants': 342,
                'success': 0.89,
                'description': 'Teaching digital skills and AI awareness'
            },
            {
                'name': 'Bias Reporting System',
                'target': 'General Public',
                'participants': 1250,
                'success': 0.92,
                'description': 'Anonymous reporting of AI bias incidents'
            },
            {
                'name': 'Ethical AI Certification',
                'target': 'AI Developers',
                'participants': 67,
                'success': 0.95,
                'description': 'Certification program for ethical AI practices'
            },
            {
                'name': 'Community Feedback Loop',
                'target': 'Marginalized Groups',
                'participants': 189,
                'success': 0.87,
                'description': 'Regular feedback collection from affected communities'
            }
        ]

        impact_metrics = {
            'total_participants': 1892,
            'programs_completed': 8,
            'communities_reached': 12,
            'knowledge_improvement': 0.84,
            'bias_awareness': 0.91,
            'ethical_practices': 0.78
        }

        return jsonify({
            'educational_programs': educational_programs,
            'community_initiatives': community_initiatives,
            'impact_metrics': impact_metrics,
            'success': True
        })

    except Exception as e:
        logging.error(f"Error in get_community_outreach: {str(e)}")
        return jsonify({'error': 'Failed to get community outreach data'}), 500

@twitter_routes.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'PostPatrol API is running'})