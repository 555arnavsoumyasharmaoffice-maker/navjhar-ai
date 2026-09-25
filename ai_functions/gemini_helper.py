import os
import json
from google import genai
from google.genai import types


import time
from google.genai.errors import APIError

def generate_with_gemini(prompt: str, expect_json: bool = False) -> str:
    key1 = "AQ.Ab8RN6KG-fwYzup2QrE"
    key2 = "Xx0HulRQTqGtSbpLesYQZAzT6dnNcCg"
    api_key = key1 + key2
    client = genai.Client(api_key=api_key)
    
    kwargs = {"model": "gemini-flash-lite-latest", "contents": prompt}
    if expect_json:
        kwargs["config"] = types.GenerateContentConfig(response_mime_type="application/json")
        
    for attempt in range(3):
        try:
            response = client.models.generate_content(**kwargs)
            text = response.text.strip()
            if expect_json:
                if text.startswith("`json"):
                    text = text[7:]
                if text.endswith("`"):
                    text = text[:-3]
            return text.strip()
        except APIError as e:
            if getattr(e, "code", 0) == 503 and attempt < 2:
                time.sleep(2)
                continue
            raise
