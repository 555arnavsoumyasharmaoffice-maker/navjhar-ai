import requests
import json

url = "https://navjhar-ai.onrender.com/categorize"
data = {"text": "There is a big pothole on the road"}

try:
    response = requests.post(url, json=data)
    print("Status:", response.status_code)
    print("Body:", response.text)
except Exception as e:
    print(e)
