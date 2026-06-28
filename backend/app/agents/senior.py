import json
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from .state import PRReviewState, ArchitecturalFileOutput

def senior_node(state: PRReviewState) -> dict:
    """
    Combines the localized flaws from the Critic with the deterministic graph from the Navigator, per file.
    Produces an architectural impact summary and risk assessment for each file.
    """
    llm = ChatOpenAI(
        model="openrouter/auto", 
        openai_api_key=os.environ.get("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0
    )
    structured_llm = llm.with_structured_output(ArchitecturalFileOutput)
    
    prompt = PromptTemplate.from_template("""
    You are a Senior Staff Engineer assessing the architectural impact of a code change in a specific file.
    You will be provided with the isolated code flaws found by the Critic Agent for this file, and the deterministic blast radius (upstream/downstream dependencies) from the Graph Navigator Agent for this file.
    
    Your job is to formulate an Architectural Verdict for THIS FILE.
    1. Summarize how the change and the flaws impact the architecture.
    2. Determine the risk assessment (Low, Medium, High).
    3. List the affected components that might break.
    
    File Path: {file_path}
    
    Critic Flaws for this file:
    {flaws}
    
    Blast Radius involving this file:
    {blast_radius}
    
    Do not invent dependencies not present in the Blast Radius.
    If information is unavailable, return "unknown". Do not infer or fabricate.
    """)
    
    chain = prompt | structured_llm
    
    changed_files = state.get("changed_files", [])
    blast_radius = state.get("blast_radius", {})
    critic_flaws = state.get("critic_flaws", {})
    
    architectural_summary = {}
    
    for file_info in changed_files:
        file_path = file_info.get("file", "")
        if not file_path:
            continue
            
        file_flaws = critic_flaws.get(file_path, {})
        
        # Extract blast radius specifically relevant to this file
        file_blast_radius = {
            "downstream": [item for item in blast_radius.get("downstream", []) if item.get("target_file") == file_path],
            "upstream": [item for item in blast_radius.get("upstream", []) if item.get("target_file") == file_path]
        }
        
        try:
            result = chain.invoke({
                "file_path": file_path,
                "flaws": json.dumps(file_flaws, indent=2),
                "blast_radius": json.dumps(file_blast_radius, indent=2)
            })
            architectural_summary[file_path] = result.model_dump()
        except Exception as e:
            print(f"Error processing {file_path} in Senior: {e}")
            architectural_summary[file_path] = {
                "impact_summary": f"Error during analysis: {str(e)}",
                "risk_assessment": "Unknown",
                "affected_components": []
            }
            
    return {"architectural_summary": architectural_summary}

