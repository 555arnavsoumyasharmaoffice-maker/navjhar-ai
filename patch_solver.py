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
    "ai_functions/solver_matching.py",
    '''payload = {"model": os.getenv("OLLAMA_MODEL", "llama3.1:8b"), "prompt": prompt, "format": "json", "stream": False}
    request = urllib.request.Request(os.getenv("OLLAMA_URL", "http://localhost:11434").rstrip("/") + "/api/generate", data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            result = json.loads(json.loads(response.read())["response"])''',
    '''try:
        response_text = generate_with_gemini(prompt, expect_json=True)
        result = json.loads(response_text)'''
)
