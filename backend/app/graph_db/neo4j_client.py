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

    def merge_user_flow(self, flow_name: str, entry_point_path: str):
        """
        Upserts a UserFlow node and connects it to a File node via ENTRY_POINT.
        """
        query = """
        MERGE (flow:UserFlow {name: $flow_name})
        MERGE (file:File {path: $entry_point_path})
        MERGE (flow)-[r:ENTRY_POINT]->(file)
        RETURN r
        """
        with self.driver.session() as session:
            session.run(query, flow_name=flow_name, entry_point_path=entry_point_path)

    def merge_team_ownership(self, team_name: str, file_path: str):
        """
        Upserts a Team node and connects it to a File node via OWNS.
        """
        query = """
        MERGE (team:Team {name: $team_name})
        MERGE (file:File {path: $file_path})
        MERGE (team)-[r:OWNS]->(file)
        RETURN r
        """
        with self.driver.session() as session:
            session.run(query, team_name=team_name, file_path=file_path)
