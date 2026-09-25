import os

files_json = [
    "ai_functions/categorization.py",
    "ai_functions/idea_matching.py",
    "ai_functions/profile_categorization.py",
    "ai_functions/sentiment.py",
    "ai_functions/solution_structuring.py",
    "ai_functions/solver_matching.py"
]

files_text = [
    "ai_functions/impact_report.py",
    "main.py"
]

def apply_patch(filepath, is_json):
    if not os.path.exists(filepath): return
    with open(filepath, "r", encoding="utf-8") as f:
        code = f.read()

    if "from ai_functions.gemini_helper import generate_with_gemini" not in code:
        code = "from ai_functions.gemini_helper import generate_with_gemini\n" + code

    new_code_lines = []
    lines = code.split("\n")
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check if start of ollama block
        if "http://localhost:11434/api/generate" in line or "OLLAMA_URL" in line:
            indent = len(line) - len(line.lstrip())
            ind = " " * indent
            
            if is_json:
                new_code_lines.append(ind + "try:")
                new_code_lines.append(ind + "    import json")
                new_code_lines.append(ind + "    response_text = generate_with_gemini(prompt, expect_json=True)")
                new_code_lines.append(ind + "    parsed_json = json.loads(response_text)")
            else:
                new_code_lines.append(ind + "try:")
                new_code_lines.append(ind + "    text = generate_with_gemini(prompt, expect_json=False)")
                
            # Skip lines until we find except 
            while i < len(lines):
                if "except urllib.error.URLError" in lines[i] or "except Exception" in lines[i] or "except urllib.error" in lines[i]:
                    new_code_lines.append(lines[i])
                    break
                
                # Copy the specific logic that parses json and returns
                if is_json and ("if not candidates:" in lines[i] or "parsed_json[" in lines[i] or "return parsed_json" in lines[i] or "if not parsed_json" in lines[i] or "return {" in lines[i] and not "payload =" in lines[i] and not "url =" in lines[i] and not "req =" in lines[i] and not "json.loads" in lines[i]):
                    new_code_lines.append(lines[i])
                elif not is_json and "return" in lines[i] and "markdown" in lines[i]:
                    new_code_lines.append(lines[i])
                i += 1
        else:
            new_code_lines.append(line)
        i += 1
        
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(new_code_lines))

for f in files_json: apply_patch(f, True)
for f in files_text: apply_patch(f, False)
