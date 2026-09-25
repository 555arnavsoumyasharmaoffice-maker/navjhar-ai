import sys
import re

with open("ai_functions/solution_structuring.py", "r", encoding="utf-8") as f:
    code = f.read()

# We will replace ONLY the format_synthesis_prompt function string literal
old_func = """def format_synthesis_prompt(problem_context, list_of_solutions):
    prompt = "You are an AI problem-solving assistant that evaluates multiple raw solutions and recommends the absolute BEST solution.\\n\\n"
    prompt += f"Problem Context:\\n{problem_context}\\n\\n"
    prompt += "Submitted Solutions:\\n"
    for i, sol in enumerate(list_of_solutions):
        prompt += f"Solution {i+1}: {sol}\\n"
        
    prompt += "\\nTask: Analyze all submitted solutions for effectiveness, scalability, and cost-effectiveness. Your goal is to identify the BEST approach.\\n"
    prompt += "- In most cases, one of the submitted solutions will be the best. You should select it and refine it.\\n"
    prompt += "- If combining the best parts of multiple solutions yields a significantly better result, you may do that.\\n"
    prompt += "- If all submitted solutions are weak, you can add your own original points or formulate the best approach yourself.\\n"
    prompt += "- Do NOT forcefully combine bad ideas. Just recommend the single most optimal, practical, and effective approach.\\n\\n"
    prompt += "Provide your response strictly in the following JSON format:\\n"
    prompt += "{\\n"
    prompt += '  "individual_analysis": [\\n'
    prompt += '    {"solution_number": 1, "strength": "...", "weakness": "..."}\\n'
    prompt += '  ],\\n'
    prompt += '  "synthesized_solution": {\\n'
    prompt += '    "description": "Describe the final BEST recommended solution in 2-3 sentences",\\n'
    prompt += '    "title": "A short, descriptive title",\\n'
    prompt += '    "timeline": "Estimated timeline",\\n'
    prompt += '    "resources_needed": "Resources needed (budget, manpower, materials)",\\n'
    prompt += '    "feasibility_score": 85\\n'
    prompt += '  },\\n'
    prompt += '  "synthesis_reasoning": "Explain WHY this approach was chosen as the best, whether it came from a specific submission, a combination, or your own additions."\\n'
    prompt += "}\\n\\nOutput JSON:"
    return prompt"""

new_func = """def format_synthesis_prompt(problem_context, list_of_solutions):
    prompt = "You are an AI problem-solving assistant that evaluates multiple raw solutions and recommends the absolute BEST solution.\\n\\n"
    prompt += f"Problem Context:\\n{problem_context}\\n\\n"
    prompt += "Submitted Solutions:\\n"
    for i, sol in enumerate(list_of_solutions):
        prompt += f"Solution {i+1}: {sol}\\n"
        
    prompt += "\\nTask: Analyze all submitted solutions for effectiveness, scalability, and cost-effectiveness. Your goal is to identify the BEST approach.\\n"
    prompt += "- In most cases, one of the submitted solutions will be the best. You should select it and refine it.\\n"
    prompt += "- If combining the best parts of multiple solutions yields a significantly better result, you may do that.\\n"
    prompt += "- If all submitted solutions are weak, you can add your own original points or formulate the best approach yourself.\\n"
    prompt += "- Do NOT forcefully combine bad ideas. Just recommend the single most optimal, practical, and effective approach.\\n\\n"
    prompt += "Provide your response strictly in the following JSON format:\\n"
    prompt += "{\\n"
    prompt += '  "problem_understanding": "Describe the root cause and core challenges based on the context",\\n'
    prompt += '  "proposed_solution": "Detailed explanation of the final BEST recommended solution architecture",\\n'
    prompt += '  "technology_approach": "List the technologies, hardware, or algorithms needed",\\n'
    prompt += '  "expected_impact": "Describe the quantifiable improvements or benefits",\\n'
    prompt += '  "estimated_budget": "Provide a realistic estimated cost (e.g. 5,00,000 INR)",\\n'
    prompt += '  "timeline_months": 6,\\n'
    prompt += '  "synthesis_reasoning": "Explain WHY this approach was chosen based on the chat history."\\n'
    prompt += "}\\n\\nOutput JSON:"
    return prompt"""

start = code.find("def format_synthesis_prompt(problem_context, list_of_solutions):")
if start != -1:
    end = code.find("return prompt", start) + len("return prompt")
    code = code[:start] + new_func + code[end:]
    with open("ai_functions/solution_structuring.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("Function replaced correctly!")
else:
    print("Could not find function.")

