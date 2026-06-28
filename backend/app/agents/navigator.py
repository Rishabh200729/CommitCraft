import os
import sys

# Ensure backend is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.agents.state import PRReviewState
from app.graph_db.neo4j_client import Neo4jClient
from app.graph_db.blast_radius import BlastRadiusEngine
from app.parser.diff_parser import DiffParser

def navigator_node(state: PRReviewState) -> dict:
    """
    Deterministically queries Neo4j for the target file's blast radius.
    """
    repo_id = state.get("repo_id", "")
    pr_diff = state.get("pr_diff", "")
    changed_files = state.get("changed_files", [])
    
    if not changed_files and pr_diff:
        changed_files = DiffParser.parse_diff(pr_diff)
        
    if not changed_files:
        return {"blast_radius": {"error": "No files changed"}}
    
    if not repo_id:
        return {"blast_radius": {"error": "repo_id is required"}}
    
    client = Neo4jClient()
    engine = BlastRadiusEngine(client)
    
    combined_downstream = []
    combined_upstream = []
    seen_downstream_edges = set()
    seen_upstream_edges = set()
    
    try:
        for file_info in changed_files:
            # f_path is relative to the repo root
            f_path = file_info["file"].replace('\\', '/')
            file_info["file"] = f_path
            
            # Fetch target file's own teams and flows using repo_id
            file_info["owners"] = engine.get_file_owners(f_path, repo_id)
            file_info["flows"] = engine.get_file_flows(f_path, repo_id)
            
            downstream = engine.get_downstream_impact(f_path, repo_id)
            upstream = engine.get_upstream_dependencies(f_path, repo_id)
            
            for item in downstream:
                rel_file = item["file"].replace('\\', '/')
                edge_id = f"{rel_file}->{f_path}"
                if edge_id not in seen_downstream_edges:
                    combined_downstream.append({
                        "file": rel_file, 
                        "target_file": f_path,
                        "flows": item.get("flows", [])
                    })
                    seen_downstream_edges.add(edge_id)
                    
            for item in upstream:
                rel_file = item["file"].replace('\\', '/')
                edge_id = f"{f_path}->{rel_file}"
                if edge_id not in seen_upstream_edges:
                    combined_upstream.append({
                        "file": rel_file, 
                        "target_file": f_path,
                        "teams": item.get("teams", [])
                    })
                    seen_upstream_edges.add(edge_id)
        
        # Collect target file owners and flows
        target_owners = []
        target_flows = []
        for file_info in changed_files:
            target_owners.extend(file_info.get("owners", []))
            target_flows.extend(file_info.get("flows", []))

        return {
            "changed_files": changed_files,
            "blast_radius": {
                "downstream": combined_downstream,
                "upstream": combined_upstream,
                "target_owners": list(set(target_owners)),
                "target_flows": list(set(target_flows))
            }
        }
    except Exception as e:
        return {"blast_radius": {"error": str(e)}}
    finally:
        client.close()

