from ai_functions.gemini_helper import generate_with_gemini
import requests
import json

def analyze_sentiment(feedback_text: str) -> str:
    prompt = (
        "Analyze the sentiment of the following feedback. "
        "Respond with ONLY ONE WORD: 'Positive', 'Negative', or 'Neutral'.\n\n"
        f"Feedback: '{feedback_text}'"
    )
    
    try:
        sentiment = generate_with_gemini(prompt, expect_json=False)
        return sentiment
    except Exception as e:
        return f"Error: {str(e)}"
