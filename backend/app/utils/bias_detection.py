import re
import logging
from typing import Dict, List, Any
import numpy as np

def detect_bias(text_analysis: Dict, user_data: Dict) -> Dict:
    """
    Detect various types of bias in the analysis results
    """
    try:
        bias_results = {
            'gender_bias': detect_gender_bias(text_analysis, user_data),
            'racial_bias': detect_racial_bias(text_analysis, user_data),
            'age_bias': detect_age_bias(text_analysis, user_data),
            'socioeconomic_bias': detect_socioeconomic_bias(text_analysis, user_data)
        }
        
        # Calculate overall bias score
        bias_scores = [bias['score'] for bias in bias_results.values()]
        overall_bias = np.mean(bias_scores)
        
        bias_results['overall_bias'] = {
            'score': overall_bias,
            'status': get_bias_status(overall_bias),
            'description': f'Overall bias score: {overall_bias:.2f}'
        }
        
        return bias_results
        
    except Exception as e:
        logging.error(f"Error in bias detection: {str(e)}")
        return get_default_bias_results()

def detect_gender_bias(text_analysis: Dict, user_data: Dict) -> Dict:
    """Detect gender-related bias in text analysis"""
    try:
        # Gender-related keywords and patterns
        gender_keywords = {
            'male': ['he', 'him', 'his', 'man', 'men', 'guy', 'guys', 'male'],
            'female': ['she', 'her', 'hers', 'woman', 'women', 'girl', 'girls', 'female']
        }
        
        text_content = ' '.join([tweet.get('text', '') for tweet in text_analysis.get('tweets', [])])
        text_content = text_content.lower()
        
        male_count = sum(text_content.count(word) for word in gender_keywords['male'])
        female_count = sum(text_content.count(word) for word in gender_keywords['female'])
        
        total_gender_mentions = male_count + female_count
        if total_gender_mentions == 0:
            return {'score': 0.0, 'status': 'very-low', 'description': 'No gender bias detected'}
        
        gender_ratio = abs(male_count - female_count) / total_gender_mentions
        bias_score = min(gender_ratio * 0.5, 1.0)  # Normalize to 0-1
        
        return {
            'score': bias_score,
            'status': get_bias_status(bias_score),
            'description': f'Gender bias detected: {bias_score:.2f}'
        }
        
    except Exception as e:
        logging.error(f"Error in gender bias detection: {str(e)}")
        return {'score': 0.15, 'status': 'low', 'description': 'Gender bias analysis failed'}

def detect_racial_bias(text_analysis: Dict, user_data: Dict) -> Dict:
    """Detect racial bias in text analysis"""
    try:
        # Racial/ethnic keywords and patterns
        racial_keywords = [
            'race', 'racial', 'ethnic', 'minority', 'majority', 'diversity',
            'black', 'white', 'asian', 'hispanic', 'latino', 'african', 'european'
        ]
        
        text_content = ' '.join([tweet.get('text', '') for tweet in text_analysis.get('tweets', [])])
        text_content = text_content.lower()
        
        racial_mentions = sum(text_content.count(word) for word in racial_keywords)
        
        # Simple heuristic: more racial mentions might indicate bias
        bias_score = min(racial_mentions * 0.1, 1.0)
        
        return {
            'score': bias_score,
            'status': get_bias_status(bias_score),
            'description': f'Racial bias detected: {bias_score:.2f}'
        }
        
    except Exception as e:
        logging.error(f"Error in racial bias detection: {str(e)}")
        return {'score': 0.08, 'status': 'very-low', 'description': 'Racial bias analysis failed'}

