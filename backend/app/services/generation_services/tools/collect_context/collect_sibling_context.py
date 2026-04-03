import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.neo4j_service import neo4j_service

from .constants import CRUD_REGISTRY

async def collect_sibling_context(db: AsyncSession, item_id: uuid.UUID) -> str:
    """
    Собирает контекст соседних элементов (предыдущий и следующий),
    используя связи :NEXT в Neo4j.
    """

    async def get_items_info(records: list) -> list:
        info_list = []
        for record in records:
            crud_manager = CRUD_REGISTRY.get(record["label"])
            if not crud_manager: continue
            
            item = await crud_manager.get(db, id=uuid.UUID(record["id"]))
            if not item: continue

            title = getattr(item, 'title', 'N/A')
            description = getattr(item, 'description', getattr(item, 'overview', 'N/A'))
            info_list.append(f"- {record['label']} \nTitle:'{title}' \nDescription:'{description}'")
        return info_list

    query_prev = """
        MATCH (prev)-[:NEXT*1..3]->(n {id: $item_id})
        WITH prev, COLLECT(prev) as prev_nodes
        UNWIND prev_nodes as p
        MATCH path = (p)-[:NEXT*]->(n)
        RETURN p.id as id, labels(p)[0] as label, length(path) as depth
        ORDER BY depth DESC
    """
    params = {"item_id": str(item_id)}
    prev_results = await neo4j_service.read_query(query_prev, params)
    prev_items_info = await get_items_info(prev_results)

    query_next = """
        MATCH (n {id: $item_id})-[:NEXT*1..3]->(next)
        WITH next, COLLECT(next) as next_nodes
        UNWIND next_nodes as nxt
        MATCH path = (n)-[:NEXT*]->(nxt)
        RETURN nxt.id as id, labels(nxt)[0] as label, length(path) as depth
        ORDER BY depth ASC
    """
    next_results = await neo4j_service.read_query(query_next, params)
    next_items_info = await get_items_info(next_results)

    context = []
    if prev_items_info:
        context.append("Элементы до:\n" + "\n".join(prev_items_info))
    if next_items_info:
        context.append("Элементы после:\n" + "\n".join(next_items_info))
    
    return "\n\n".join(context) if context else "Нет повествовательного контекста."
