from neo4j import AsyncGraphDatabase
from app.core.config import settings

class Neo4jService:
    """
    Service to handle interactions with the Neo4j graph database.
    """
    def __init__(self, uri, user, password):
        self._driver = AsyncGraphDatabase.driver(uri, auth=(user, password))

    async def close(self):
        """Closes the database connection driver."""
        if self._driver:
            await self._driver.close()

    async def get_full_graph(self):
        """
        Fetches all nodes and relationships using two separate, efficient queries
        and formats them into a structure required by the API.
        """
        async with self._driver.session() as session:
            nodes_result = await session.run(
                "MATCH (n) RETURN elementId(n) AS element_id, labels(n) AS labels, properties(n) AS properties"
            )
            nodes = [record.data() async for record in nodes_result]

            relationships_result = await session.run(
                "MATCH (n)-[r]->(m) RETURN elementId(n) AS source, elementId(m) AS target, type(r) AS type, properties(r) AS properties"
            )
            relationships = [record.data() async for record in relationships_result]
            return {"nodes": nodes, "relationships": relationships}

    async def get_graph_by_story_id(self, story_id: str):
        """
        Fetches all nodes and relationships for a specific story_id.
        """
        async with self._driver.session() as session:
            # Query 1: Fetch nodes filtered by story_id.
            nodes_result = await session.run(
                "MATCH (n {story_id: $story_id}) RETURN elementId(n) AS element_id, labels(n) AS labels, properties(n) AS properties",
                story_id=story_id
            )
            nodes = [record.data() async for record in nodes_result]
            # Query 2: Fetch relationships where both source and target nodes have the matching story_id.
            relationships_result = await session.run(
                "MATCH (n {story_id: $story_id})-[r]->(m {story_id: $story_id}) "
                "RETURN elementId(n) AS source, elementId(m) AS target, type(r) AS type, properties(r) AS properties",
                story_id=story_id
            )
            # Use an async list comprehension here as well.
            relationships = [record.data() async for record in relationships_result]

            return {"nodes": nodes, "relationships": relationships}

    async def delete_data_by_story_id(self, story_id: str):
        """
        Deletes all nodes and their relationships for a specific story_id.
        """
        async with self._driver.session() as session:
            await session.run(
                "MATCH (n {story_id: $story_id}) DETACH DELETE n",
                story_id=story_id
            )

    async def delete_all_data(self):
        """
        Deletes all nodes and relationships from the database.
        """
        async with self._driver.session() as session:
            await session.run("MATCH (n) DETACH DELETE n")


# --- Singleton Instance ---

def get_neo4j_service() -> Neo4jService:
    """Provides a singleton instance of the Neo4jService."""
    return Neo4jService(
        uri=settings.neo4j.NEO4J_URI,
        user=settings.neo4j.NEO4J_USER,
        password=settings.neo4j.NEO4J_PASSWORD
    )

neo4j_service = get_neo4j_service()
