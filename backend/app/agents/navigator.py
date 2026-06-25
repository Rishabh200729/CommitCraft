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
    target_file = state.get("target_file", "")
    pr_diff = state.get("pr_diff", "")
    changed_files = state.get("changed_files", [])
    
    if not changed_files and pr_diff:
        changed_files = DiffParser.parse_diff(pr_diff)
        
    if not changed_files and target_file:
        changed_files = [{"file": target_file, "status": "modified"}]
        
    if not changed_files:
        return {"blast_radius": {"error": "No files changed or target file provided"}}
    
    current_file_path = os.path.abspath(__file__)
    project_root = os.path.abspath(os.path.join(os.path.dirname(current_file_path), "..", "..", ".."))
    
    client = Neo4jClient()
    engine = BlastRadiusEngine(client)
    
    combined_downstream = []
    combined_upstream = []
    seen_downstream_edges = set()
    seen_upstream_edges = set()
    
    try:
        for file_info in changed_files:
            f_path = file_info["file"]
            
            # Resolve to absolute path for Neo4j querying
            abs_f_path = os.path.abspath(os.path.join(project_root, f_path))
            
            downstream = engine.get_downstream_impact(abs_f_path)
            upstream = engine.get_upstream_dependencies(abs_f_path)
            
            for item in downstream:
                rel_file = os.path.relpath(item["file"], project_root).replace('\\', '/')
                edge_id = f"{rel_file}->{f_path}"
                if edge_id not in seen_downstream_edges:
                    combined_downstream.append({"file": rel_file, "target_file": f_path})
                    seen_downstream_edges.add(edge_id)
                    
            for item in upstream:
                rel_file = os.path.relpath(item["file"], project_root).replace('\\', '/')
                edge_id = f"{f_path}->{rel_file}"
                if edge_id not in seen_upstream_edges:
                    combined_upstream.append({"file": rel_file, "target_file": f_path})
                    seen_upstream_edges.add(edge_id)
        
        return {
            "changed_files": changed_files,
            "blast_radius": {
                "downstream": combined_downstream,
                "upstream": combined_upstream
            }
        }
    except Exception as e:
        return {"blast_radius": {"error": str(e)}}
    finally:
        client.close()
