import os
import sys

# Add backend to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.graph_db.neo4j_client import Neo4jClient
from app.graph_db.blast_radius import BlastRadiusEngine

def main():
    client = Neo4jClient()
    engine = BlastRadiusEngine(client)
    
    # Use a known file like the Badge component
    target_file = os.path.abspath(os.path.join(__file__, "..", "..", "..", "frontend", "src", "components", "ui", "Badge.tsx"))
    
    print(f"Testing Blast Radius for: {target_file}")
    
    print("\n--- Downstream Impact (Files that import Badge) ---")
    downstream = engine.get_downstream_impact(target_file)
    for res in downstream:
        print(f"Depth {res['depth']}: {res['file']}")

    print("\n--- Upstream Dependencies (Files that Badge imports) ---")
    upstream = engine.get_upstream_dependencies(target_file)
    for res in upstream:
        print(f"Depth {res['depth']}: {res['file']}")
        
    client.close()

if __name__ == "__main__":
    main()
