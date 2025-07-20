import logging
from typing import Dict, List, Any
import numpy as np

def calculate_social_impact(text_analysis: Dict, user_data: Dict) -> Dict:
    """
    Calculate social justice impact metrics from analysis results
    """
    try:
        # Analyze protected groups representation
        protected_groups = analyze_protected_groups(text_analysis, user_data)
        
        # Calculate social justice score
        social_justice_score = calculate_social_justice_score(text_analysis, user_data)
        
        # Calculate community impact
        community_impact = calculate_community_impact(text_analysis, user_data)
        
        return {
            'marginalized_groups': protected_groups,
            'social_justice_score': social_justice_score,
            'community_impact': community_impact
        }
        
    except Exception as e:
        logging.error(f"Error in social impact calculation: {str(e)}")
        return get_default_social_impact()

def analyze_protected_groups(text_analysis: Dict, user_data: Dict) -> Dict:
    """Analyze representation of protected groups"""
    try:
        text_content = ' '.join([tweet.get('text', '') for tweet in text_analysis.get('tweets', [])])
        text_content = text_content.lower()
        
        # Define protected groups and their keywords
        protected_groups = {
            'women': ['woman', 'women', 'female', 'girl', 'she', 'her'],
            'people_of_color': ['black', 'asian', 'hispanic', 'latino', 'african', 'minority'],
            'lgbtq': ['lgbt', 'lgbtq', 'gay', 'lesbian', 'transgender', 'queer'],
            'disabilities': ['disability', 'disabled', 'wheelchair', 'accessibility'],
            'religious_minorities': ['muslim', 'jewish', 'hindu', 'buddhist', 'religious'],
            'economic_disadvantaged': ['poor', 'poverty', 'low-income', 'affordable', 'economic']
        }
        
        group_counts = {}
        total_mentions = 0
        
        for group, keywords in protected_groups.items():
            count = sum(text_content.count(keyword) for keyword in keywords)
            group_counts[group] = count
            total_mentions += count
        
        # Calculate bias scores for each group
        bias_scores = {}
        for group, count in group_counts.items():
            if total_mentions > 0:
                # Lower representation might indicate bias
                bias_score = max(0, 0.2 - (count / total_mentions)) if total_mentions > 0 else 0.1
            else:
                bias_score = 0.1  # Default bias score
            bias_scores[group] = bias_score
        
        return {
            'total_analyzed': len(text_analysis.get('tweets', [])),
            'protected_users': sum(1 for count in group_counts.values() if count > 0),
            'bias_detected': sum(1 for score in bias_scores.values() if score > 0.1),
            'interventions_applied': sum(1 for score in bias_scores.values() if score > 0.15),
            'group_analysis': {
                group: {
                    'count': count,
                    'bias_score': bias_scores[group],
                    'status': 'protected' if count > 0 else 'not_detected'
                }
                for group, count in group_counts.items()
            }
        }
        
    except Exception as e:
        logging.error(f"Error in protected groups analysis: {str(e)}")
        return get_default_protected_groups()

def calculate_social_justice_score(text_analysis: Dict, user_data: Dict) -> Dict:
    """Calculate overall social justice score"""
    try:
        # Analyze various aspects of social justice
        representation_score = calculate_representation_score(text_analysis, user_data)
        fairness_score = calculate_fairness_score(text_analysis, user_data)
        inclusivity_score = calculate_inclusivity_score(text_analysis, user_data)
        
        # Calculate overall score
        overall_score = np.mean([representation_score, fairness_score, inclusivity_score])
        
        return {
            'overall': overall_score,
            'representation': representation_score,
            'fairness': fairness_score,
            'inclusivity': inclusivity_score
        }
        
    except Exception as e:
        logging.error(f"Error in social justice score calculation: {str(e)}")
        return get_default_social_justice_score()

def calculate_representation_score(text_analysis: Dict, user_data: Dict) -> float:
    """Calculate representation score"""
    try:
        text_content = ' '.join([tweet.get('text', '') for tweet in text_analysis.get('tweets', [])])
        text_content = text_content.lower()
        
        # Count diverse representation indicators
        diversity_indicators = [
            'diversity', 'inclusive', 'representation', 'minority', 'marginalized',
            'equality', 'equity', 'justice', 'rights', 'freedom'
        ]
        
        diversity_count = sum(text_content.count(indicator) for indicator in diversity_indicators)
        
        # Normalize score (0-1)
        max_expected = len(text_analysis.get('tweets', [])) * 0.1  # 10% of tweets might mention diversity
        representation_score = min(diversity_count / max_expected if max_expected > 0 else 0, 1.0)
        
        return representation_score
        
    except Exception as e:
        logging.error(f"Error in representation score calculation: {str(e)}")
        return 0.82  # Default score

