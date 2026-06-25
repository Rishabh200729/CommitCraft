import os
import json
import uuid
from fastapi import APIRouter, HTTPException, BackgroundTasks
from google import genai
from google.genai import types

from app.schemas.api import (
    PullRequestWebhook, 
    WebhookAcceptedResponse, 
    PRStatusResponse, 
    GenerateRequest, 
    GenerateResponse
)
from app.services.webhook_service import jobs, process_pr_webhook

router = APIRouter()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)
else:
    client = None
# this endpoint is used for generating git commit message and pr description for a single file
@router.post("/generate", response_model=GenerateResponse)
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

@router.get("/health")
def health_check():
    neo4j_uri = os.getenv("NEO4J_URI")
    neo4j_status = "configured" if neo4j_uri else "missing"
    return {
        "status": "ok",
        "service": "GitScribe API",
        "neo4j_config": neo4j_status
    }
# this endpoint is used for processing the pull request webhook
@router.post("/api/webhooks/pr", response_model=WebhookAcceptedResponse, status_code=202)
async def handle_pr_webhook(payload: PullRequestWebhook, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    
    # Initialize job state
    jobs[job_id] = {"status": "processing"}
    
    # Launch background processing
    background_tasks.add_task(process_pr_webhook, job_id, payload.target_file, payload.diff)
    
    return WebhookAcceptedResponse(job_id=job_id, status="processing")

@router.get("/api/pr/{job_id}", response_model=PRStatusResponse)
async def get_pr_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job ID not found")
        
    job_data = jobs[job_id]
    
    return PRStatusResponse(
        status=job_data["status"],
        analysis=job_data.get("analysis"),
        error=job_data.get("error")
    )
