import sys

with open("main.py", "r", encoding="utf-8") as f:
    code = f.read()

bad_func = """@app.post("/generate-impact-report")
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
        return {"error": str(e), "markdown": "Error generating report."}"""

good_func = """@app.post("/generate-impact-report")
async def generate_impact_report(req: ImpactReportRequest):
    import urllib.request, json, os
    try:
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            # Let's read from backend/.env if needed
            try:
                with open("../backend/.env", "r") as envf:
                    for line in envf:
                        if line.startswith("GEMINI_API_KEY="):
                            api_key = line.split("=", 1)[1].strip()
            except: pass
            
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
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={api_key}"
        data = {"contents": [{"parts": [{"text": prompt}]}]}
        
        req_obj = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers={"Content-Type": "application/json"})
        response = urllib.request.urlopen(req_obj, timeout=30)
        res_data = json.loads(response.read().decode("utf-8"))
        
        text = res_data["candidates"][0]["content"]["parts"][0]["text"]
        return {"markdown": text}
    except Exception as e:
        return {"error": str(e), "markdown": f"Error generating report: {str(e)}"}"""

if bad_func in code:
    code = code.replace(bad_func, good_func)
    with open("main.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("Replaced with urllib.request HTTP call directly to Gemini API!")
else:
    print("Could not find the function to replace")
