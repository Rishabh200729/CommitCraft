import os
import sys
from pathlib import Path
import json

# Add backend to sys.path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.parser.ts_parser import TypeScriptParser
from app.graph_db.neo4j_client import Neo4jClient

def ingest_directory(directory: str, project_root: str):
    print(f"Starting ingestion for {directory}...")
    
    parser = TypeScriptParser()
    client = Neo4jClient()
    
    try:
        # 1. First pass: Create all file nodes
        print("Pass 1: Creating File nodes...")
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.ts') or file.endswith('.tsx'):
                    file_path = os.path.abspath(os.path.join(root, file))
                    ext = Path(file).suffix
                    client.merge_file_node(file_path, ext)
        
        # 2. Second pass: Extract imports and create edges
        print("Pass 2: Extracting imports and creating edges...")
        edge_count = 0
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.ts') or file.endswith('.tsx'):
                    source_path = os.path.abspath(os.path.join(root, file))
                    
                    raw_imports = parser.extract_imports(source_path)
                    
                    for raw_import in raw_imports:
                        # strip quotes just in case
                        clean_import = raw_import.strip("\"'")
                        target_path = parser.resolve_import_path(source_path, clean_import, project_root)
                        
                        if target_path:
                            client.merge_import_edge(source_path, target_path)
                            edge_count += 1
                            
        print(f"Ingestion complete! Created {edge_count} IMPORTS relationships.")

        # 3. Third pass: Ingest UserFlows and Teams from gitscribe.json
        config_path = os.path.join(project_root, "gitscribe.json")
        if os.path.exists(config_path):
            print("Pass 3: Ingesting gitscribe.json configuration...")
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                
                # Ingest flows
                for flow_name, files in config.get("flows", {}).items():
                    for file_rel_path in files:
                        entry_point = os.path.abspath(os.path.join(project_root, file_rel_path))
                        if os.path.exists(entry_point):
                            client.merge_user_flow(flow_name, entry_point)
                
                # Ingest owners
                for team_name, files in config.get("owners", {}).items():
                    for file_rel_path in files:
                        owned_file = os.path.abspath(os.path.join(project_root, file_rel_path))
                        # In a real app we'd handle glob patterns, here we'll assume direct paths for MVP
                        if os.path.exists(owned_file):
                            client.merge_team_ownership(team_name, owned_file)
                print("Configuration ingestion complete.")
            except Exception as e:
                print(f"Error parsing gitscribe.json: {e}")
        
    finally:
        client.close()

if __name__ == "__main__":
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    project_root = os.path.abspath(os.path.join(backend_dir, ".."))
    frontend_src = os.path.join(project_root, "frontend", "src")
    
    if not os.path.exists(frontend_src):
        print(f"Error: {frontend_src} does not exist.")
        sys.exit(1)
        
    ingest_directory(frontend_src, project_root)
