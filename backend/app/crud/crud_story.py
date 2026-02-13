from .base import CRUDBase
from app.models import Story
from app.schemas import StoryCreate, StoryUpdate

class CRUDStory(CRUDBase[Story, StoryCreate, StoryUpdate]):
    # Add any story-specific methods here if needed in the future
    pass

story = CRUDStory(Story)
