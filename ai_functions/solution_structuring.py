import json
import urllib.request
import urllib.error

def format_prompt(text):
    prompt = "You are an AI assistant that structures raw solution proposals from universities, industries, or NGOs.\n\n"
    prompt += "Task: Read the following raw solution text and extract the key details into a structured JSON format.\n"
    prompt += "Extract the following fields:\n"
    prompt += "- title: A short, descriptive title for the solution.\n"
    prompt += "- timeline: The estimated time to complete the solution, as mentioned in the text.\n"
    prompt += "- resources_needed: A summary of the budget, manpower, materials, or other resources mentioned.\n"
    prompt += "- feasibility_score: Estimate a feasibility score between 0 and 100 based on how well-defined and practical the proposal is. Return just the integer.\n\n"
    prompt += "Format expected:\n"
    prompt += "{\n"
    prompt += '  "title": "",\n'
    prompt += '  "timeline": "",\n'
    prompt += '  "resources_needed": "",\n'
    prompt += '  "feasibility_score": 0\n'
    prompt += "}\n\n"
    
    prompt += f"Raw Solution Text:\n{text}\n\nOutput JSON:"
    return prompt

def structure_solution(raw_solution_text: str) -> dict:
    prompt = format_prompt(raw_solution_text)
    
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
def format_synthesis_prompt(problem_context, list_of_solutions):
    prompt = "You are an AI problem-solving assistant that evaluates multiple raw solutions and recommends the absolute BEST solution.\n\n"
    prompt += f"Problem Context:\n{problem_context}\n\n"
    prompt += "Submitted Solutions:\n"
    for i, sol in enumerate(list_of_solutions):
        prompt += f"Solution {i+1}: {sol}\n"
        
    prompt += "\nTask: Analyze all submitted solutions for effectiveness, scalability, and cost-effectiveness. Your goal is to identify the BEST approach.\n"
    prompt += "- In most cases, one of the submitted solutions will be the best. You should select it and refine it.\n"
    prompt += "- If combining the best parts of multiple solutions yields a significantly better result, you may do that.\n"
    prompt += "- If all submitted solutions are weak, you can add your own original points or formulate the best approach yourself.\n"
    prompt += "- Do NOT forcefully combine bad ideas. Just recommend the single most optimal, practical, and effective approach.\n\n"
    prompt += "Provide your response strictly in the following JSON format:\n"
    prompt += "{\n"
    prompt += '  "problem_understanding": "Describe the root cause and core challenges based on the context",\n'
    prompt += '  "proposed_solution": "Detailed explanation of the final BEST recommended solution architecture",\n'
    prompt += '  "technology_approach": "List the technologies, hardware, or algorithms needed",\n'
    prompt += '  "expected_impact": "Describe the quantifiable improvements or benefits",\n'
    prompt += '  "estimated_budget": "Provide a realistic estimated cost (e.g. 5,00,000 INR)",\n'
    prompt += '  "timeline_months": 6,\n'
    prompt += '  "synthesis_reasoning": "Explain WHY this approach was chosen based on the chat history."\n'
    prompt += "}\n\nOutput JSON:"
    return prompt

def synthesize_best_solution(problem_context: str, list_of_solutions: list) -> dict:
    prompt = format_synthesis_prompt(problem_context, list_of_solutions)
    
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
