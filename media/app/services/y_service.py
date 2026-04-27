
import uuid
from typing import Dict

import pycrdt
from sqlalchemy.orm import Session

from app.crud.crud_entity import crud_entity
from app.models.entity import Entity

_root_doc: pycrdt.Doc = None
_entity_docs: Dict[str, pycrdt.Doc] = {}


async def get_root_document_bootstrap(db: Session) -> pycrdt.Doc:
    global _root_doc
    if _root_doc is not None:
        return _root_doc

    _root_doc = pycrdt.Doc()
    # Карта, которая будет содержать субдокументы
    entities_map = _root_doc.get("entities", type=pycrdt.Map)

    # Получаем только ID и базовые метаданные, чтобы создать "заглушки"
    entities = await crud_entity.get_multi(db)

    print(entities)

    with _root_doc.transaction():
        for entity in entities:
            entity_id = str(entity.id)
            # Создаем отдельный документ для каждой сущности
            subdoc = pycrdt.Doc()
            # Помещаем субдокумент в основную карту
            entities_map[entity_id] = subdoc
            # Сохраняем ссылку в локальном кэше для быстрого доступа
            _entity_docs[entity_id] = subdoc

    def on_update(event):
        """
        Mock implementation for observing changes.
        In a real scenario, this would trigger persistence logic.
        """
        print(f"Root document updated. Event: {event}")

    entities_map.observe(on_update)

    return _root_doc

def load_entity_data(db: Session, entity_id: str) -> pycrdt.Doc:
    """
    Тот самый 'запрос на подгрузку'.
    Наполняет субдокумент реальными данными из БД.
    """
    if entity_id not in _entity_docs:
        raise ValueError(f"Entity {entity_id} not found in root doc")

    subdoc = _entity_docs[entity_id]

    # Проверяем, не загружены ли данные уже (например, по наличию ключей в map)
    data_map = subdoc.get("data", type=pycrdt.Map)
    if len(data_map) > 0:
        return subdoc

    entity = crud_entity.get(db, id=entity_id)
    if not entity:
        raise ValueError("Entity not found in DB")

    with subdoc.transaction():
        data_map["type"] = str(entity.type.value)
        data_map["canonical_name"] = entity.canonical_name
        data_map["description"] = entity.description or ""
        data_map["detailed_prompt"] = pycrdt.Map(entity.detailed_prompt)
        data_map["use_detailed_prompt"] = entity.use_detailed_prompt
        data_map["is_description_stale"] = entity.is_description_stale
        data_map["aliases"] = pycrdt.Map(entity.aliases)

    return subdoc

def apply_update_to_subdoc(entity_id: str, update: bytes):
    """Обновление конкретной сущности"""
    if entity_id in _entity_docs:
        pycrdt.apply_update(_entity_docs[entity_id], update)


def apply_update_to_root_document(update: bytes):
    """Applies a Y-py update to the root server-side document."""
    if _root_doc is None:
        # This shouldn't happen if bootstrap is called first.
        raise RuntimeError("Root document not initialized. Call get_root_document_bootstrap first.")

    pycrdt.apply_update(_root_doc, update)

