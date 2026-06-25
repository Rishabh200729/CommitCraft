from .neo4j_client import Neo4jClient

class BlastRadiusEngine:
    def __init__(self, client: Neo4jClient):
        self.client = client

    def get_downstream_impact(self, file_path: str, max_depth: int = 3):
        """
        Finds all files that depend on (import) the given file.
        In our schema: (DownstreamFile)-[:IMPORTS]->(TargetFile)
        So we traverse backwards from TargetFile along the IMPORTS relationship.
        """
        query = """
        MATCH (target:File {path: $file_path})
        MATCH path = (dependent:File)-[:IMPORTS*1..%s]->(target)
        RETURN dependent.path AS impacted_file, length(path) AS depth
        ORDER BY depth ASC
        """ % max_depth

        impacted = []
        with self.client.driver.session() as session:
            result = session.run(query, file_path=file_path)
            for record in result:
                impacted.append({
                    "file": record["impacted_file"],
                    "depth": record["depth"]
                })
        return impacted

    def get_upstream_dependencies(self, file_path: str, max_depth: int = 3):
        """
        Finds all files that the given file depends on.
        In our schema: (TargetFile)-[:IMPORTS]->(UpstreamFile)
        """
        query = """
        MATCH (target:File {path: $file_path})
        MATCH path = (target)-[:IMPORTS*1..%s]->(upstream:File)
        RETURN upstream.path AS dependency_file, length(path) AS depth
        ORDER BY depth ASC
        """ % max_depth

        dependencies = []
        with self.client.driver.session() as session:
            result = session.run(query, file_path=file_path)
            for record in result:
                dependencies.append({
                    "file": record["dependency_file"],
                    "depth": record["depth"]
                })
        return dependencies
