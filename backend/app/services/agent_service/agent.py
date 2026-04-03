
import uuid
import json
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.services.agent_service.tools import EntityAgentTools
from app.services.helpers.llm.run_llm_generation import run_llm_generation


# --- Pydantic Models for Structured LLM Extraction ---

class ExtractedEntity(BaseModel):
    """Structured data for a single entity extracted from text by the LLM."""
    name: str = Field(description="The canonical name of the entity.")
    type: str = Field(description="The entity's type (e.g., 'character', 'location', 'item').")
    aliases: List[str] = Field(default_factory=list, description="Alternative names for the entity mentioned in the text.")
    facts: List[str] = Field(default_factory=list, description="A list of atomic facts about this entity from the text.")

class LLMExtractionResult(BaseModel):
    """The root model for the LLM's JSON output."""
    entities: List[ExtractedEntity]


class EntityProcessingAgent:
    """
    Analyzes text to extract entities and facts, then uses EntityAgentTools
    to intelligently update the knowledge base.

    The agent's own code, not the LLM, handles the application logic
    (e.g., searching before creating) to ensure robust and predictable behavior.
    """

    def __init__(self, db: AsyncSession, story_id: uuid.UUID):
        self.db = db
        self.story_id = story_id
        self.tools = EntityAgentTools(db=db)

    @staticmethod
    def _build_system_prompt() -> str:
        """Constructs the master prompt for the LLM, defining its task and output format."""
        system_prompt = f"""
        You are a specialized AI assistant for analyzing story text. Your task is to identify all named entities (characters, locations, items, etc.) and extract key facts about them from the provided text.

        1.  **Identify Entities**: Find every unique entity. Determine its primary name and type. Note any aliases used in the text.
        2.  **Extract Facts**: For each entity, pull out distinct, atomic pieces of information. A good fact is a single, self-contained statement (e.g., "wears a deerstalker hat," "is located in London," "is a magnifying glass").

        You MUST format your output as a single JSON object that conforms to the following Pydantic models:

        ```python
        class ExtractedEntity(BaseModel):
            name: str = Field(description="The canonical name of the entity.")
            type: str = Field(description="The entity's type (e.g., 'character', 'location').")
            aliases: List[str] = Field(default_factory=list, description="Alternative names for the entity mentioned in the text.")
            facts: List[str] = Field(default_factory=list, description="A list of atomic facts about this entity from the text.")

        class LLMExtractionResult(BaseModel):
            entities: List[ExtractedEntity]
        ```

        Example Input Text:
        "Sherlock Holmes, the famous detective, entered his flat at 221B Baker Street. He picked up his violin and noted that Dr. Watson seemed troubled."

        Example JSON Output:
        {{
            "entities": [
                {{
                    "name": "Sherlock Holmes",
                    "type": "character",
                    "aliases": ["the famous detective"],
                    "facts": ["has a flat at 221B Baker Street", "owns a violin"]
                }},
                {{
                    "name": "221B Baker Street",
                    "type": "location",
                    "aliases": [],
                    "facts": ["is the location of Sherlock Holmes's flat"]
                }},
                {{
                    "name": "Dr. Watson",
                    "type": "character",
                    "aliases": [],
                    "facts": ["seemed troubled"]
                }},
                {{
                    "name": "Violin",
                    "type": "item",
                    "aliases": [],
                    "facts": ["is owned by Sherlock Holmes"]
                }}
            ]
        }}

        Provide only the JSON object in your response. Do not include any other explanatory text.
        """
        return system_prompt

    async def _extract_entities_from_text(self, text_to_analyze: str) -> LLMExtractionResult:
        """Calls the LLM to perform the structured data extraction."""
        system_prompt = self._build_system_prompt()
        user_prompt = f"Here is the text to analyze:\n\n{text_to_analyze}"

        extraction_result = await run_llm_generation(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_model=LLMExtractionResult
        )
        return extraction_result

    async def process_text_and_update_db(self, text_to_analyze: str, source_node_id: uuid.UUID):
        """
        Main orchestration method.
        1. Extracts entities from text via LLM.
        2. Intelligently syncs each entity with the database.
        """
        print(f"AGENT: Starting processing of text from source node {source_node_id}...")

        # 1. Extract structured data from the text
        try:
            extracted_data = await self._extract_entities_from_text(text_to_analyze)
            if not extracted_data or not extracted_data.entities:
                print("AGENT: LLM did not extract any entities. Finishing.")
                return
        except Exception as e:
            print(f"AGENT ERROR: Failed to get or parse LLM response: {e}")
            return

        print(f"AGENT: Extracted {len(extracted_data.entities)} entities from text.")

        # 2. Process each extracted entity sequentially
        for entity_data in extracted_data.entities:
            print(f"AGENT: Processing extracted entity '{entity_data.name}'...")
            entity_id = None

            # a. Search for the entity to avoid duplicates.
            search_results = await self.tools.search_for_entity(
                query=entity_data.name,
                story_id=self.story_id,
                entity_type=entity_data.type
            )

            # Use the top search result if it's a strong match (score > 0.9)
            if search_results and search_results[0].score > 0.9:
                entity_id = search_results[0].id
                print(f"  - Found existing entity with ID: {entity_id} (Score: {search_results[0].score})")
            else:
                # b. If not found or match is weak, create a new entity.
                print(f"  - No strong match found. Creating new entity...")
                new_id_str = await self.tools.create_new_entity(
                    canonical_name=entity_data.name,
                    entity_type=entity_data.type,
                    story_id=self.story_id,
                    aliases=entity_data.aliases
                )
                entity_id = uuid.UUID(new_id_str)
                print(f"  - Created new entity with ID: {entity_id}")

            # c. Link the entity (whether new or existing) to the source node.
            await self.tools.link_entity_to_node(
                entity_id=entity_id,
                node_id=source_node_id
            )
            print(f"  - Linked entity {entity_id} to source node {source_node_id}")

            # d. Add all extracted facts about the entity to the database.
            for fact in entity_data.facts:
                await self.tools.add_information_to_entity(
                    entity_id=entity_id,
                    fact=fact,
                    source_node_id=source_node_id
                )
                print(f"  - Added fact: '{fact}'")
        
        print(f"AGENT: Finished processing text from source node {source_node_id}.")
