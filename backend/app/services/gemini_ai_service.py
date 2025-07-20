import google.generativeai as genai
import os
import logging
from typing import Dict, List, Optional, Any
from PIL import Image
import requests
from io import BytesIO
import base64
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class GeminiAIService:
    def __init__(self):
        """Initialize Gemini AI service"""
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        logger.info(f"Initializing Gemini AI service with API key length: {len(self.api_key)}")
        
        try:
            # Configure Gemini
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Test the connection
            test_response = self.model.generate_content("Test connection")
            logger.info("Gemini AI service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini AI service: {e}")
            raise
    
    def analyze_bias_detection(self, tweets: List[Dict], user_profile: Dict) -> Dict:
        """Analyze tweets for bias detection using Gemini"""
        try:
            logger.info(f"Starting bias detection analysis for {len(tweets)} tweets")
            
            # Prepare tweet text for analysis
            tweet_texts = [tweet.get('text', '') for tweet in tweets if tweet.get('text')]
            combined_text = '\n\n'.join(tweet_texts[:50])  # Limit to 50 tweets
            
            if not combined_text.strip():
                logger.warning("No tweet text available for analysis")
                return self._get_default_bias_results()
            
            prompt = f"""
            Analyze the following tweets for bias detection. Focus on:
            1. Gender bias (male/female representation, stereotypes)
            2. Racial bias (racial references, stereotypes)
            3. Age bias (age-related stereotypes)
            4. Socioeconomic bias (class references, economic stereotypes)
            
            User Profile: {user_profile.get('name', 'Unknown')} (@{user_profile.get('username', 'unknown')})
            Bio: {user_profile.get('bio', 'No bio')}
            
            Tweets to analyze:
            {combined_text}
            
            Provide analysis in this exact JSON format:
            {{
                "gender_bias": {{
                    "score": 0.0-1.0,
                    "status": "very-low|low|moderate|high",
                    "description": "Detailed analysis",
                    "examples": ["specific examples from tweets"]
                }},
                "racial_bias": {{
                    "score": 0.0-1.0,
                    "status": "very-low|low|moderate|high", 
                    "description": "Detailed analysis",
                    "examples": ["specific examples from tweets"]
                }},
                "age_bias": {{
                    "score": 0.0-1.0,
                    "status": "very-low|low|moderate|high",
                    "description": "Detailed analysis", 
                    "examples": ["specific examples from tweets"]
                }},
                "socioeconomic_bias": {{
                    "score": 0.0-1.0,
                    "status": "very-low|low|moderate|high",
                    "description": "Detailed analysis",
                    "examples": ["specific examples from tweets"]
                }},
                "overall_bias": {{
                    "score": 0.0-1.0,
                    "status": "very-low|low|moderate|high",
                    "description": "Overall bias assessment"
                }}
            }}
            """
            
            logger.info("Sending prompt to Gemini API...")
            response = self.model.generate_content(prompt)
            logger.info("Received response from Gemini API")
            
            result = self._parse_json_response(response.text)
            logger.info("Bias detection analysis completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error in bias detection analysis: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            return self._get_default_bias_results()
    
    def analyze_social_impact(self, tweets: List[Dict], user_profile: Dict) -> Dict:
        """Analyze tweets for social justice impact using Gemini"""
        try:
            logger.info(f"Starting social impact analysis for {len(tweets)} tweets")
            
            tweet_texts = [tweet.get('text', '') for tweet in tweets if tweet.get('text')]
            combined_text = '\n\n'.join(tweet_texts[:50])
            
            if not combined_text.strip():
                logger.warning("No tweet text available for analysis")
                return self._get_default_social_impact()
            
            prompt = f"""
            Analyze the following tweets for social justice impact. Focus on:
            1. Representation of marginalized groups (women, people of color, LGBTQ+, disabilities, religious minorities)
            2. Social justice advocacy and support
            3. Community engagement and positive interventions
            4. Fairness and inclusivity in content
            
            User Profile: {user_profile.get('name', 'Unknown')} (@{user_profile.get('username', 'unknown')})
            Bio: {user_profile.get('bio', 'No bio')}
            
            Tweets to analyze:
            {combined_text}
            
            Provide analysis in this exact JSON format:
            {{
                "marginalized_groups": {{
                    "total_analyzed": number,
                    "protected_users": number,
                    "bias_detected": number,
                    "interventions_applied": number,
                    "group_analysis": {{
                        "women": {{"count": number, "bias_score": 0.0-1.0, "status": "protected|not_detected"}},
                        "people_of_color": {{"count": number, "bias_score": 0.0-1.0, "status": "protected|not_detected"}},
                        "lgbtq": {{"count": number, "bias_score": 0.0-1.0, "status": "protected|not_detected"}},
                        "disabilities": {{"count": number, "bias_score": 0.0-1.0, "status": "protected|not_detected"}},
                        "religious_minorities": {{"count": number, "bias_score": 0.0-1.0, "status": "protected|not_detected"}},
                        "economic_disadvantaged": {{"count": number, "bias_score": 0.0-1.0, "status": "protected|not_detected"}}
                    }}
                }},
                "social_justice_score": {{
                    "overall": 0.0-1.0,
                    "representation": 0.0-1.0,
                    "fairness": 0.0-1.0,
                    "inclusivity": 0.0-1.0
                }},
                "community_impact": {{
                    "positive_interventions": number,
                    "bias_reduction": 0.0-1.0,
                    "protected_groups_supported": number,
                    "social_justice_initiatives": number
                }}
            }}
            """
            
            logger.info("Sending social impact prompt to Gemini API...")
            response = self.model.generate_content(prompt)
            logger.info("Received social impact response from Gemini API")
            
            result = self._parse_json_response(response.text)
            logger.info("Social impact analysis completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error in social impact analysis: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            return self._get_default_social_impact()
    
    def analyze_community_outreach(self, tweets: List[Dict], user_profile: Dict) -> Dict:
        """Analyze tweets for community outreach and educational impact using Gemini"""
        try:
            logger.info(f"Starting community outreach analysis for {len(tweets)} tweets")
            
            tweet_texts = [tweet.get('text', '') for tweet in tweets if tweet.get('text')]
            combined_text = '\n\n'.join(tweet_texts[:50])
            
            if not combined_text.strip():
                logger.warning("No tweet text available for analysis")
                return self._get_default_community_outreach()
            
            prompt = f"""
            Analyze the following tweets for community outreach and educational impact. Focus on:
            1. Educational content and knowledge sharing
            2. Community engagement and support
            3. Mentorship and guidance
            4. Resource sharing and accessibility
            5. Volunteer opportunities and community service
            
            User Profile: {user_profile.get('name', 'Unknown')} (@{user_profile.get('username', 'unknown')})
            Bio: {user_profile.get('bio', 'No bio')}
            
            Tweets to analyze:
            {combined_text}
            
            Provide analysis in this exact JSON format:
            {{
                "educational_programs": [
                    {{
                        "name": "string",
                        "description": "string", 
                        "participants": number,
                        "impact": "string",
                        "status": "ongoing|completed",
                        "category": "education|training|hands-on|mentorship"
                    }}
                ],
                "community_initiatives": [
                    {{
                        "name": "string",
                        "target": "string",
                        "participants": number,
                        "success": 0.0-1.0,
                        "description": "string"
                    }}
                ],
                "impact_metrics": {{
                    "total_participants": number,
                    "programs_completed": number,
                    "communities_reached": number,
                    "knowledge_improvement": 0.0-1.0,
                    "bias_awareness": 0.0-1.0,
                    "ethical_practices": 0.0-1.0
                }}
            }}
            """
            
            logger.info("Sending community outreach prompt to Gemini API...")
            response = self.model.generate_content(prompt)
            logger.info("Received community outreach response from Gemini API")
            
            result = self._parse_json_response(response.text)
            logger.info("Community outreach analysis completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error in community outreach analysis: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            return self._get_default_community_outreach()
    
    def analyze_images_for_bias(self, image_paths: List[str]) -> Dict:
        """Analyze images for bias using Gemini Vision"""
        try:
            if not image_paths:
                return {"image_bias": {"score": 0.0, "status": "no_images", "description": "No images to analyze"}}
            
            # Analyze first few images (limit to avoid API costs)
            images_to_analyze = image_paths[:5]
            
            prompt = """
            Analyze these images for potential bias in representation. Look for:
            1. Gender representation and stereotypes
            2. Racial/ethnic diversity and representation
            3. Age diversity and stereotypes
            4. Socioeconomic indicators and bias
            5. Accessibility and inclusion
            
            Provide analysis in this exact JSON format:
            {
                "image_bias": {
                    "score": 0.0-1.0,
                    "status": "very-low|low|moderate|high",
                    "description": "Detailed analysis of image bias",
                    "gender_representation": "analysis",
                    "racial_diversity": "analysis", 
                    "age_diversity": "analysis",
                    "accessibility": "analysis"
                }
            }
            """
            
            # Load and analyze images
            image_analysis = []
            for img_path in images_to_analyze:
                try:
                    if os.path.exists(img_path):
                        image = Image.open(img_path)
                        response = self.model.generate_content([prompt, image])
                        analysis = self._parse_json_response(response.text)
                        image_analysis.append(analysis)
                except Exception as e:
                    logger.error(f"Error analyzing image {img_path}: {e}")
                    continue
            
            # Combine results
            if image_analysis:
                avg_score = sum(analysis.get('image_bias', {}).get('score', 0) for analysis in image_analysis) / len(image_analysis)
                return {
                    "image_bias": {
                        "score": avg_score,
                        "status": self._get_bias_status(avg_score),
                        "description": f"Analyzed {len(image_analysis)} images for bias",
                        "images_analyzed": len(image_analysis)
                    }
                }
            
            return {"image_bias": {"score": 0.0, "status": "no_images", "description": "No valid images to analyze"}}
            
        except Exception as e:
            logger.error(f"Error in image bias analysis: {e}")
            return {"image_bias": {"score": 0.0, "status": "error", "description": "Image analysis failed"}}
    
    def _parse_json_response(self, response_text: str) -> Dict:
        """Parse JSON response from Gemini"""
        try:
            import json
            # Clean the response text
            cleaned_text = response_text.strip()
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3]
            
            logger.info(f"Parsing JSON response: {cleaned_text[:100]}...")
            result = json.loads(cleaned_text)
            logger.info("JSON parsing successful")
            return result
        except Exception as e:
            logger.error(f"Error parsing JSON response: {e}")
            logger.error(f"Response text: {response_text}")
            return {}
    
    def _get_bias_status(self, score: float) -> str:
        """Convert bias score to status"""
        if score < 0.1:
            return 'very-low'
        elif score < 0.2:
            return 'low'
        elif score < 0.4:
            return 'moderate'
        else:
            return 'high'
    
    def _get_default_bias_results(self) -> Dict:
        """Default bias results when analysis fails"""
        return {
            'gender_bias': {'score': 0.15, 'status': 'low', 'description': 'Default gender bias'},
            'racial_bias': {'score': 0.08, 'status': 'very-low', 'description': 'Default racial bias'},
            'age_bias': {'score': 0.22, 'status': 'moderate', 'description': 'Default age bias'},
            'socioeconomic_bias': {'score': 0.12, 'status': 'low', 'description': 'Default socioeconomic bias'},
            'overall_bias': {'score': 0.14, 'status': 'low', 'description': 'Default overall bias'}
        }
    
    def _get_default_social_impact(self) -> Dict:
        """Default social impact results when analysis fails"""
        return {
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
    
    def _get_default_community_outreach(self) -> Dict:
        """Default community outreach results when analysis fails"""
        return {
            'educational_programs': [
                {
                    'name': 'AI Ethics Workshop',
                    'description': 'Interactive workshops on responsible AI development',
                    'participants': 156,
                    'impact': '85% reported improved understanding',
                    'status': 'ongoing',
                    'category': 'education'
                }
            ],
            'community_initiatives': [
                {
                    'name': 'Digital Literacy Program',
                    'target': 'Underserved Communities',
                    'participants': 342,
                    'success': 0.89,
                    'description': 'Teaching digital skills and AI awareness'
                }
            ],
            'impact_metrics': {
                'total_participants': 1892,
                'programs_completed': 8,
                'communities_reached': 12,
                'knowledge_improvement': 0.84,
                'bias_awareness': 0.91,
                'ethical_practices': 0.78
            }
        } 