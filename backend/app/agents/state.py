from typing import TypedDict, List
from pydantic import BaseModel, Field

class CriticOutput(BaseModel):
    security_concerns: List[str] = Field(description="List of security vulnerabilities found in the diff.")
    logic_flaws: List[str] = Field(description="List of logic errors or bugs.")
    code_smells: List[str] = Field(description="List of maintainability or readability issues.")
    reliability_risks: List[str] = Field(description="List of risks that could cause crashes or performance drops.")

class ArchitecturalVerdict(BaseModel):
    impact_summary: str = Field(description="A high-level summary of how the code change impacts the architecture, given the blast radius.")
    risk_assessment: str = Field(description="Assessment of the risk level (e.g. Low, Medium, High) with justification.")
    affected_components: List[str] = Field(description="List of upstream/downstream components that might break due to this change.")

class FinalVerdict(BaseModel):
    risk_level: str = Field(description="Final validated risk level: Low, Medium, High, or Critical.")
    architectural_summary: str = Field(description="Verified architectural summary, stripped of any hallucinations.")
    critical_findings: List[str] = Field(description="Verified critical issues from the Critic.")
    recommendations: List[str] = Field(description="Actionable recommendations for the developer.")

class PRReviewState(TypedDict, total=False):
    target_file: str # Legacy, to be removed or kept for single-file tests
    changed_files: List[dict] # Added for Feature 01: Architecture Diff Engine
    pr_diff: str
    blast_radius: dict
    critic_flaws: dict
    architectural_summary: str
    risk_assessment: str
    final_verdict: dict