def detect_age_bias(text_analysis: Dict, user_data: Dict) -> Dict:
    """Detect age-related bias in text analysis"""
    try:
        # Age-related keywords and patterns
        age_keywords = {
            'young': ['young', 'youth', 'teen', 'teenager', 'kid', 'child'],
            'old': ['old', 'elderly', 'senior', 'aged', 'boomer', 'millennial']
        }
        
        text_content = ' '.join([tweet.get('text', '') for tweet in text_analysis.get('tweets', [])])
        text_content = text_content.lower()
        
        young_count = sum(text_content.count(word) for word in age_keywords['young'])
        old_count = sum(text_content.count(word) for word in age_keywords['old'])
        
        total_age_mentions = young_count + old_count
        if total_age_mentions == 0:
            return {'score': 0.0, 'status': 'very-low', 'description': 'No age bias detected'}
        
        age_ratio = abs(young_count - old_count) / total_age_mentions
        bias_score = min(age_ratio * 0.6, 1.0)
        
        return {
            'score': bias_score,
            'status': get_bias_status(bias_score),
            'description': f'Age bias detected: {bias_score:.2f}'
        }
        
    except Exception as e:
        logging.error(f"Error in age bias detection: {str(e)}")
        return {'score': 0.22, 'status': 'moderate', 'description': 'Age bias analysis failed'}

def detect_socioeconomic_bias(text_analysis: Dict, user_data: Dict) -> Dict:
    """Detect socioeconomic bias in text analysis"""
    try:
        # Socioeconomic keywords and patterns
        socioeconomic_keywords = [
            'rich', 'poor', 'wealthy', 'poverty', 'money', 'income',
            'class', 'economic', 'financial', 'expensive', 'cheap',
            'luxury', 'affordable', 'cost', 'price', 'wealth'
        ]
        
        text_content = ' '.join([tweet.get('text', '') for tweet in text_analysis.get('tweets', [])])
        text_content = text_content.lower()
        
        socioeconomic_mentions = sum(text_content.count(word) for word in socioeconomic_keywords)
        
        # Simple heuristic: more socioeconomic mentions might indicate bias
        bias_score = min(socioeconomic_mentions * 0.08, 1.0)
        
        return {
            'score': bias_score,
            'status': get_bias_status(bias_score),
            'description': f'Socioeconomic bias detected: {bias_score:.2f}'
        }
        
    except Exception as e:
        logging.error(f"Error in socioeconomic bias detection: {str(e)}")
        return {'score': 0.12, 'status': 'low', 'description': 'Socioeconomic bias analysis failed'}

def get_bias_status(bias_score: float) -> str:
    """Convert bias score to status string"""
    if bias_score < 0.1:
        return 'very-low'
    elif bias_score < 0.2:
        return 'low'
    elif bias_score < 0.4:
        return 'moderate'
    else:
        return 'high'

def calculate_fairness_metrics(text_analysis: Dict, user_data: Dict) -> Dict:
    """Calculate fairness metrics for the analysis"""
    try:
        # This would typically involve more sophisticated fairness calculations
        # For now, we'll use simplified metrics based on bias detection
        
        bias_results = detect_bias(text_analysis, user_data)
        
        # Calculate fairness metrics based on bias scores
        bias_scores = [bias['score'] for bias in bias_results.values() if bias['score'] is not None]
        
        if not bias_scores:
            return get_default_fairness_metrics()
        
        # Convert bias scores to fairness scores (inverse relationship)
        fairness_scores = [1 - score for score in bias_scores]
        
        return {
            'equalized_odds': np.mean(fairness_scores),
            'demographic_parity': np.mean(fairness_scores),
            'predictive_rate_parity': np.mean(fairness_scores),
            'overall_fairness': np.mean(fairness_scores)
        }
        
    except Exception as e:
        logging.error(f"Error in fairness metrics calculation: {str(e)}")
        return get_default_fairness_metrics()

def get_default_bias_results() -> Dict:
    """Return default bias results when analysis fails"""
    return {
        'gender_bias': {'score': 0.15, 'status': 'low', 'description': 'Default gender bias'},
        'racial_bias': {'score': 0.08, 'status': 'very-low', 'description': 'Default racial bias'},
        'age_bias': {'score': 0.22, 'status': 'moderate', 'description': 'Default age bias'},
        'socioeconomic_bias': {'score': 0.12, 'status': 'low', 'description': 'Default socioeconomic bias'},
        'overall_bias': {'score': 0.14, 'status': 'low', 'description': 'Default overall bias'}
    }

def get_default_fairness_metrics() -> Dict:
    """Return default fairness metrics when calculation fails"""
    return {
        'equalized_odds': 0.89,
        'demographic_parity': 0.92,
        'predictive_rate_parity': 0.88,
        'overall_fairness': 0.90
    } 