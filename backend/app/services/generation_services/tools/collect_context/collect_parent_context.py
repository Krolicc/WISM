import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.neo4j_service import neo4j_service
from .constants import CRUD_REGISTRY

async def collect_parent_context(db: AsyncSession, parent_id: uuid.UUID) -> str:
    """
    Собирает контекст родительских элементов, получая структуру из Neo4j и контент из PostgreSQL.
    Использует единую связь :CONTAINS для обхода иерархии.
    """
    # 1. Получаем ID и метки всех предков из графа с помощью связи :CONTAINS
    query = """
        CALL {
            MATCH (n {id: $item_id}) RETURN n, 0 AS depth
            UNION ALL
            MATCH p = (ancestor)-[:CONTAINS*]->(n {id: $item_id})
            RETURN ancestor AS n, length(p) AS depth
        }
        RETURN n.id AS id, labels(n)[0] AS label
        ORDER BY depth DESC
    """
    params = {"item_id": str(parent_id)}
    results = await neo4j_service.read_query(query, params)

    if not results:
        return "No parent context available."

    # 2. Получаем контент для каждого предка из PostgreSQL
    context_parts = []
    for record in results:
        node_id = uuid.UUID(record["id"])
        node_label = record["label"]

        crud_manager = CRUD_REGISTRY.get(node_label)
        if not crud_manager:
            continue

        parent_item = await crud_manager.get(db, id=node_id)
        if not parent_item:
            continue

        title = getattr(parent_item, 'title', 'N/A')
        content = getattr(parent_item, 'description', getattr(parent_item, 'overview', ''))
        
        parent_info = f"Level: {node_label}\\nTitle: {title}"
        if content:
            parent_info += f"\\nContent: {content}"
        context_parts.append(parent_info)

    return "\\n\\n---\\n\\n".join(context_parts)