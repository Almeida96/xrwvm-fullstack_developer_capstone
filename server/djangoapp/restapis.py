import os
import requests
from dotenv import load_dotenv

load_dotenv()

# The starter template contains a placeholder backend_url in .env.
# Use the local Node.js service unless a valid HTTP(S) URL is configured.
configured_backend_url = os.getenv("backend_url", "").strip()
backend_url = (
    configured_backend_url
    if configured_backend_url.startswith(("http://", "https://"))
    else "http://127.0.0.1:3030"
)

configured_sentiment_url = os.getenv("sentiment_analyzer_url", "").strip()
sentiment_analyzer_url = (
    configured_sentiment_url
    if configured_sentiment_url.startswith(("http://", "https://"))
    else "http://127.0.0.1:5050/"
)

def get_request(endpoint, **kwargs):
    """Request JSON from the dealership Node.js API."""
    url = f"{backend_url.rstrip('/')}/{endpoint.lstrip('/')}"
    response = requests.get(url, timeout=15, **kwargs)
    response.raise_for_status()
    return response.json()

# def analyze_review_sentiments(text):
#     request_url = sentiment_analyzer_url + "analyze/" + text
#     # Implementation is part of a later capstone task.

def post_review(data_dict):
    """Send a new dealership review to the Node.js/MongoDB backend."""
    url = f"{backend_url.rstrip('/')}/insert_review"
    response = requests.post(url, json=data_dict, timeout=15)
    response.raise_for_status()
    return response.json()
