import os
import sys

# Ensure backend is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.state import PRReviewState
from graph_db.neo4j_client import Neo4jClient
from graph_db.blast_radius import BlastRadiusEngine

def navigator_node(state: PRReviewState) -> dict:
    """
    Deterministically queries Neo4j for the target file's blast radius.
    """
    target_file = state.get("target_file", "")
    if not target_file:
        return {"blast_radius": {"error": "No target file provided"}}
        
    # MOCK DATA FOR UI GRAPH TESTING
    if "Header.tsx" in target_file:
        return {
            "blast_radius": {
                "downstream": [
                    {"file": "frontend/src/app/page.tsx"},
                    {"file": "frontend/src/components/Layout.tsx"}
                ],
                "upstream": [
                    {"file": "frontend/src/components/UserAvatar.tsx"},
                    {"file": "frontend/src/components/ui/Button.tsx"},
                    {"file": "frontend/src/hooks/useAuth.ts"}
                ]
            }
        }
    
    client = Neo4jClient()
    engine = BlastRadiusEngine(client)
    
    try:
        downstream = engine.get_downstream_impact(target_file)
        upstream = engine.get_upstream_dependencies(target_file)
        
        return {
            "blast_radius": {
                "downstream": downstream,
                "upstream": upstream
            }
        }
    except Exception as e:
        return {"blast_radius": {"error": str(e)}}
    finally:
        client.close()
