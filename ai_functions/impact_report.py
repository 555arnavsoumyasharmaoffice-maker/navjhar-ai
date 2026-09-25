from ai_functions.gemini_helper import generate_with_gemini
import json
import urllib.request
import urllib.error

def format_prompt(challenge_data, solution_data, feedback_list):
    prompt = "You are an expert report writer for a civic tech organization. Your task is to generate a professional, highly readable Impact Case Study Report based on the provided data.\n\n"
    
    prompt += "The report should include the following sections:\n"
    prompt += "1. Problem Summary\n"
    prompt += "2. Solution Implemented\n"
    prompt += "3. Timeline\n"
    prompt += "4. Citizen Sentiment/Satisfaction Summary\n"
    prompt += "5. Key Outcome/Impact Statement\n\n"
    
    prompt += "Use professional English. Do NOT output JSON, just output the plain text report.\n\n"
    
    prompt += "=== DATA ===\n"
    prompt += f"Challenge Data: {json.dumps(challenge_data)}\n"
    prompt += f"Solution Data: {json.dumps(solution_data)}\n"
    prompt += f"Feedback List (Citizen reviews): {json.dumps(feedback_list)}\n\n"
    
    prompt += "=== IMPACT REPORT ===\n"
    return prompt

def generate_impact_report(challenge_data: dict, solution_data: dict, feedback_list: list) -> str:
    prompt = format_prompt(challenge_data, solution_data, feedback_list)
    
    try:
        response_text = generate_with_gemini(prompt, expect_json=False)
        return response_text
    except urllib.error.URLError as e:
        return f"Failed to connect to Ollama server: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"
