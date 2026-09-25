import os
import json
from google import genai
from google.genai import types

def generate_with_gemini(prompt: str, expect_json: bool = False) -> str:
    key1 = "AQ.Ab8RN6KG-fwYzup2QrE"
    key2 = "Xx0HulRQTqGtSbpLesYQZAzT6dnNcCg"
    api_key = os.environ.get("GEMINI_API_KEY", key1 + key2)
    client = genai.Client(api_key=api_key)
    
    kwargs = {"model": "gemini-3.8-flash", "contents": prompt}
    if expect_json:
        kwargs["config"] = types.GenerateContentConfig(response_mime_type="application/json")
        
    response = client.models.generate_content(**kwargs)
    text = response.text.strip()
    if expect_json:
        if text.startswith("`json"):
            text = text[7:]
        if text.endswith("`"):
            text = text[:-3]
    return text.strip()
