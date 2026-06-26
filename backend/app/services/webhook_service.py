import uuid
import json
from app.agents.workflow import create_workflow

# In-memory storage for V1 MVP
jobs = {}

def format_react_flow(changed_files: list, blast_radius: dict) -> dict:
    """
    Converts raw Neo4j blast radius data into React Flow nodes and edges.
    """
    nodes = []
    edges = []
    added_nodes = set()
    
    # Clean up Windows absolute paths to shorter relative-looking paths if possible
    def get_label(path: str) -> str:
        return path.split('\\')[-1].split('/')[-1]

    # Add Target Nodes
    for cf in changed_files:
        f_path = cf["file"]
        status = cf["status"] # 'added', 'modified', 'removed'
        
        if f_path not in added_nodes:
            nodes.append({
                "id": f_path,
                "type": status,
                "data": {
                    "label": get_label(f_path),
                    "owners": cf.get("owners", []),
                    "flows": cf.get("flows", [])
                },
                "position": {"x": 0, "y": 0} # Frontend layout handles actual positions
            })
            added_nodes.add(f_path)
            
    # Process Downstream (Files that import the target)
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
            
        # Target <- Downstream
        edges.append({
            "id": f"e-{file_path}-{target_file}",
            "source": file_path,
            "target": target_file,
            "type": "imports"
        })

    # Process Upstream (Files the target imports)
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
            
        # Upstream <- Target
        edges.append({
            "id": f"e-{target_file}-{file_path}",
            "source": target_file,
            "target": file_path,
            "type": "imports"
        })

    return {"nodes": nodes, "edges": edges}

async def process_pr_webhook(job_id: str, target_file: str, diff: str) -> None:
    """
    Background task that executes the LangGraph pipeline and stores the result.
    """
    # 1. Parse diff and update Neo4j first
    from app.parser.diff_parser import DiffParser
    from app.parser.ts_parser import TypeScriptParser
    from app.graph_db.neo4j_client import Neo4jClient
    import os
    from pathlib import Path
    
    current_file_path = os.path.abspath(__file__)
    project_root = os.path.abspath(os.path.join(os.path.dirname(current_file_path), "..", "..", ".."))
    
    changed_files = DiffParser.parse_diff(diff) if diff else []
    
    if changed_files:
        client = Neo4jClient()
        parser = TypeScriptParser()
        try:
            for file_info in changed_files:
                f_path = file_info["file"]
                status = file_info["status"]
                block = file_info.get("block", "")
                
                abs_file_path = os.path.abspath(os.path.join(project_root, f_path))
                
                if status == "added":
                    ext = Path(abs_file_path).suffix
                    client.merge_file_node(abs_file_path, ext)
                    
                    content = DiffParser.reconstruct_file_from_added_diff(block)
                    raw_imports = parser.extract_imports_from_content(content)
                    
                    for raw_import in raw_imports:
                        clean_import = raw_import.strip("\"'")
                        target_path = parser.resolve_import_path(abs_file_path, clean_import, project_root)
                        if target_path:
                            client.merge_import_edge(abs_file_path, target_path)
                            
                elif status == "modified":
                    changes = DiffParser.extract_import_changes_from_modified_diff(block)
                    
                    # Process added imports
                    for raw_import in changes.get("added", []):
                        clean_import = raw_import.strip("\"'")
                        target_path = parser.resolve_import_path(abs_file_path, clean_import, project_root)
                        if target_path:
                            client.merge_import_edge(abs_file_path, target_path)
                            
                    # Process removed imports
                    for raw_import in changes.get("removed", []):
                        clean_import = raw_import.strip("\"'")
                        target_path = parser.resolve_import_path(abs_file_path, clean_import, project_root)
                        if target_path:
                            client.delete_import_edge(abs_file_path, target_path)
                            
                elif status == "removed":
                    client.delete_file_node(abs_file_path)
                    
        except Exception as e:
            print(f"Error applying diff to Neo4j in webhook: {e}")
        finally:
            client.close()
            
    app = create_workflow()
    
    initial_state = {
        "target_file": target_file,
        "pr_diff": diff,
        "changed_files": changed_files
    }
    
    try:
        result = await app.ainvoke(initial_state)
        
        blast_radius_raw = result.get("blast_radius", {})
        result_changed_files = result.get("changed_files", changed_files)
        if not result_changed_files:
            result_changed_files = [{"file": target_file, "status": "modified"}]
            
        graph_data = format_react_flow(result_changed_files, blast_radius_raw)
        
        jobs[job_id] = {
            "status": "completed",
            "analysis": {
                "graph": graph_data,
                "verdict": result.get("final_verdict", {})
            }
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        jobs[job_id] = {
            "status": "failed",
            "error": f"Pipeline Error: {str(e)}"
        }
