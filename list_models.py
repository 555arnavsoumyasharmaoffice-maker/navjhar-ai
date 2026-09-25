from google import genai
import os

key1 = "AQ.Ab8RN6KG-fwYzup2QrE"
key2 = "Xx0HulRQTqGtSbpLesYQZAzT6dnNcCg"
client = genai.Client(api_key=key1+key2)
for m in client.models.list():
    if "flash" in m.name:
        print(m.name)
