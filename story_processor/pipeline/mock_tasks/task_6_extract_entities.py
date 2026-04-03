'''
Mock for Task 6: Extracting entities from the story.
'''

from ._utils import load_example

async def extract_entities(story_text: str) -> dict:
    return load_example(
        task_name="6: Extract Entities",
        prompt_file='5_extract_entities.txt',
        example_file='14_entities.json'
    )
