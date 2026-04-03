'''
Mock for Task 2: Consolidating the found chapters.
'''

from typing import List
from ..data_models import Chapter, RawChapterResult

async def consolidate_chapters(chapters_data: RawChapterResult) -> List[Chapter]:
    '''
    Simulates Task 2: For mock purposes, we'll just return the same data.
    In a real scenario, this step might fix numbering, merge small sections, etc.
    '''
    print("\n--- [MOCK AI CALL] Task: 2: Consolidate Chapters ---")
    print("SIMULATING: No change to chapter data in mock mode.")
    print("--- [END MOCK AI CALL] ---")
    return [Chapter(**c.model_dump()) for c in chapters_data.potential_chapters]
