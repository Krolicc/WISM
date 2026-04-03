'''
This package contains mock implementations for each task in the story processing pipeline.

The __all__ variable defines the public API of this package, making the task
functions directly importable from `story_processor.pipeline.mock_tasks`.
'''

from .task_1_get_chapters import get_chapters_from_story as extract_chapters
from .task_2_consolidate_chapters import consolidate_chapters
from .task_3_get_scenes import get_scenes_from_chapter as extract_scenes
from .task_4_get_simple_frames import get_simple_frames_from_scene as extract_simple_frames
from .task_5_get_detailed_frame import get_detailed_frame as enrich_frame
from .task_6_extract_entities import extract_entities
from .task_7_enrich_entity import enrich_entity

__all__ = [
    'extract_chapters',
    'consolidate_chapters',
 
    'extract_entities',
    'enrich_entity',
 
    'extract_scenes',
    'extract_simple_frames',
    'enrich_frame',
]