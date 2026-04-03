'''
Mock for Task 1: Breaking a full story text into chapters.
'''

from ._utils import load_example

async def get_chapters_from_story(story_text: str) -> dict:
    '''Simulates the call to get chapters from a story.'''
    return load_example(
        task_name="1: Find Chapters", 
        prompt_file='1_find_chapters.txt', 
        example_file='1_chapters.json'
    )
