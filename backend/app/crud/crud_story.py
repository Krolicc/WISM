
from sqlalchemy.orm import subqueryload

from .base import CRUDBase
from app.models import Story, Chapter, Scene
from app.schemas import StoryCreate, StoryUpdate


class CRUDStory(CRUDBase[Story, StoryCreate, StoryUpdate]):
    def _get_eager_loading_options(self) -> list:
        return [
            subqueryload(Story.chapters)
            .subqueryload(Chapter.scenes)
            .subqueryload(Scene.frames),
            # subqueryload(Story.characters),
        ]


crud_story = CRUDStory(Story)
