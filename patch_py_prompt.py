import sys
import re

with open("ai_functions/solution_structuring.py", "r", encoding="utf-8") as f:
    code = f.read()

old_json_format = """      prompt += "{\\n"
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
    prompt += "}\\n\\nOutput JSON:" """

new_json_format = """    prompt += "{\\n"
    prompt += '  "problem_understanding": "Describe the root cause and core challenges based on the context",\\n'
    prompt += '  "proposed_solution": "Detailed explanation of the final BEST recommended solution architecture",\\n'
    prompt += '  "technology_approach": "List the technologies, hardware, or algorithms needed",\\n'
    prompt += '  "expected_impact": "Describe the quantifiable improvements or benefits",\\n'
    prompt += '  "estimated_budget": "Provide a realistic estimated cost (e.g. ₹5,00,000)",\\n'
    prompt += '  "timeline_months": 6,\\n'
    prompt += '  "synthesis_reasoning": "Explain WHY this approach was chosen based on the chat history."\\n'
    prompt += "}\\n\\nOutput JSON:" """

# Since python strings might have different whitespace, we'll replace using regex targeting the block
import re
# Find the start of the block
start_str = 'prompt += "{\\n"'
end_str = 'prompt += "}\\n\\nOutput JSON:"'

start = code.find(start_str)
end = code.find(end_str) + len(end_str)

if start != -1 and end != -1:
    code = code[:start] + new_json_format + code[end:]
    with open("ai_functions/solution_structuring.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("Python AI Prompt Updated successfully!")
else:
    print("Could not find the JSON block in python file.")
