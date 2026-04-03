
from .base import CRUDBase
from app.models import Chapter
from app.schemas import ChapterCreate, ChapterUpdate


class CRUDChapter(CRUDBase[Chapter, ChapterCreate, ChapterUpdate]):
    pass

crud_chapter = CRUDChapter(Chapter)