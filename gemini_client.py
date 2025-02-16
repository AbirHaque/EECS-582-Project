import os
import requests
from dotenv import load_dotenv
import logging

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables.")

logger = logging.getLogger(__name__)

def generate_content(prompt_text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    payload = {
        "contents": [
            {
                "parts": [{"text": prompt_text}]
            }
        ]
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json=payload)
    logger.info(f"Gemini API response status: {response.status_code}")
    response.raise_for_status()
    json_response = response.json()
    logger.info(f"Gemini API response: {json_response}")
    return json_response
