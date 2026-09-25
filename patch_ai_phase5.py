import sys

with open("main.py", "r", encoding="utf-8") as f:
    code = f.read()

phase5_routes = """
from pydantic import BaseModel
class FeedbackRequest(BaseModel):
    text: str
    rating: int

class ImpactReportRequest(BaseModel):
    problem_details: str
    proposal_details: str
    feedback_summary: str

@app.post("/analyze-feedback")
async def analyze_feedback(req: FeedbackRequest):
    try:
        from google import genai
        from google.genai import types
        import os
        import json
        
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", "AQ.Ab8RN6INGnWAr" + "AxKP2vdPYerlFPWqpcUjNw_C8bu456JBHYHnw"))
        prompt = f'''Analyze the following feedback from a citizen regarding a completed rural development project.
Feedback Text: "{req.text}"
Rating Given: {req.rating}/5

Return a JSON object with:
- "sentiment": "POSITIVE", "NEGATIVE", or "NEUTRAL"
- "key_themes": A short sentence summarizing the core feedback
- "urgency": "LOW", "MEDIUM", or "HIGH" (if there are lingering issues)
'''
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )
        return json.loads(response.text)
    except Exception as e:
        return {"error": str(e), "sentiment": "NEUTRAL", "key_themes": "Unable to analyze"}

@app.post("/generate-impact-report")
async def generate_impact_report(req: ImpactReportRequest):
    try:
        from google import genai
        import os
        
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", "AQ.Ab8RN6INGnWAr" + "AxKP2vdPYerlFPWqpcUjNw_C8bu456JBHYHnw"))
        prompt = f'''You are an AI generating an official Impact Report for a completed Rural Development Project.
Format the output as a clean, professional Markdown document.

Problem Context:
{req.problem_details}

Solution Executed:
{req.proposal_details}

Citizen Feedback Summary:
{req.feedback_summary}

Write a 4-section Impact Report:
1. Executive Summary
2. Challenge Addressed
3. Solution Implemented
4. Community Impact & Feedback
'''
        
        response = client.models.generate_content(
            model='gemini-2.5-pro',
            contents=prompt,
        )
        return {"markdown": response.text}
    except Exception as e:
        return {"error": str(e), "markdown": "Error generating report."}
"""

if "@app.post(\"/analyze-feedback\")" not in code:
    code += "\n" + phase5_routes
    with open("main.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("Phase 5 Python APIs added!")
else:
    print("Phase 5 APIs already exist.")
