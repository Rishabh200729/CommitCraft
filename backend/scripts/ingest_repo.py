import os
import sys
from pathlib import Path

# Add backend to sys.path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from parser.ts_parser import TypeScriptParser
from graph_db.neo4j_client import Neo4jClient

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
