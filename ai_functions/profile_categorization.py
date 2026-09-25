import json
import urllib.request
import urllib.error
import os

DATASET_FILE = "sample_data/profiles_dataset.json"

def get_few_shot_examples():
    try:
        with open(DATASET_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data[:5]  # Take first 5 examples to keep prompt reasonable
    except Exception as e:
        print(f"Failed to load profile examples: {e}")
        return []

def format_prompt(text, examples):
    prompt = "You are an AI assistant that analyzes and categorizes expertise profiles (from Universities, Industry, or NGOs).\n\n"
    prompt += "Task: Analyze the given profile text and extract the following information in JSON format:\n"
    prompt += "- expertise: A list of strings. Valid categories: [Water, Health, Education, Infrastructure, Agriculture, Science, Technology, Engineering, Management, Humanities, Social Sciences, etc.]. Extract domains accurately based on the text.\n"
    prompt += "- capabilities: A list of strings detailing specific facilities, resources, or skills mentioned.\n"
    prompt += "- entity_type_suggestion: One of [University, Industry, NGO].\n\n"
    prompt += "Respond ONLY with a valid JSON object. All text must be in English.\n\n"
    
    if examples:
        prompt += "Here are some examples:\n\n"
        for ex in examples:
            prompt += f"Input: {ex['input']}\n"
            prompt += f"Output: {json.dumps(ex['output'])}\n\n"
            
    prompt += f"Now process the following profile.\nInput: {text}\nOutput:"
    return prompt

def categorize_expertise_profile(profile_text: str) -> dict:
    examples = get_few_shot_examples()
    prompt = format_prompt(profile_text, examples)
    
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "llama3.1:8b",
        "prompt": prompt,
        "format": "json",
        "stream": False
    }
    
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
    
    try:
        response = urllib.request.urlopen(req, timeout=180)
        result = json.loads(response.read().decode("utf-8"))
        
        response_text = result.get("response", "{}")
        parsed_json = json.loads(response_text)
        return parsed_json
    except urllib.error.URLError as e:
        return {"error": f"Failed to connect to Ollama server: {str(e)}"}
    except json.JSONDecodeError:
        return {"error": "LLM returned invalid JSON"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}
