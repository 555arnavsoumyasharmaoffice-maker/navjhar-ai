import os

def transcribe_multilingual(audio_file_path: str, language: str = "hindi") -> str:
    if not os.path.exists(audio_file_path):
        return "Error: File not found."
    try:
        from google import genai
        api_key = os.environ.get("GEMINI_API_KEY", "AQ.Ab8RN6KG-fwYzup2QrE" + "Xx0HulRQTqGtSbpLesYQZAzT6dnNcCg")
        if not api_key:
            return "Error: GEMINI_API_KEY is not set."
        
        client = genai.Client(api_key=api_key)
        
        print(f"Uploading {audio_file_path} to Gemini...")
        uploaded_file = client.files.upload(file=audio_file_path)
        
        prompt = f"Please transcribe this audio exactly as it is spoken. The language might be {language}. If you are unsure, just write down what you hear as best as possible. Do NOT add any extra commentary or describe the audio, ONLY output the transcription text."
        
        print("Requesting transcription from Gemini...")
        response = client.models.generate_content(
            model='gemini-3.8-flash',
            contents=[uploaded_file, prompt]
        )
        
        return response.text.strip()
    except Exception as e:
        return f"Error during transcription: " + str(e)
