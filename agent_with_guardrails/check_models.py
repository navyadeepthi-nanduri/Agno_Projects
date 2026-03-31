import os
from dotenv import load_dotenv
from google import genai

# load .env
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ API key not found in .env")
    exit()

# create client
client = genai.Client(api_key=api_key)

print("\n🔍 Available Gemini models for your API key:\n")

try:
    for model in client.models.list():
        print(model.name)
except Exception as e:
    print("Error:", e)