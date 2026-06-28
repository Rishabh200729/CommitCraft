from .neo4j_client import Neo4jClient

class BlastRadiusEngine:
    def __init__(self, client: Neo4jClient):
        self.client = client

    def get_downstream_impact(self, file_path: str, repo_id: str, max_depth: int = 3):
        """
        Finds all files that depend on (import) the given file.
        In our schema: (DownstreamFile)-[:IMPORTS]->(TargetFile)
        So we traverse backwards from TargetFile along the IMPORTS relationship.
        """
        query = """
        MATCH (target:File {path: $file_path, repo_id: $repo_id})
        MATCH path = (dependent:File {repo_id: $repo_id})-[:IMPORTS*1..%s]->(target)
        OPTIONAL MATCH (flow:UserFlow {repo_id: $repo_id})-[:ENTRY_POINT]->(dependent)
        RETURN dependent.path AS impacted_file, length(path) AS depth, collect(flow.name) AS flows
        ORDER BY depth ASC
        """ % max_depth

        impacted = []
        with self.client.driver.session() as session:
            result = session.run(query, file_path=file_path, repo_id=repo_id)
            for record in result:
                impacted.append({
                    "file": record["impacted_file"],
                    "depth": record["depth"],
                    "flows": record["flows"]
                })
        return impacted

    def get_upstream_dependencies(self, file_path: str, repo_id: str, max_depth: int = 3):
        """
        Finds all files that the given file depends on.
        In our schema: (TargetFile)-[:IMPORTS]->(UpstreamFile)
        """
        query = """
        MATCH (target:File {path: $file_path, repo_id: $repo_id})
        MATCH path = (target)-[:IMPORTS*1..%s]->(upstream:File {repo_id: $repo_id})
        OPTIONAL MATCH (team:Team {repo_id: $repo_id})-[:OWNS]->(upstream)
        RETURN upstream.path AS dependency_file, length(path) AS depth, collect(team.name) AS teams
        ORDER BY depth ASC
        """ % max_depth

        dependencies = []
        with self.client.driver.session() as session:
            result = session.run(query, file_path=file_path, repo_id=repo_id)
            for record in result:
                dependencies.append({
                    "file": record["dependency_file"],
                    "depth": record["depth"],
                    "teams": record["teams"]
                })
        return dependencies

    def get_file_owners(self, file_path: str, repo_id: str) -> list:
        query = """
        MATCH (f:File {path: $file_path, repo_id: $repo_id})
        OPTIONAL MATCH (team:Team {repo_id: $repo_id})-[:OWNS]->(f)
        RETURN collect(team.name) AS teams
        """
        with self.client.driver.session() as session:
            result = session.run(query, file_path=file_path, repo_id=repo_id)
            record = result.single()
            if record:
                return record["teams"]
        return []

    def get_file_flows(self, file_path: str, repo_id: str) -> list:
        query = """
        MATCH (f:File {path: $file_path, repo_id: $repo_id})
        OPTIONAL MATCH (flow:UserFlow {repo_id: $repo_id})-[:ENTRY_POINT]->(f)
        RETURN collect(flow.name) AS flows
        """
        with self.client.driver.session() as session:
            result = session.run(query, file_path=file_path, repo_id=repo_id)
            record = result.single()
            if record:
                return record["flows"]
        return []

