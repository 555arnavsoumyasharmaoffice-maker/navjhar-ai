from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from ai_functions.sentiment import analyze_sentiment
from ai_functions.voice_to_text import transcribe_multilingual
from ai_functions.categorization import categorize_complaint
from ai_functions.idea_matching import find_similar_ideas_llm
from ai_functions.profile_categorization import categorize_expertise_profile
from ai_functions.solution_structuring import structure_solution, synthesize_best_solution
from ai_functions.impact_report import generate_impact_report
import shutil
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CategorizeRequest(BaseModel):
    text: str
    coordinates: Optional[str] = None
    existing_problems: Optional[List[Dict[str, Any]]] = None
    manual_category: Optional[str] = None

class TextRequest(BaseModel):
    text: str

class IdeaItem(BaseModel):
    text: str
    location: str

class IdeaRequest(BaseModel):
    ideas: List[IdeaItem]



class SynthesizeRequest(BaseModel):
    problem_context: str
    list_of_solutions: List[str]

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...), language: str = Form("hindi")):
    import shutil
    from fastapi import HTTPException
    
    file_location = f"temp_{file.filename}"
    try:
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        transcription = transcribe_multilingual(file_location, language)
        
        if transcription.startswith("Error:"):
            raise HTTPException(status_code=400, detail=transcription)
            
        return {"transcription": transcription}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(file_location):
            os.remove(file_location)

@app.get("/")
def read_root():
    return {"message": "AI Service is running!"}

@app.post("/analyze-sentiment")
def analyze_sentiment_endpoint(request: TextRequest):
    sentiment = analyze_sentiment(request.text)
    if not isinstance(sentiment, str) or sentiment.strip().lower() not in {"positive", "neutral", "negative"}:
        raise HTTPException(status_code=503, detail="Sentiment analysis unavailable")
    return {"sentiment": sentiment.strip().capitalize()}

@app.post("/categorize")
def categorize_endpoint(request: CategorizeRequest):
    result = categorize_complaint(request.text, request.coordinates, request.existing_problems, getattr(request, 'manual_category', None))
    if not isinstance(result, dict) or result.get("error"):
        raise HTTPException(status_code=503, detail="AI processing unavailable; retry the request")
    return result

@app.post("/find-similar-ideas")
def find_similar_ideas_endpoint(request: IdeaRequest):
    ideas_list = [{"text": idea.text, "location": idea.location} for idea in request.ideas]
    result = find_similar_ideas_llm(ideas_list)
    if not isinstance(result, dict) or result.get("error"):
        raise HTTPException(status_code=503, detail="AI processing unavailable; retry the request")
    return result

@app.post("/categorize-profile")
def categorize_profile_endpoint(request: TextRequest):
    result = categorize_expertise_profile(request.text)
    if not isinstance(result, dict) or result.get("error"):
        raise HTTPException(status_code=503, detail="AI processing unavailable; retry the request")
    return result

@app.post("/structure-solution")
def structure_solution_endpoint(request: TextRequest):
    result = structure_solution(request.text)
    if not isinstance(result, dict) or result.get("error"):
        raise HTTPException(status_code=503, detail="AI processing unavailable; retry the request")
    return result

@app.post("/synthesize-solution")
def synthesize_solution_endpoint(request: SynthesizeRequest):
    result = synthesize_best_solution(request.problem_context, request.list_of_solutions)
    if not isinstance(result, dict) or result.get("error"):
        raise HTTPException(status_code=503, detail="AI processing unavailable; retry the request")
    return result

class MatchSolversRequest(BaseModel):
    problem: Dict[str, Any]
    solvers: List[Dict[str, Any]]


@app.post("/match-solvers")
def match_solvers_endpoint(request: MatchSolversRequest):
    from fastapi import HTTPException
    from ai_functions.solver_matching import match_problem_to_solvers
    ids = [str(s.get("solver_id", "")) for s in request.solvers]
    if any(not i or not i.isdigit() for i in ids) or len(set(ids)) != len(ids):
        raise HTTPException(status_code=422, detail="Unique numeric solver IDs are required")
    result = match_problem_to_solvers(request.problem, request.solvers)
    if result.get("error"):
        raise HTTPException(status_code=503, detail=result["error"])
    return result


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
    import urllib.request, json
    try:
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
        
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": "llama3.1:8b",
            "prompt": prompt,
            "stream": False
        }
        
        req_obj = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
        response = urllib.request.urlopen(req_obj, timeout=180)
        result = json.loads(response.read().decode("utf-8"))
        
        text = result.get("response", "Error generating report")
        return {"markdown": text}
    except Exception as e:
        return {"error": str(e), "markdown": f"Error generating report: {str(e)}"}
