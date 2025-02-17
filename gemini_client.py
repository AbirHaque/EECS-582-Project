# Importing necessary modules 
import os
import requests
from dotenv import load_dotenv
import logging
import time
import threading

# Loading environment variables from a .env file
load_dotenv()

# Retrieving the API key for Gemini from environment variables
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables.")

logger = logging.getLogger(__name__)

# Defining rate-limiting parameters
REQUEST_LIMIT = 15
REQUEST_WINDOW = 60
request_count = 0
window_start = time.time()
rate_limit_lock = threading.Lock()

# Function to generate content using the Gemini API
def generate_content(prompt_text):
    global request_count, window_start
    max_retries = 3
    delay = 1
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    payload = {
        "contents": [
            {
                "parts": [{"text": prompt_text}]
            }
        ]
    }
    headers = {"Content-Type": "application/json"}
    # Attempting the API request with retries
    for attempt in range(max_retries):
        with rate_limit_lock:
            now = time.time()
            if now - window_start >= REQUEST_WINDOW:
                logger.debug("Resetting local rate-limit counters")
                window_start = now
                request_count = 0
            if request_count >= REQUEST_LIMIT:
                sleep_time = REQUEST_WINDOW - (now - window_start)
                logger.info(f"Local rate limit reached (count: {request_count}). Sleeping for {sleep_time} seconds...")
                time.sleep(sleep_time)
                window_start = time.time()
                request_count = 0
            else:
                logger.debug(f"Local request count: {request_count}/{REQUEST_LIMIT}")
            request_count += 1
        # Handling rate-limiting errors 
        response = requests.post(url, headers=headers, json=payload)
        logger.info(f"Gemini API response status: {response.status_code}")
        if response.status_code == 429:
            with rate_limit_lock:
                now = time.time()
                remaining = REQUEST_WINDOW - (now - window_start)
                if remaining < delay:
                    remaining = delay
                logger.warning(f"API returned 429. Sleeping for {remaining} seconds to respect rate limits (attempt {attempt+1}/{max_retries}).")
                time.sleep(remaining)
                window_start = time.time()
                request_count = 0
            continue
        # If the request was successful, will process the response
        response.raise_for_status()
        json_response = response.json()
        logger.info(f"Gemini API response: {json_response}")
        return json_response
    # Raise an exception if all retries fail
    raise Exception("Gemini API request failed after retries")