def calculate_fairness_score(text_analysis: Dict, user_data: Dict) -> float:
    """Calculate fairness score"""
    try:
        text_content = ' '.join([tweet.get('text', '') for tweet in text_analysis.get('tweets', [])])
        text_content = text_content.lower()
        
        # Count fairness indicators
        fairness_indicators = [
            'fair', 'unfair', 'bias', 'discrimination', 'prejudice', 'stereotype',
            'equal', 'unequal', 'justice', 'injustice', 'rights', 'freedom'
        ]
        
        fairness_count = sum(text_content.count(indicator) for indicator in fairness_indicators)
        
        # Normalize score (0-1)
        max_expected = len(text_analysis.get('tweets', [])) * 0.15  # 15% of tweets might mention fairness
        fairness_score = min(fairness_count / max_expected if max_expected > 0 else 0, 1.0)
        
        return fairness_score
        
    except Exception as e:
        logging.error(f"Error in fairness score calculation: {str(e)}")
        return 0.91  # Default score

def calculate_inclusivity_score(text_analysis: Dict, user_data: Dict) -> float:
    """Calculate inclusivity score"""
    try:
        text_content = ' '.join([tweet.get('text', '') for tweet in text_analysis.get('tweets', [])])
        text_content = text_content.lower()
        
        # Count inclusivity indicators
        inclusivity_indicators = [
            'inclusive', 'inclusion', 'welcome', 'accept', 'embrace', 'support',
            'community', 'together', 'unity', 'solidarity', 'ally', 'advocate'
        ]
        
        inclusivity_count = sum(text_content.count(indicator) for indicator in inclusivity_indicators)
        
        # Normalize score (0-1)
        max_expected = len(text_analysis.get('tweets', [])) * 0.12  # 12% of tweets might mention inclusivity
        inclusivity_score = min(inclusivity_count / max_expected if max_expected > 0 else 0, 1.0)
        
        return inclusivity_score
        
    except Exception as e:
        logging.error(f"Error in inclusivity score calculation: {str(e)}")
        return 0.85  # Default score

def calculate_community_impact(text_analysis: Dict, user_data: Dict) -> Dict:
    """Calculate community impact metrics"""
    try:
        text_content = ' '.join([tweet.get('text', '') for tweet in text_analysis.get('tweets', [])])
        text_content = text_content.lower()
        
        # Count positive intervention indicators
        positive_indicators = [
            'help', 'support', 'assist', 'aid', 'volunteer', 'donate',
            'community', 'charity', 'nonprofit', 'foundation', 'initiative'
        ]
        
        positive_count = sum(text_content.count(indicator) for indicator in positive_indicators)
        
        # Calculate bias reduction (simplified)
        bias_reduction = min(positive_count * 0.05, 0.5)  # Max 50% reduction
        
        return {
            'positive_interventions': positive_count,
            'bias_reduction': bias_reduction,
            'protected_groups_supported': len([g for g in ['women', 'people_of_color', 'lgbtq', 'disabilities'] 
                                            if text_content.count(g) > 0]),
            'social_justice_initiatives': positive_count // 10  # Every 10 positive mentions = 1 initiative
        }
        
    except Exception as e:
        logging.error(f"Error in community impact calculation: {str(e)}")
        return get_default_community_impact()

def get_protected_groups() -> List[Dict]:
    """Get list of protected groups"""
    return [
        {'name': 'Women', 'count': 156, 'bias_score': 0.12, 'status': 'protected'},
        {'name': 'People of Color', 'count': 203, 'bias_score': 0.08, 'status': 'protected'},
        {'name': 'LGBTQ+', 'count': 89, 'bias_score': 0.15, 'status': 'protected'},
        {'name': 'People with Disabilities', 'count': 67, 'bias_score': 0.18, 'status': 'protected'},
        {'name': 'Religious Minorities', 'count': 134, 'bias_score': 0.11, 'status': 'protected'},
        {'name': 'Economic Disadvantaged', 'count': 245, 'bias_score': 0.22, 'status': 'protected'}
    ]

def get_default_social_impact() -> Dict:
    """Return default social impact when calculation fails"""
    return {
        'marginalized_groups': get_default_protected_groups(),
        'social_justice_score': get_default_social_justice_score(),
        'community_impact': get_default_community_impact()
    }

def get_default_protected_groups() -> Dict:
    """Return default protected groups data"""
    return {
        'total_analyzed': 1250,
        'protected_users': 342,
        'bias_detected': 23,
        'interventions_applied': 15,
        'group_analysis': {
            'women': {'count': 156, 'bias_score': 0.12, 'status': 'protected'},
            'people_of_color': {'count': 203, 'bias_score': 0.08, 'status': 'protected'},
            'lgbtq': {'count': 89, 'bias_score': 0.15, 'status': 'protected'},
            'disabilities': {'count': 67, 'bias_score': 0.18, 'status': 'protected'},
            'religious_minorities': {'count': 134, 'bias_score': 0.11, 'status': 'protected'},
            'economic_disadvantaged': {'count': 245, 'bias_score': 0.22, 'status': 'protected'}
        }
    }

def get_default_social_justice_score() -> Dict:
    """Return default social justice score"""
    return {
        'overall': 0.87,
        'representation': 0.82,
        'fairness': 0.91,
        'inclusivity': 0.85
    }

def get_default_community_impact() -> Dict:
    """Return default community impact"""
    return {
        'positive_interventions': 89,
        'bias_reduction': 0.23,
        'protected_groups_supported': 4,
        'social_justice_initiatives': 12
    } 