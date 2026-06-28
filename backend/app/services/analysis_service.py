import uuid
import os
import traceback
from typing import Dict, Any

from app.services.github_service import GithubService
from app.parser.diff_parser import DiffParser
from app.parser.ts_parser import TypeScriptParser
from app.graph_db.neo4j_client import Neo4jClient
from app.agents.workflow import create_workflow

# In-memory job storage for MVP
jobs: Dict[str, Any] = {}

def format_react_flow(changed_files: list, blast_radius: dict) -> dict:
    """
    Converts raw Neo4j blast radius data into React Flow nodes and edges.
    """
    nodes = []
    edges = []
    added_nodes = set()
    
    def get_label(path: str) -> str:
        return path.split('/')[-1]

    for cf in changed_files:
        f_path = cf["file"]
        status = cf["status"] 
        
        if f_path not in added_nodes:
            nodes.append({
                "id": f_path,
                "type": status,
                "data": {
                    "label": get_label(f_path),
                    "owners": cf.get("owners", []),
                    "flows": cf.get("flows", [])
                },
                "position": {"x": 0, "y": 0} 
            })
            added_nodes.add(f_path)
            
    downstream = blast_radius.get("downstream", [])
    for item in downstream:
        file_path = item.get("file")
        target_file = item.get("target_file")
        
        flows = item.get("flows", [])
        
        if not file_path or not target_file:
            continue
            
        if file_path not in added_nodes:
            nodes.append({
                "id": file_path,
                "type": "impacted",
                "data": {
                    "label": get_label(file_path),
                    "flows": flows
                },
                "position": {"x": 0, "y": 0}
            })
            added_nodes.add(file_path)
            
        edges.append({
            "id": f"e-{file_path}-{target_file}",
            "source": file_path,
            "target": target_file,
            "type": "imports"
        })

    upstream = blast_radius.get("upstream", [])
    for item in upstream:
        file_path = item.get("file")
        target_file = item.get("target_file")
        
        teams = item.get("teams", [])
        
        if not file_path or not target_file:
            continue
            
        if file_path not in added_nodes:
            nodes.append({
                "id": file_path,
                "type": "dependency",
                "data": {
                    "label": get_label(file_path),
                    "owners": teams
                },
                "position": {"x": 0, "y": 0}
            })
            added_nodes.add(file_path)
            
        edges.append({
            "id": f"e-{target_file}-{file_path}",
            "source": target_file,
            "target": file_path,
            "type": "imports"
        })

    return {"nodes": nodes, "edges": edges}

async def run_analysis_pipeline(job_id: str, owner: str, repo: str, pr_number: int, token: str):
    """
    Orchestrates the full analysis pipeline: clone, parse, graph build, fetch diff, LangGraph agents.
    """
    repo_id = f"{owner}/{repo}"
    temp_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", f"temp_{job_id}"))
    
    try:
        # 1. Fetch metadata & Clone Repo
        metadata = await GithubService.fetch_pr_metadata(owner, repo, pr_number, token)
        base_branch = metadata["base_branch"]
        clone_url = metadata["clone_url"]
        
        GithubService.clone_repo(clone_url, base_branch, token, temp_dir)
        
        # 2. Parse Codebase & Build Neo4j Graph
        parser = TypeScriptParser()
        parsed_data = parser.parse_directory(temp_dir, repo_id)
        
        client = Neo4jClient()
        try:
            # Clear existing graph for this repo to avoid stale data
            client.clear_repo_graph(repo_id)
            
            for file_data in parsed_data:
                f_path = file_data["file_path"]
                ext = file_data["extension"]
                client.merge_file_node(f_path, ext, repo_id)
                
                for imp_path in file_data["imports"]:
                    client.merge_import_edge(f_path, imp_path, repo_id)
        except Exception as e:
            print(f"Neo4j build error: {e}")
        finally:
            client.close()
            
        # 3. Fetch PR Diff
        pr_diff = await GithubService.fetch_pr_diff(owner, repo, pr_number, token)
        changed_files = DiffParser.parse_diff(pr_diff) if pr_diff else []
        
        # 4. Run LangGraph Pipeline
        app = create_workflow()
        
        initial_state = {
            "repo_id": repo_id,
            "repo_url": clone_url,
            "pr_number": pr_number,
            "base_branch": base_branch,
            "pr_diff": pr_diff,
            "changed_files": changed_files
        }
        
        result = await app.ainvoke(initial_state)
        
        # 5. Format results
        blast_radius_raw = result.get("blast_radius", {})
        result_changed_files = result.get("changed_files", changed_files)
        
        graph_data = format_react_flow(result_changed_files, blast_radius_raw)
        
        jobs[job_id] = {
            "status": "completed",
            "analysis": {
                "graph": graph_data,
                "final_annotations": result.get("final_annotations", {}),
                "overall_verdict": result.get("overall_verdict", {})
            }
        }
        
    except Exception as e:
        traceback.print_exc()
        jobs[job_id] = {
            "status": "failed",
            "error": f"Analysis Pipeline Error: {str(e)}"
        }
    finally:
        # Cleanup cloned repo
        GithubService.cleanup_clone(temp_dir)
