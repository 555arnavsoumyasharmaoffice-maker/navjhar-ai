import json
import urllib.request
import urllib.error
import os
import math

COMPLAINTS_FILE = os.path.join("sample_data", "complaints_updated.json")

def calculate_distance_meters(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c

def parse_coordinates(coord_str):
    if not coord_str:
        return None
    try:
        parts = coord_str.split(',')
        return (float(parts[0].strip()), float(parts[1].strip()))
    except:
        return None

def get_few_shot_examples():
    try:
        with open(COMPLAINTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        categories_seen = set()
        examples = []
        for item in data:
            cat = item["output"]["category"]
            if cat not in categories_seen:
                categories_seen.add(cat)
                examples.append(item)
            if len(examples) >= 3:
                break
                
        # Add one explicit duplicate example
        examples.append({
            "input": "There is a huge pothole near the main market",
            "output": {
                "category": "Roads",
                "confidence": 95,
                "severity": "HIGH",
                "priorityScore": 85,
                "isDuplicate": True,
                "duplicateOfId": "JH-ABC-1234",
                "requiredSkills": ["Road Repair"],
                "expectedImpact": "Repairing the road will prevent accidents."
            }
        })
            
        return examples
    except Exception as e:
        print(f"Failed to load examples: {e}")
        return []

def format_prompt(text, candidates, examples, manual_category=None):
    prompt = "You are an AI assistant that categorizes civic complaints from citizens in India (often written in Hindi, English, or mixed language).\n\n"
    prompt += "Task: Analyze the given complaint and extract the following information strictly in JSON format. Do not add any extra fields. YOU MUST INCLUDE ALL THE FIELDS LISTED BELOW.\n\n"
    if manual_category:
        prompt += f"\nUSER MANUAL SELECTION: The user has explicitly selected the category '{manual_category}'. Unless the text completely contradicts this, you MUST set the category to '{manual_category}'.\n\n"
    prompt += "Fields to extract:\n"
    prompt += "- category (String): Exactly ONE of [Agriculture, Water, Healthcare, Education, Roads, Sanitation, Environment, Electricity, Public Services, Other].\n"
    prompt += "- confidence (Integer): 0 to 100 representing how confident you are in the category.\n"
    prompt += "- severity (String): Exactly ONE of [LOW, MEDIUM, HIGH, CRITICAL]. Use uppercase.\n"
    prompt += "- priorityScore (Integer): 0 to 100 representing the overall priority/importance of the issue.\n"
    prompt += "- requiredSkills (Array of Strings): Professional skills/domains needed to solve this issue (e.g., [\"Water Quality Analysis\", \"Environmental Engineering\"]).\n"
    prompt += "- expectedImpact (String): A brief description of the quantifiable or qualitative impact of solving the issue.\n"
    prompt += "- professionalDraft (String): A professional, formal, official-sounding rewrite of the complaint, suitable for government/university officials. MUST be generated for EVERY request.\n"
    prompt += "- categoryChangeReason (String or null): IF AND ONLY IF you disagree with the USER MANUAL SELECTION and change the category, explain WHY in 1-2 polite sentences. Otherwise, null.\n"
    
    prompt += "\nDuplicate Detection:\n"
    if candidates and len(candidates) > 0:
        prompt += "CRITICAL INSTRUCTION: The following problems are already confirmed to be within 2000 meters of the new complaint's location.\n"
        prompt += "Your only task is to determine if they describe the SAME underlying issue, regardless of exact wording. If there is a 70% or higher semantic overlap/similarity in the problem described, you MUST flag it as a duplicate (isDuplicate: true).\n"
        prompt += "Existing candidate problems:\n"
        for ep in candidates:
            prompt += f"ID: {ep.get('id', '')}, Text: '{ep.get('text', '')}'\n"
        prompt += "\n- isDuplicate (Boolean): true if a semantically identical issue is found in the candidates list, otherwise false.\n"
        prompt += "- duplicateOfId (String or null): The ID of the existing problem if duplicate, otherwise null.\n"
    else:
        prompt += "- isDuplicate (Boolean): Always false (no nearby candidates provided).\n"
        prompt += "- duplicateOfId (String or null): Always null.\n"
        
    prompt += "\nFormat expected exactly like this (Set isDuplicate to true/false and duplicateOfId to ID/null accordingly):\n"
    prompt += "{\n"
    prompt += '  "category": "<Insert Category>",\n'
    prompt += '  "confidence": 90,\n'
    prompt += '  "severity": "<Insert Severity>",\n'
    prompt += '  "priorityScore": 85,\n'
    prompt += '  "isDuplicate": true_or_false,\n'
    prompt += '  "duplicateOfId": "ID_String_or_null",\n'
    prompt += '  "requiredSkills": ["<Skill 1>", "<Skill 2>"],\n'
    prompt += '  "expectedImpact": "<Insert Description>"\n'
    prompt += '  "professionalDraft": "<Insert Professional Rewrite>",\n'
    prompt += '  "categoryChangeReason": "<Insert Reason or null>"\n'
    prompt += "}\n\n"
    
    if examples and len(examples) > 0:
        prompt += "Here are some examples of valid categorizations:\n\n"
        for ex in examples:
            prompt += f"Input text: {ex['input']}\n"
            if ex.get("output", {}).get("isDuplicate") is True:
                prompt += "Existing candidate problems:\nID: 404, Text: 'The road near market is broken'\n"
            prompt += f"Output JSON: {json.dumps(ex['output'])}\n\n"
    
    prompt += f"Now process the following complaint.\nInput text: {text}\nOutput JSON:"
    return prompt

def categorize_complaint(text: str, coordinates: str = None, existing_problems: list = None, manual_category: str = None) -> dict:
    candidates = []
    
    # Pre-filter by distance if coordinates and existing_problems are provided
    if coordinates and existing_problems:
        new_coords = parse_coordinates(coordinates)
        if new_coords:
            for ep in existing_problems:
                ep_coords = parse_coordinates(ep.get('coordinates'))
                if ep_coords:
                    dist = calculate_distance_meters(new_coords[0], new_coords[1], ep_coords[0], ep_coords[1])
                    if dist <= 2000:
                        candidates.append(ep)

    examples = get_few_shot_examples()
    prompt = format_prompt(text, candidates, examples, manual_category)
    
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
        
        # Override duplicate flag if no candidates (failsafe against LLM hallucination)
        if not candidates:
            parsed_json["isDuplicate"] = False
            parsed_json["duplicateOfId"] = None
            
        # Add original text explicitly via python to avoid LLM hallucination
        parsed_json["originalText"] = text
            
        return parsed_json
    except urllib.error.URLError as e:
        return {"error": f"Failed to connect to Ollama server: {str(e)}"}
    except json.JSONDecodeError:
        return {"error": "LLM returned invalid JSON"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}
