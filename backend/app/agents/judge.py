import json
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from .state import PRReviewState, FileReviewAnnotation, OverallVerdict

def judge_node(state: PRReviewState) -> dict:
    """
    Acts as the adversarial filter for the pipeline.
    Validates the Senior Engineer's claims against the deterministic Neo4j graph, stripping out any hallucinations.
    Produces per-file validated annotations and an overall PR verdict.
    """
    llm = ChatOpenAI(
        model="openrouter/auto",
        openai_api_key=os.environ.get("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0
    )
    
    file_structured_llm = llm.with_structured_output(FileReviewAnnotation)
    overall_structured_llm = llm.with_structured_output(OverallVerdict)
    
    file_prompt = PromptTemplate.from_template("""
    You are the final Judge and Adversarial Filter for a code review pipeline.
    You will receive the Senior Engineer's architectural summary and risk assessment for a specific file, the original Critic flaws for that file, and the deterministic Blast Radius involving this file.
    
    CRITICAL INSTRUCTION:
    Your primary job is to REMOVE HALLUCINATIONS. 
    Validate every claim made by the Senior Engineer against the Blast Radius. If the Senior Engineer claims a dependency exists that is NOT in the Blast Radius, remove that claim.
    If information is unavailable, return "unknown". Do not infer or fabricate.
    
    Produce the Final File Review Annotation for THIS FILE.
    
    File Path: {file_path}
    
    Senior Engineer Summary: {summary}
    Critic Flaws: {flaws}
    Neo4j Blast Radius: {blast_radius}
    """)
    
    overall_prompt = PromptTemplate.from_template("""
    You are the final Judge summarizing an entire pull request.
    You will receive the validated annotations for all files and the overall blast radius for the PR.
    
    Produce the Overall Verdict for the PR.
    Extract the 'impacted_flows' from the overall Neo4j Blast Radius data if present.
    
    File Annotations: {file_annotations}
    Overall Neo4j Blast Radius: {blast_radius}
    """)
    
    file_chain = file_prompt | file_structured_llm
    overall_chain = overall_prompt | overall_structured_llm
    
    changed_files = state.get("changed_files", [])
    blast_radius = state.get("blast_radius", {})
    critic_flaws = state.get("critic_flaws", {})
    architectural_summary = state.get("architectural_summary", {})
    
    final_annotations = {}
    
    for file_info in changed_files:
        file_path = file_info.get("file", "")
        if not file_path:
            continue
            
        file_summary = architectural_summary.get(file_path, {})
        file_flaws = critic_flaws.get(file_path, {})
        
        file_blast_radius = {
            "downstream": [item for item in blast_radius.get("downstream", []) if item.get("target_file") == file_path],
            "upstream": [item for item in blast_radius.get("upstream", []) if item.get("target_file") == file_path]
        }
        
        try:
            result = file_chain.invoke({
                "file_path": file_path,
                "summary": json.dumps(file_summary, indent=2),
                "flaws": json.dumps(file_flaws, indent=2),
                "blast_radius": json.dumps(file_blast_radius, indent=2)
            })
            final_annotations[file_path] = result.model_dump()
        except Exception as e:
            print(f"Error processing {file_path} in Judge: {e}")
            final_annotations[file_path] = {
                "risk_level": "Unknown",
                "architectural_summary": f"Error during validation: {str(e)}",
                "critical_findings": [],
                "recommendations": []
            }
            
    # Now compute the overall verdict
    try:
        overall_result = overall_chain.invoke({
            "file_annotations": json.dumps(final_annotations, indent=2),
            "blast_radius": json.dumps(blast_radius, indent=2)
        })
        overall_verdict = overall_result.model_dump()
    except Exception as e:
        print(f"Error computing overall verdict in Judge: {e}")
        overall_verdict = {
            "risk_level": "Unknown",
            "summary": f"Error during overall validation: {str(e)}",
            "impacted_flows": []
        }
        
    return {
        "final_annotations": final_annotations,
        "overall_verdict": overall_verdict
    }
