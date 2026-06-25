import json
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from .state import PRReviewState, ArchitecturalVerdict

def senior_node(state: PRReviewState) -> dict:
    """
    Combines the localized flaws from the Critic with the deterministic graph from the Navigator.
    Produces an initial architectural impact summary and risk assessment.
    """
    llm = ChatOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ.get("OPENROUTER_API_KEY"),
        model="google/gemma-4-31b-it:free",
        temperature=0,
        extra_body={"reasoning": {"enabled": True}}
    )
    structured_llm = llm.with_structured_output(ArchitecturalVerdict)
    
    prompt = PromptTemplate.from_template("""
    You are a Senior Staff Engineer assessing the architectural impact of a code change.
    You will be provided with the isolated code flaws found by the Critic Agent, and the deterministic blast radius (upstream/downstream dependencies) from the Graph Navigator Agent.
    
    Your job is to formulate an Architectural Verdict.
    1. Summarize how the change and the flaws impact the architecture.
    2. Determine the risk assessment (Low, Medium, High).
    3. List the affected components that might break.
    
    Critic Flaws:
    {flaws}
    
    Blast Radius:
    {blast_radius}
    
    Do not invent dependencies not present in the Blast Radius.
    If information is unavailable, return "unknown". Do not infer or fabricate.
    """)
    
    chain = prompt | structured_llm
    result = chain.invoke({
        "flaws": json.dumps(state.get("critic_flaws", {}), indent=2),
        "blast_radius": json.dumps(state.get("blast_radius", {}), indent=2)
    })
    
    return {
        "architectural_summary": result.impact_summary,
        "risk_assessment": result.risk_assessment
    }
