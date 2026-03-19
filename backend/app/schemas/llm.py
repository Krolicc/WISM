
# --- External Imports ---
from typing import List
from pydantic import BaseModel, Field

# --- LLM Response Schemas ---

class LLMScenePoint(BaseModel):
    """A Pydantic model representing a single scene's title and description from the LLM."""
    title: str = Field(description="A short, catchy title for this scene (e.g., 'The Confrontation').")
    description: str = Field(description="A one or two-sentence description of what happens in this part of the chapter.")

class LLMFrame(BaseModel):
    """A Pydantic model for a single comic frame's details from the LLM."""
    # panel_number is requested from the LLM but not currently used for ordering.
    # The services use a loop index instead. It's kept for future-proofing.
    common_description: str = Field(description="A detailed visual description of the scene, camera angle, character actions and any dialogue. This will be used to generate the image.")

class LLMChapter(BaseModel):
    """A Pydantic model for a full chapter's details from the LLM, including scenes."""
    title: str = Field(description="A short, evocative title for the chapter.")
    description: str = Field(description="A one or two-sentence summary of the chapter's content.")

class LLMStory(BaseModel):
    """A Pydantic model for a full story's details from the LLM."""
    title: str = Field(description="A short, evocative title for the story.")
    description: str = Field(description="A one or two-sentence summary of the story's content.")



# --- List/Response Wrappers ---

class LLMFrameList(BaseModel):
    """A Pydantic model that wraps a list of LLMFrame objects."""
    frames: List[LLMFrame]

class LLMScenePointList(BaseModel):
    """A Pydantic model that wraps a list of LLMScenePoint objects."""
    scenes: List[LLMScenePoint]

class LLMChapterList(BaseModel):
    """A Pydantic model that wraps a list of LLMChapter objects."""
    chapters: List[LLMChapter]
