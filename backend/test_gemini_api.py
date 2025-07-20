import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_gemini_api():
    """Test Gemini API connection"""
    try:
        # Get API key
        api_key = os.getenv('GEMINI_API_KEY')
        print(f"API Key found: {'Yes' if api_key else 'No'}")
        print(f"API Key length: {len(api_key) if api_key else 0}")
        print(f"API Key starts with: {api_key[:10]}..." if api_key else "No API key")
        
        if not api_key:
            print("❌ GEMINI_API_KEY not found in environment variables")
            return False
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Test with a simple prompt
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        print("🤖 Testing Gemini API connection...")
        
        response = model.generate_content("Hello! Please respond with 'API connection successful' if you can see this message.")
        
        print("✅ API Response received!")
        print(f"Response: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Gemini API: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Gemini API Setup...")
    print("=" * 50)
    
    success = test_gemini_api()
    
    print("=" * 50)
    if success:
        print("✅ Gemini API is working correctly!")
    else:
        print("❌ Gemini API test failed!")
        print("\n🔧 Troubleshooting steps:")
        print("1. Make sure your API key is correct")
        print("2. Check if the API key has proper permissions")
        print("3. Verify the API key is enabled for Gemini API")
        print("4. Try regenerating the API key") 