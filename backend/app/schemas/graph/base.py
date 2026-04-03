import uuid

from typing import Optional, List
from pydantic import BaseModel, Field

from ..enums import EntityType

# --- Базовый узел ---
class Node(BaseModel):
    """Базовая модель для узла в графе, содержит общие поля."""
    id: uuid.UUID
    story_id: uuid.UUID
    title: str

# --- Узлы структуры истории ---
class StoryNode(Node):
    """Pydantic модель для узла Story в графе."""

class ArcNode(Node):
    """Pydantic модель для узла Arc в графе."""
    pass

class ChapterNode(Node):
    """Pydantic модель для узла Chapter в графе."""
    pass

class SceneNode(Node):
    """Pydantic модель для узла Scene в графе."""
    pass

class FrameNode(Node):
    """Pydantic модель для узла Frame в графе."""
    pass

# --- Узел сущности ---
class EntityNode(BaseModel):
    """Pydantic модель для узла Entity."""
    id: uuid.UUID
    story_id: uuid.UUID
    canonical_name: str
    type: EntityType
    aliases: Optional[List[str]] = []