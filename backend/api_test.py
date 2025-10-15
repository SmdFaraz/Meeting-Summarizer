import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

print(f"API Key loaded: {api_key[:10]}..." if api_key else "NO API KEY!")

if api_key:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        response = model.generate_content("Say hello!")
        print("✅ API Key works!")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ API Error: {e}")
else:
    print("❌ No API key found in .env file!")
