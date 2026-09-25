import os

def replace_in_file(filepath, search_str, replace_str):
    if not os.path.exists(filepath): return
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    if search_str in content:
        if "generate_with_gemini" not in content:
            content = "from ai_functions.gemini_helper import generate_with_gemini\n" + content
        content = content.replace(search_str, replace_str)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Patched {filepath}")
    else:
        print(f"Skipped {filepath} - search string not found")

replace_in_file(
    "ai_functions/impact_report.py",
    '''url = "http://localhost:11434/api/generate"
    payload = {
        "model": "llama3.1:8b",
        "prompt": prompt,
        "stream": False
    }
    
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
    
    try:
        response = urllib.request.urlopen(req, timeout=180)
        result = json.loads(response.read().decode("utf-8"))
        
        response_text = result.get("response", "Error generating report")''',
    '''try:
        response_text = generate_with_gemini(prompt, expect_json=False)'''
)

replace_in_file(
    "ai_functions/solver_matching.py",
    '''url = "http://localhost:11434/api/generate"
    payload = {
        "model": "llama3.1:8b",
        "prompt": prompt,
        "format": "json",
        "stream": False
    }
    
    request = urllib.request.Request(os.getenv("OLLAMA_URL", "http://localhost:11434").rstrip("/") + "/api/generate", data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
    
    try:
        response = urllib.request.urlopen(request, timeout=180)
        result = json.loads(response.read().decode("utf-8"))
        
        response_text = result.get("response", "{}")''',
    '''try:
        response_text = generate_with_gemini(prompt, expect_json=True)'''
)
