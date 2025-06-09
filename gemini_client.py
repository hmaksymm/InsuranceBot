import requests
from config import GOOGLE_GEMINI_API_KEY

class GeminiClient:
    def __init__(self):
        self.api_key = GOOGLE_GEMINI_API_KEY
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.model = "models/gemini-2.0-flash"
        self.headers = {
            'Content-Type': 'application/json'
        }
    
    def test_gemini(self):
        try:
            url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"
            payload = {
                "contents": [{
                    "parts": [{
                        "text": "Explain how AI works in a few words"
                    }]
                }]
            }
            
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                return result['candidates'][0]['content']['parts'][0]['text']
            return "No response generated"
        except Exception as e:
            print(f"Test error details: {str(e)}")
            return f"Error in test: {str(e)}"
    
    def communicate(self, message: str) -> str:
        try:
            url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"
            payload = {
                "contents": [{
                    "parts": [{
                        "text": message
                    }]
                }]
            }
            
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                return result['candidates'][0]['content']['parts'][0]['text']
            return "No response generated"
        except Exception as e:
            print(f"Communication error details: {str(e)}")
            return f"Error generating response: {str(e)}"


