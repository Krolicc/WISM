import uuid

from neo4j import AsyncGraphDatabase
from typing import Dict, Any

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

    async def export_story_as_dict(self, story_id: uuid.UUID) -> Dict[str, Any]:
        """
        Экспортирует всю иерархию истории в виде вложенного словаря,
        используя один запрос к Neo4j.
        
        Предполагается, что на узлах в Neo4j есть свойство 'title'.
        """

        # Этот запрос использует библиотеку APOC для эффективного получения
        # всего подграфа истории, включая все узлы и их связи.
        query = """
            MATCH (story {id: $story_id})
            CALL apoc.path.subgraphAll(story, {
                relationshipFilter: "CONTAINS|NEXT"
            })
            YIELD nodes
            
            UNWIND nodes as n
            
            OPTIONAL MATCH (p)-[:CONTAINS]->(n)
            OPTIONAL MATCH (prev)-[:NEXT]->(n)
            
            RETURN
                n.id AS id,
                labels(n)[0] AS type,
                n.title AS title,
                p.id AS parent_id,
                prev.id AS prev_id
        """
        params = {"story_id": str(story_id)}
        results = await self.read_query(query, params)

        if not results:
            return {}

        print(f"Results: {results}")

        # 1. Создаем карту узлов для быстрого доступа и инициализируем 'children'
        nodes_map = {
            res["id"]: {
                "id": res["id"],
                "type": res["type"],
                "title": res["title"],
                "children": []
            } for res in results
        }
        
        # Вспомогательная карта для связи 'id' с 'prev_id'
        id_to_prev_id_map = {res["id"]: res["prev_id"] for res in results}
        
        # 2. Группируем детей по их родителям
        for res in results:
            if res["parent_id"] and res["parent_id"] in nodes_map:
                child_node = nodes_map[res["id"]]
                nodes_map[res["parent_id"]]["children"].append(child_node)
        # 3. Сортируем 'children' в каждом узле, используя восстановленную цепочку
        for node_data in nodes_map.values():
            if len(node_data["children"]) > 1:
                
                # Находим "голову" связанного списка - элемент, у которого нет 'prev_id'
                # среди своих братьев.
                children_ids = {c["id"] for c in node_data["children"]}
                
                head_node = next((
                    child for child in node_data["children"]
                    if id_to_prev_id_map.get(child["id"]) not in children_ids
                ), None)
                if not head_node:
                    # Если не нашли голову (например, цикл), оставляем как есть, чтобы избежать падения
                    continue
                
                # Создаем карту 'id' -> 'узел' для быстрой сборки цепочки
                id_to_child_map = {c["id"]: c for c in node_data["children"]}
                
                # Создаем обратную карту 'prev_id' -> 'id' для быстрого поиска следующего
                prev_id_to_id_map = {
                    id_to_prev_id_map.get(child_id): child_id
                    for child_id in children_ids if id_to_prev_id_map.get(child_id)
                }
                # Собираем отсортированный список, идя по цепочке от головы
                sorted_children = []
                current_node = head_node
                while current_node:
                    sorted_children.append(current_node)
                    next_id = prev_id_to_id_map.get(current_node["id"])
                    current_node = id_to_child_map.get(next_id) if next_id else None
                
                node_data["children"] = sorted_children
        # 4. Возвращаем корневой узел, который теперь содержит всю вложенную структуру
        return nodes_map.get(str(story_id), {})

    async def delete_all_data(self):
        """
        Deletes all nodes and relationships from the database.
        """
        async with self._driver.session() as session:
            await session.run("MATCH (n) DETACH DELETE n")

    async def read_query(self, query, parameters=None, single=False):
        """
        Выполняет запрос на чтение в Neo4j с поддержкой получения одного результата.
        """
        async def work(tx, query, parameters):
            result = await tx.run(query, parameters)
            return [record.data() async for record in result]

        async with self._driver.session() as session:
            records = await session.execute_read(work, query, parameters or {})
            if single:
                return records[0] if records else None
            return records

    async def write_query(self, query, parameters=None):
        """
        Выполняет запрос на запись в Neo4j.
        """
        async def work(tx, query, parameters):
            await tx.run(query, parameters)
            
        async with self._driver.session() as session:
            await session.execute_write(work, query, parameters or {})

    async def execute_query(self, query: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Выполняет запрос к Neo4j, используя сессию из драйвера,
        и возвращает результат в виде списка словарей.
        """
        if params is None:
            params = {}
            
        async with self._driver.session() as session:
            result = await session.run(query, **params)

            records = [record.data() for record in await result.list()]
            return records

# --- Singleton Instance ---

def get_neo4j_service() -> Neo4jService:
    """Provides a singleton instance of the Neo4jService."""
    return Neo4jService(
        uri=settings.neo4j.NEO4J_URI,
        user=settings.neo4j.NEO4J_USER,
        password=settings.neo4j.NEO4J_PASSWORD
    )

neo4j_service = get_neo4j_service()
