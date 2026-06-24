import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from google.genai import types
from fastapi import BackgroundTasks
from pydantic import BaseModel, Field
from typing import Literal, Dict, Any, Optional
import uuid

# Load from ../.env as it's in the project root
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

app = FastAPI(title="GitScribe API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for MVP
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)
else:
    client = None

from services.webhook_service import jobs, process_pr_webhook

class PullRequestWebhook(BaseModel):
    repository_id: str
    pr_number: int
    target_file: str
    diff: str

class WebhookAcceptedResponse(BaseModel):
    job_id: str
    status: str

class PRStatusResponse(BaseModel):
    status: Literal["processing", "completed", "failed"]
    analysis: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class GenerateRequest(BaseModel):
    diff: str

class GenerateResponse(BaseModel):
    commitMessage: str
    prDescription: str

@app.post("/generate", response_model=GenerateResponse)
def generate(request: GenerateRequest):
    if not client:
        raise HTTPException(status_code=500, detail="Gemini API key not configured")

    if not request.diff.strip():
        raise HTTPException(status_code=400, detail="Diff content is required")

    system_instruction = """You are an expert developer tool.
Given a git diff, you must generate a Conventional Commit message and a professional GitHub PR description.
Return ONLY valid JSON with this schema:
{
  "commitMessage": "string (The conventional commit message)",
  "prDescription": "string (The PR description including Summary, Changes, and Testing sections)"
}
Do NOT wrap the response in markdown codeblocks like ```json...```, just output the raw JSON object."""

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=request.diff,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
            ),
        )
        
        result_text = response.text
        if result_text.startswith("```json"):
            result_text = result_text[7:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]
            
        data = json.loads(result_text)
        return GenerateResponse(
            commitMessage=data.get("commitMessage", ""),
            prDescription=data.get("prDescription", "")
        )
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse JSON from AI: {e}\nResponse: {result_text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    neo4j_uri = os.getenv("NEO4J_URI")
    neo4j_status = "configured" if neo4j_uri else "missing"
    return {
        "status": "ok",
        "service": "GitScribe API",
        "neo4j_config": neo4j_status
    }

@app.post("/api/webhooks/pr", response_model=WebhookAcceptedResponse, status_code=202)
async def handle_pr_webhook(payload: PullRequestWebhook, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    
    # Initialize job state
    jobs[job_id] = {"status": "processing"}
    
    # Launch background processing
    background_tasks.add_task(process_pr_webhook, job_id, payload.target_file, payload.diff)
    
    return WebhookAcceptedResponse(job_id=job_id, status="processing")

@app.get("/api/pr/{job_id}", response_model=PRStatusResponse)
async def get_pr_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job ID not found")
        
    job_data = jobs[job_id]
    
    return PRStatusResponse(
        status=job_data["status"],
        analysis=job_data.get("analysis"),
        error=job_data.get("error")
    )
