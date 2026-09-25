import requests
import json

def analyze_sentiment(feedback_text: str) -> str:
    url = "http://localhost:11434/api/generate"
    prompt = (
        "Analyze the sentiment of the following feedback. "
        "Respond with ONLY ONE WORD: 'Positive', 'Negative', or 'Neutral'.\n\n"
        f"Feedback: '{feedback_text}'"
    )
    
    payload = {
        "model": "llama3.1:8b",
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(url, json=payload, timeout=180)
        response.raise_for_status()
        result = response.json()
        sentiment = result.get("response", "").strip()
        return sentiment
    except Exception as e:
        return f"Error: {str(e)}"
