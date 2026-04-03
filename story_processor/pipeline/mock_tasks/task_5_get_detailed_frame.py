'''
Mock for Task 5: Getting a detailed frame from a simple frame.
'''

from ._utils import load_example
from ..data_models import DetailedFramePrompt

async def get_detailed_frame(description: str, entities: dict) -> DetailedFramePrompt:
    return load_example(
        task_name="5: Detailed Frame from Simple Frame",
        prompt_file='4_simple_frame_to_detailed_frame.txt', 
        example_file='5_frame_criterion_bar_detailed.json' # Mock: always return the same frame
    )
