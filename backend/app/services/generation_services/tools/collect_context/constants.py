
from app import crud

CRUD_REGISTRY = {
    "story": crud.crud_story,
    "arc": crud.crud_arc,
    "chapter": crud.crud_chapter,
    "scene": crud.crud_scene,
    "frame": crud.crud_frame,
    "entity": crud.crud_entity,
}