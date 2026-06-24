import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from .state import PRReviewState, FinalVerdict

def judge_node(state: PRReviewState) -> dict:
    """
    Acts as the adversarial filter for the pipeline.
    Validates the Senior Engineer's claims against the deterministic Neo4j graph, stripping out any hallucinations.
    """
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    structured_llm = llm.with_structured_output(FinalVerdict)
    
    prompt = PromptTemplate.from_template("""
    You are the final Judge and Adversarial Filter for a code review pipeline.
    You will receive the Senior Engineer's architectural summary and risk assessment, the original Critic flaws, and the deterministic Blast Radius from Neo4j.
    
    CRITICAL INSTRUCTION:
    Your primary job is to REMOVE HALLUCINATIONS. 
    Validate every claim made by the Senior Engineer against the Blast Radius. If the Senior Engineer claims a dependency exists that is NOT in the Blast Radius, remove that claim.
    If information is unavailable, return "unknown". Do not infer or fabricate.
    
    Produce the Final Verdict.
    
    Senior Engineer Summary: {summary}
    Senior Engineer Risk Assessment: {risk}
    Critic Flaws: {flaws}
    Neo4j Blast Radius: {blast_radius}
    """)
    
    chain = prompt | structured_llm
    result = chain.invoke({
        "summary": state.get("architectural_summary", ""),
        "risk": state.get("risk_assessment", ""),
        "flaws": json.dumps(state.get("critic_flaws", {}), indent=2),
        "blast_radius": json.dumps(state.get("blast_radius", {}), indent=2)
    })
    
    return {"final_verdict": result.dict()}
