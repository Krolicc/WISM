import uuid

from typing import Optional

from app.services.providers.vector_store_service import vector_store_service
from app.core.neo4j_service import neo4j_service

async def collect_vector_context(
    story_id: uuid.UUID, 
    query_text: str, 
    k: int = 5,
    exclude_id: Optional[uuid.UUID] = None
) -> str:
    """Finds semantically similar items from the entire story using vector search."""
    if not query_text.strip():
        return "No vector query provided."

    try:
        similar_docs = vector_store_service.search(
            story_id=story_id,
            query_text=query_text,
            limit=k,
            exclude_id=exclude_id
        )

        if not similar_docs:
            return "No semantically similar moments found in the story."
    except Exception as e:
        # Log the error in a real application
        print(f"Error during vector context collection: {e}")
        return "Could not retrieve vector context due to an error."

    # 2. Графовый анализ: определяем хронологию найденных документов
    similar_ids = [str(doc.metadata['id']) for doc in similar_docs if doc.metadata.get('id')]
    if not similar_ids or not exclude_id:
        # Если нет ID для сравнения, просто возвращаем базовый список
        titles = [f"- {doc.metadata.get('model_name', 'Элемент')} '{doc.metadata.get('title', 'Без названия')}'" for doc in similar_docs]
        return "Найдены следующие похожие элементы в истории:\n" + "\n".join(titles)

    # Запрос для определения относительного положения
    query = """
    UNWIND $similar_ids AS similar_id
    MATCH (current {id: $current_id})
    MATCH (similar {id: similar_id})

    OPTIONAL MATCH path_past = (similar)-[:NEXT*]->(current)
    OPTIONAL MATCH path_future = (current)-[:NEXT*]->(similar)

    RETURN similar.id AS id,
        CASE
            WHEN path_past IS NOT NULL THEN '[ПРОШЛОЕ]'
            WHEN path_future IS NOT NULL THEN '[БУДУЩЕЕ]'
            ELSE '[ДРУГАЯ ВЕТКА]'
        END AS relation
    """
    params = {"similar_ids": similar_ids, "current_id": str(exclude_id)}
    relations_result = await neo4j_service.read_query(query, params)
    
    relations_map = {item['id']: item['relation'] for item in relations_result}

    # 3. Собираем финальный контекст с разметкой
    context_parts = []
    for doc in similar_docs:
        doc_id = str(doc.metadata.get('id'))
        relation = relations_map.get(doc_id, '')
        model_name = doc.metadata.get('model_name', 'Элемент')
        title = doc.metadata.get('title', 'Без названия')
        
        context_parts.append(f"- {relation} {model_name} '{title}'")
            
    return "Найдены следующие похожие элементы в истории:\n" + "\n".join(context_parts)
