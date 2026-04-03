'''
Mock for Task 4: Getting simple frames from a scene.
'''

from ._utils import load_example

async def get_simple_frames_from_scene(scene_text: str) -> dict:
    return load_example(
        task_name="4: Simple Frames from Scene",
        prompt_file='3_scene_to_simple_frames.txt', 
        example_file='4_scene_criterion_bar_simple_frames.json'
    )
