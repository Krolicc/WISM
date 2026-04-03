'''
Mock for Task 3: Getting scenes from a chapter.
'''

from ._utils import load_example
from ..data_models import Scene

async def get_scenes_from_chapter(chapter_text: str) -> Scene:
    return load_example(
        task_name=f"3: Scenes from Chapter",
        prompt_file='3_chapter_to_scenes.txt',
        example_file=f"2_chapter_1_scenes.json"
    )
