
from .base import CRUDBase
from app.models import Story
from app.schemas import StoryCreate, StoryUpdate


class CRUDStory(CRUDBase[Story, StoryCreate, StoryUpdate]):
    pass

crud_story = CRUDStory(Story)
