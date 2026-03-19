from neo4j import AsyncGraphDatabase
from app.core.config import settings
from app.schemas import KnowledgeGraph, Node, Relationship

class Neo4jService:
    """
    Service to handle all interactions with the Neo4j graph database.
    """
    def __init__(self, uri, user, password):
        self._driver = AsyncGraphDatabase.driver(uri, auth=(user, password))

    async def close(self):
        """Closes the database connection driver."""
        await self._driver.close()

    async def merge_graph(self, graph: KnowledgeGraph, story_id: str):
        """
        Merges a KnowledgeGraph into Neo4j, ensuring all nodes and relationships
        are scoped to a specific story_id.
        """
        async def _merge_graph_tx(tx):
            # This inner function defines the transactional unit of work.
            for node in graph.nodes:
                await self._merge_node(tx, node, story_id)
            for rel in graph.relationships:
                await self._merge_relationship(tx, rel, story_id)


        async with self._driver.session() as session:
            await session.execute_write(_merge_graph_tx)


    async def _merge_node(self, tx, node: Node, story_id: str):
        """
        Merges a single node, uniquely identifying it by its name AND story_id.
        It also sets/updates the description property based on the new schema.
        """
        cypher = f"""
        MERGE (n:{node.label} {{name: $name, story_id: $story_id}})
        SET n.description = $description
        """
        await tx.run(
            cypher, 
            name=node.properties.name, 
            story_id=story_id, 
            description=node.properties.description
        )

    async def _merge_relationship(self, tx, rel: Relationship, story_id: str):
        """
        Merges a relationship, ensuring it connects nodes within the same story.
        It also sets/updates the relationship's description property.
        """
        cypher = f"""
        MATCH (a:{rel.source_node_label} {{name: $source_name, story_id: $story_id}})
        MATCH (b:{rel.target_node_label} {{name: $target_name, story_id: $story_id}})
        MERGE (a)-[r:{rel.type}]->(b)
        SET r.description = $description
        """
        await tx.run(
            cypher, 
            source_name=rel.source_node_name, 
            target_name=rel.target_node_name,
            story_id=story_id,
            description=rel.properties.description
        )

# --- Singleton Instance ---

def get_neo4j_service() -> Neo4jService:
    """Provides a singleton instance of the Neo4jService."""
    return Neo4jService(
        uri=settings.neo4j.NEO4J_URI,
        user=settings.neo4j.NEO4J_USER,
        password=settings.neo4j.NEO4J_PASSWORD
    )

neo4j_service = get_neo4j_service()
