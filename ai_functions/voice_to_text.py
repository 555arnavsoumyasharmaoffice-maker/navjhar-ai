import whisper
import os
import threading
from transformers import pipeline, AutoProcessor, AutoModelForSpeechSeq2Seq

# The large model needs several GB of RAM and, without a lock, simultaneous
# requests can each try to load it. That makes the transcription endpoint
# appear unavailable even though the audio upload itself succeeded.
whisper_model = None
whisper_model_lock = threading.Lock()
santali_pipeline = None
WHISPER_MODEL_NAME = "medium"

def transcribe_santali(audio_file_path: str) -> str:
    global santali_pipeline
    if santali_pipeline is None:
        print("Loading Santali Whisper model...")
        processor = AutoProcessor.from_pretrained("openai/whisper-small")
        model = AutoModelForSpeechSeq2Seq.from_pretrained("thunderboltc/whisper-small-santali-ol-chiki")
        santali_pipeline = pipeline(
            "automatic-speech-recognition",
            model=model,
            tokenizer=processor.tokenizer,
            feature_extractor=processor.feature_extractor
        )
        print("Santali model loaded successfully.")
    
    result = santali_pipeline(audio_file_path)
    return result["text"].strip()

def transcribe_multilingual(audio_file_path: str, language: str = "hindi") -> str:
    global whisper_model
    
    if not os.path.exists(audio_file_path):
        return "Error: File not found. Please provide a valid audio file path."
        
    valid_extensions = {".mp3", ".wav", ".m4a", ".flac", ".ogg", ".mp4", ".webm"}
    _, ext = os.path.splitext(audio_file_path)
    if ext.lower() not in valid_extensions:
        return f"Error: Unsupported file format '{ext}'. Please provide a valid audio file (e.g., .mp3, .wav)."
        
    try:
        language = language.lower()
        if language == "santali":
            return transcribe_santali(audio_file_path)
        else:
            if whisper_model is None:
                with whisper_model_lock:
                    if whisper_model is None:
                        print(f"Loading Whisper model ({WHISPER_MODEL_NAME})...")
                        whisper_model = whisper.load_model(WHISPER_MODEL_NAME)
                        print("Whisper model loaded successfully.")
                
            # Pass language and parameters to prevent short-audio hallucinations
            transcribe_kwargs = {
                "condition_on_previous_text": False,
                "no_speech_threshold": 0.6,
                "logprob_threshold": -1.0,
                "initial_prompt": "यह एक नागरिक की समस्या की रिपोर्ट है। मेरी समस्या यह है कि"
            }
            if language and language != "english": # Whisper auto-detects or we can force it
                transcribe_kwargs["language"] = language
            elif language == "english":
                transcribe_kwargs["task"] = "translate"
                transcribe_kwargs["initial_prompt"] = "This is a citizen problem report."
                
            result = whisper_model.transcribe(audio_file_path, fp16=False, **transcribe_kwargs)
            
            text = result["text"].strip()
# Catch common whisper hallucinations for short clips
            text_lower = text.lower().strip()
            hallucinations = ["thank you", "thanks for watching", "thank you very much", "you", "thank", "linear c", "subs by", "amara.org"]
            
            for h in hallucinations:
                if text_lower == h or text_lower == h + "." or text_lower.startswith(h):
                    if len(text_lower) < len(h) + 5: # If it's just the hallucination and nothing else
                        return "Error: Could not transcribe clearly. Please speak a longer sentence."
                
            return text
    except Exception as e:
        return f"Error during transcription: {str(e)}"
