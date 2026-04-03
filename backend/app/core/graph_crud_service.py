
import uuid
from typing import Union, Dict, Any

from app.core.neo4j_service import neo4j_service
from app.schemas.graph.base import StoryNode, ArcNode, ChapterNode, SceneNode, FrameNode, EntityNode

# Типизация для всех возможных моделей узлов, которые мы можем создавать
AnyNode = Union[StoryNode, ArcNode, ChapterNode, SceneNode, FrameNode, EntityNode]

class GraphCrudService:
    """
    Сервис для высокоуровневых CRUD-операций в графе Neo4j.
    Инкапсулирует логику создания и связывания узлов.
    """

    async def get_story_id(self, item_id: uuid.UUID) -> Optional[uuid.UUID]:
        """
        Получает story_id для любого элемента, запрашивая его узел в Neo4j.
        """
        if not item_id:
            return None
            
        query = "MATCH (n {id: $item_id}) RETURN n.story_id AS story_id"
        params = {"item_id": str(item_id)}
        result = await neo4j_service.read_query(query, params, single=True)
        
        if result and result.get("story_id"):
            return uuid.UUID(result["story_id"])
            
        return None

    async def get_parent_id(self, item_id: uuid.UUID) -> Optional[uuid.UUID]:
        """
        Находит родителя элемента по связи :CONTAINS в Neo4j.
        """
        if not item_id:
            return None
            
        query = """
            MATCH (parent)-[:CONTAINS]->(child {id: $item_id})
            RETURN parent.id AS parent_id
            LIMIT 1
        """
        params = {"item_id": str(item_id)}
        result = await neo4j_service.read_query(query, params, single=True)
        
        if result and result.get("parent_id"):
            return uuid.UUID(result["parent_id"])
            
        return None

    async def recursive_break_next_links(self, left_id: uuid.UUID, right_id: uuid.UUID):
        """
        Рекурсивно разрывает :NEXT связи на всех уровнях иерархии вниз.
        """
        if not left_id or not right_id:
            return

        # 1. Разрываем связь на ТЕКУЩЕМ уровне.
        break_query = "MATCH (left {id: $left_id})-[r:NEXT]->(right {id: $right_id}) DELETE r"
        await self.neo4j_service.execute_query(break_query, {
            'left_id': str(left_id),
            'right_id': str(right_id)
        })

        # 2. Ищем детей для следующего уровня рекурсии.
        # Находим последнего ребенка левого узла.
        find_last_q = """
        MATCH (p {id: $parent_id})-[:CONTAINS]->(child) 
        WHERE NOT (child)-[:NEXT]->() 
        RETURN child.id as id LIMIT 1
        """
        last_child_res = await self.neo4j_service.execute_query(find_last_q, {'parent_id': str(left_id)})
        new_left_id = last_child_res[0].get('id') if last_child_res else None

        # Находим первого ребенка правого узла.
        find_first_q = """
        MATCH (p {id: $parent_id})-[:CONTAINS]->(child) 
        WHERE NOT ()-[:NEXT]->(child) 
        RETURN child.id as id LIMIT 1
        """
        first_child_res = await self.neo4j_service.execute_query(find_first_q, {'parent_id': str(right_id)})
        new_right_id = first_child_res[0].get('id') if first_child_res else None

        # 3. Если нашли пару детей, проверяем, связаны ли они, и уходим в рекурсию.
        if new_left_id and new_right_id:
            check_link_q = "RETURN EXISTS(MATCH ({id: $id1})-[:NEXT]->({id: $id2})) as link_exists"
            link_exists_res = await self.neo4j_service.execute_query(check_link_q, {'id1': new_left_id, 'id2': new_right_id})

            if link_exists_res and link_exists_res[0]['link_exists']:
                await self._recursive_break_next_links(uuid.UUID(new_left_id), uuid.UUID(new_right_id))


    async def find_narrative_anchor_id(self, parent_id: uuid.UUID) -> Optional[uuid.UUID]:
        anchor_id = await self.find_last_child_of_prev_sibling(db, parent_id=parent_id)

        if not anchor_id:
            anchor_id = await self.find_first_child_of_next_sibling(db, parent_id=parent_id)

        return anchor_id

    async def find_last_child_of_prev_sibling(self, parent_id: uuid.UUID) -> Optional[uuid.UUID]:
        """
        Находит ID ПОСЛЕДНЕГО РЕБЕНКА у ПРЕДЫДУЩЕГО БРАТА текущего родителя.
        Это "точка входа" для сшивания.
        """
        query = f"""
        MATCH (current_parent {{id: $parent_id}})
        OPTIONAL MATCH (prev_sibling)-[:NEXT]->(current_parent)
        WITH prev_sibling
        WHERE prev_sibling IS NOT NULL
        MATCH (prev_sibling)-[:CONTAINS]->(child)
        WHERE NOT (child)-[:NEXT]->()
        RETURN child.id as last_child_id
        LIMIT 1
        """
        result = await self.neo4j_service.execute_query(query, {'parent_id': str(parent_id)})
        if result and result[0]['last_child_id']:
            return uuid.UUID(result[0]['last_child_id'])
        return None

    async def find_first_child_of_next_sibling(self, parent_id: uuid.UUID) -> Optional[uuid.UUID]:
        """
        Находит ID ПЕРВОГО РЕБЕНКА у СЛЕДУЮЩЕГО БРАТА текущего родителя.
        Это "точка выхода" для сшивания.
        """
        query = f"""
        MATCH (current_parent {{id: $parent_id}})
        OPTIONAL MATCH (current_parent)-[:NEXT]->(next_sibling)
        WITH next_sibling
        WHERE next_sibling IS NOT NULL
        MATCH (next_sibling)-[:CONTAINS]->(child)
        WHERE NOT ()-[:NEXT]->(child)
        RETURN child.id as first_child_id
        LIMIT 1
        """
        result = await self.neo4j_service.execute_query(query, {'parent_id': str(parent_id)})
        if result and result[0]['first_child_id']:
            return uuid.UUID(result[0]['first_child_id'])
        return None

    #--------------------------

    async def create_node(self, node_label: str, node_data: AnyNode) -> Dict[str, Any]:
        """
        Создает узел в графе с указанным лейблом и свойствами.
        """
        query = f"CREATE (n:{node_label} $props) RETURN n"
        params = {"props": node_data.model_dump(mode='json')}
        await neo4j_service.write_query(query, params)


    async def create_relationship(self, start_node_id: uuid.UUID, end_node_id: uuid.UUID, relationship_type: str) -> None:
        """
        Создает направленную связь между двумя узлами по их ID.

        Args:
            start_node_id: ID начального узла.
            end_node_id: ID конечного узла.
            relationship_type: Тип создаваемой связи (например, 'HAS_ARC').
        """
        query = (
            "MATCH (a), (b) "
            "WHERE a.id = $start_id AND b.id = $end_id "
            f"CREATE (a)-[:{relationship_type}]->(b)"
        )

        params = {
            "start_id": str(start_node_id),
            "end_id": str(end_node_id)
        }

        await neo4j_service.write_query(query, params)


    async def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        if params is None:
            params = {}
        
        await neo4j_service.execute_query(query, params)

# --- Singleton-экземпляр для удобного доступа из других частей приложения ---
graph_crud_service = GraphCrudService()
