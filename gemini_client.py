import requests
from config import GOOGLE_GEMINI_API_KEY
import json

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
            
            if response.status_code == 401:
                return "Authentication error: Please check your API key"
            elif response.status_code == 400:
                return "Invalid request: Please check your request format"
            
            response.raise_for_status()
            
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                return result['candidates'][0]['content']['parts'][0]['text']
            return "No response generated"
        except requests.exceptions.RequestException as e:
            print(f"Network error: {str(e)}")
            return f"Network error occurred: {str(e)}"
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {str(e)}")
            return "Error parsing API response"
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return f"Unexpected error: {str(e)}"
    
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
            
            if response.status_code == 401:
                return "Authentication error: Please check your API key"
            elif response.status_code == 400:
                return "Invalid request: Please check your request format"
                
            response.raise_for_status()
            
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                return result['candidates'][0]['content']['parts'][0]['text']
            return "No response generated"
        except requests.exceptions.RequestException as e:
            print(f"Network error: {str(e)}")
            return f"Network error occurred: {str(e)}"
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {str(e)}")
            return "Error parsing API response"
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return f"Unexpected error: {str(e)}"


