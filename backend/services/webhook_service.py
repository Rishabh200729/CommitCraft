import uuid
import json
from agents.workflow import create_workflow

# In-memory storage for V1 MVP
jobs = {}

def format_react_flow(target_file: str, blast_radius: dict) -> dict:
    """
    Converts raw Neo4j blast radius data into React Flow nodes and edges.
    """
    nodes = []
    edges = []
    added_nodes = set()
    
    # Clean up Windows absolute paths to shorter relative-looking paths if possible, or just use basename for label
    def get_label(path: str) -> str:
        return path.split('\\')[-1].split('/')[-1]

    # Add Target Node
    nodes.append({
        "id": target_file,
        "type": "modified",
        "data": {"label": get_label(target_file)},
        "position": {"x": 0, "y": 0} # Let frontend layout engine handle actual positions
    })
    added_nodes.add(target_file)
    
    # Process Downstream (Files that import the target)
    downstream = blast_radius.get("downstream", [])
    for item in downstream:
        file_path = item.get("file")
        if file_path not in added_nodes:
            nodes.append({
                "id": file_path,
                "type": "impacted",
                "data": {"label": get_label(file_path)},
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
        if file_path not in added_nodes:
            nodes.append({
                "id": file_path,
                "type": "dependency",
                "data": {"label": get_label(file_path)},
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
    app = create_workflow()
    
    initial_state = {
        "target_file": target_file,
        "pr_diff": diff
    }
    
    try:
        result = await app.ainvoke(initial_state)
        
        blast_radius_raw = result.get("blast_radius", {})
        graph_data = format_react_flow(target_file, blast_radius_raw)
        
        jobs[job_id] = {
            "status": "completed",
            "analysis": {
                "graph": graph_data,
                "verdict": result.get("final_verdict", {})
            }
        }
    except (ValueError, RuntimeError, KeyError) as e:
        jobs[job_id] = {
            "status": "failed",
            "error": f"Pipeline Error: {str(e)}"
        }
