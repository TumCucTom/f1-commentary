#!/usr/bin/env python3
"""
Test script to debug Groq API connection issues
"""

import os
import requests
from dotenv import load_dotenv

def test_groq_api():
    """Test the Groq API connection with a simple request."""
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("Error: GROQ_API_KEY not found in .env file")
        return
    
    print(f"API Key found: {api_key[:10]}...{api_key[-10:]}")
    
    # Test with a simple request
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Try different model names
    models_to_try = [
        "llama-3.1-8b-instant",
        "llama-3.1-70b-versatile", 
        "mixtral-8x7b-32768",
        "gemma-7b-it"
    ]
    
    for model in models_to_try:
        print(f"\nTrying model: {model}")
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": "Hello, this is a test message."
                }
            ],
            "temperature": 0.7,
            "max_tokens": 50
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Model {model} works!")
                print(f"Response: {result['choices'][0]['message']['content']}")
                return model  # Return the working model
            else:
                print(f"❌ Model {model} failed: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception with {model}: {e}")
    
    return None
    
    print("Sending test request to Groq API...")
    print(f"URL: {url}")
    print(f"Model: {payload['model']}")
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API call successful!")
            print(f"Response: {result}")
        else:
            print("❌ API call failed!")
            print(f"Error response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception occurred: {e}")

if __name__ == "__main__":
    test_groq_api()
