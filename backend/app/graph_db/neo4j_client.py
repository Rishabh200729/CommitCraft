import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env")))

class Neo4jClient:
    def __init__(self):
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        username = os.getenv("NEO4J_USERNAME", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "gitscribe_password")
        
        self.driver = GraphDatabase.driver(uri, auth=(username, password))

    def close(self):
        self.driver.close()

    def merge_file_node(self, file_path: str, extension: str):
        """
        Upserts a File node using MERGE.
        """
        query = """
        MERGE (f:File {path: $path})
        ON CREATE SET f.extension = $extension, f.complexity_score = 0
        ON MATCH SET f.extension = $extension
        RETURN f
        """
        with self.driver.session() as session:
            session.run(query, path=file_path, extension=extension)

    def merge_import_edge(self, source_path: str, target_path: str):
        """
        Upserts an IMPORTS relationship between two File nodes.
        Requires both nodes to exist (or will create them with bare paths).
        """
        query = """
        MERGE (source:File {path: $source_path})
        MERGE (target:File {path: $target_path})
        MERGE (source)-[r:IMPORTS]->(target)
        RETURN r
        """
        with self.driver.session() as session:
            session.run(query, source_path=source_path, target_path=target_path)

    def delete_file_node(self, file_path: str):
        """
        Deletes a File node and all of its relationships.
        """
        query = """
        MATCH (f:File {path: $path})
        DETACH DELETE f
        """
        with self.driver.session() as session:
            session.run(query, path=file_path)

    def delete_import_edge(self, source_path: str, target_path: str):
        """
        Deletes the IMPORTS relationship between two File nodes.
        """
        query = """
        MATCH (source:File {path: $source_path})-[r:IMPORTS]->(target:File {path: $target_path})
        DELETE r
        """
        with self.driver.session() as session:
            session.run(query, source_path=source_path, target_path=target_path)
