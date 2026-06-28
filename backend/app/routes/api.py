import os
import uuid
from fastapi import APIRouter, HTTPException, BackgroundTasks, Header
from pydantic import BaseModel

from app.services.analysis_service import jobs, run_analysis_pipeline

router = APIRouter()

class AnalyzeRequest(BaseModel):
    owner: str
    repo: str
    pr_number: int

class PRStatusResponse(BaseModel):
    status: str
    analysis: dict | None = None
    error: str | None = None

class AnalyzeResponse(BaseModel):
    job_id: str
    status: str

@router.get("/health")
def health_check():
    neo4j_uri = os.getenv("NEO4J_URI")
    neo4j_status = "configured" if neo4j_uri else "missing"
    return {
        "status": "ok",
        "service": "GitScribe API",
        "neo4j_config": neo4j_status
    }

@router.post("/api/analyze", response_model=AnalyzeResponse, status_code=202)
async def start_analysis(
    request: AnalyzeRequest, 
    background_tasks: BackgroundTasks,
    authorization: str | None = Header(None)
):
    token = ""
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        
    if not token:
        # We allow it without a token for public repos, though GitHub API rate limits might apply
        pass

    job_id = str(uuid.uuid4())
    
    # Initialize job state
    jobs[job_id] = {"status": "processing"}
    
    # Launch background processing
    background_tasks.add_task(
        run_analysis_pipeline, 
        job_id, 
        request.owner, 
        request.repo, 
        request.pr_number, 
        token
    )
    
    return AnalyzeResponse(job_id=job_id, status="processing")

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

