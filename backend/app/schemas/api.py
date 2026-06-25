from pydantic import BaseModel, Field
from typing import Literal, Dict, Any, Optional

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
