'''
Mock for Task 7: Enriching a single entity.
'''

from ._utils import load_example

async def enrich_entity(entity_data: dict) -> dict:
    return load_example(
        task_name="7: Enrich Entity",
        prompt_file='6_enrich_entity.txt',
        example_file='15_entity_enrichment.json' # Mock: always return the same entity
    )
