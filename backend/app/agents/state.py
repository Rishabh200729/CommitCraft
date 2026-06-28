from typing import TypedDict, List, Dict
from pydantic import BaseModel, Field

class CriticFileOutput(BaseModel):
    security_concerns: List[str] = Field(description="List of security vulnerabilities found in the diff for this file.")
    logic_flaws: List[str] = Field(description="List of logic errors or bugs.")
    code_smells: List[str] = Field(description="List of maintainability or readability issues.")
    reliability_risks: List[str] = Field(description="List of risks that could cause crashes or performance drops.")

class ArchitecturalFileOutput(BaseModel):
    impact_summary: str = Field(description="A high-level summary of how the code change in this file impacts the architecture, given its blast radius.")
    risk_assessment: str = Field(description="Assessment of the risk level (e.g. Low, Medium, High) with justification.")
    affected_components: List[str] = Field(description="List of upstream/downstream components that might break due to this change.")

class FileReviewAnnotation(BaseModel):
    risk_level: str = Field(description="Final validated risk level for this file: Low, Medium, High, or Critical.")
    architectural_summary: str = Field(description="Verified architectural summary for this file.")
    critical_findings: List[str] = Field(description="Verified critical issues from the Critic.")
    recommendations: List[str] = Field(description="Actionable recommendations for the developer.")

class OverallVerdict(BaseModel):
    risk_level: str = Field(description="Overall PR risk level.")
    summary: str = Field(description="Overall summary of the PR.")
    impacted_flows: List[str] = Field(default_factory=list, description="List of UserFlows impacted by this PR.")

class PRReviewState(TypedDict, total=False):
    repo_id: str
    repo_url: str
    pr_number: int
    base_branch: str
    pr_diff: str
    changed_files: List[dict]
    blast_radius: dict
    critic_flaws: Dict[str, dict] # keyed by file_path
    architectural_summary: Dict[str, dict] # keyed by file_path
    final_annotations: Dict[str, dict] # keyed by file_path
    overall_verdict: dict
