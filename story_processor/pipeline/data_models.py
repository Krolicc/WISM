'''
This module defines the Pydantic data models for the story processing pipeline.
These models provide structure and validation for the data at each stage.
'''
from collections import deque
from typing import Any, Deque, Dict, List, Optional

from pydantic import BaseModel, Field

# --- Entity Models ---

class RawEntity(BaseModel):
    '''Represents a single named entity (character, location, etc.).'''
    canonical_name: str = Field(..., description="The official, primary name of the entity.")
    aliases: List[str] = Field(default_factory=list, description="Alternative names or references.")

class RawEntities(BaseModel):
    characters: List[RawEntity] = Field(default_factory=list)
    locations: List[RawEntity] = Field(default_factory=list)

class EnrichEntity(RawEntity):
    description: str

class EnrichEntities(RawEntities):
    '''Holds all extracted entities, categorized by type.'''
    characters: List[EnrichEntity] = Field(default_factory=list)
    locations: List[EnrichEntity] = Field(default_factory=list)

# --- Frame Models (for image generation) ---

class DetailedFramePrompt(BaseModel):
    '''Pydantic model for the detailed prompt structure, based on JSON examples.'''
    class Setting(BaseModel):
        location_type: str
        description: str
        time_of_day: str
        weather: str
        key_objects: List[str]
        background_details: str

    class Camera(BaseModel):
        angle: str
        shot_type: str
        lens_type: str
        focus: str
        motion_blur: str

    class Lighting(BaseModel):
        style: str
        sources: List[str]
        color_temperature: str
        description: str

    class Composition(BaseModel):
        rule: str
        leading_lines: str
        notes: str

    class Style(BaseModel):
        class ColorPalette(BaseModel):
            primary_colors: List[str]
            mood: str

        medium: str
        reference_artists: List[str]
        general_style: str
        color_palette: ColorPalette
        quality_tags: str

    negative_prompt: str
    setting: Setting
    camera: Camera
    lighting: Lighting
    composition: Composition
    style: Style

class Frame(BaseModel):
    '''Represents a single frame or panel in a scene.'''
    source_text: str = Field(..., description="The segment of the original text this frame is based on.")
    common_description: str = Field(..., description="A concise, human-readable summary of the frame's content.")
    detailed_prompt: Optional[DetailedFramePrompt] = Field(None, description="A rich, detailed prompt for an image generator.")


# --- Hierarchical Story Structure Models ---

class Scene(BaseModel):
    '''Represents a continuous action in a single location.'''
    summary: str = Field(..., description="A brief summary of the scene.")
    characters: List[str] = Field(default_factory=list, description="List of characters present in the scene.")
    location: str = Field(..., description="The primary location of the scene.")
    text: str = Field(..., description="The full text of the scene.")

class Chapter(BaseModel):
    '''Represents a chapter of the story.'''
    title: str = Field(..., description="The title of the chapter.")
    first_sentence: str = Field(..., description="The first sentence, used for identification.")


# --- Pipeline-Internal Models ---

class RawChapter(BaseModel):
    title: str
    first_sentence: str

class RawChapterResult(BaseModel):
    potential_chapters: List[RawChapter] = Field(default_factory=list)

class IntermediateResults(BaseModel):
    '''
    A structured container for intermediate data produced during the pipeline run.
    This data is not part of the final, clean output.
    '''
    raw_chapters: Optional[RawChapterResult] = None
    raw_entities: Optional[RawEntities] = Field(default_factory=RawEntities)

class StatusFlags(BaseModel):
    '''Tracks the readiness of different pipeline phases and tasks.'''
    chapters_ready: bool = False
    entities_ready: bool = False
    entities_tasks_count: int = 0
    error_occurred: bool = False

    pending_tasks_count: int = 0

# --- Main Pipeline Data Model ---

class PipelineData(BaseModel):
    '''
    The main state-holding model for the entire pipeline.
    It uses the specific models defined above for strong typing.
    '''
    # --- Final, Clean Data ---
    full_story_text: str = ""
    chapters: List[Chapter] = Field(default_factory=list)
    entities: EnrichEntities = Field(default_factory=EnrichEntities)
    
    # --- Pipeline Internals ---
    intermediate_results: IntermediateResults = Field(
        default_factory=IntermediateResults, 
        exclude=True # Exclude from final serialization
    )
    task_queue: Deque[Any] = Field(
        default_factory=deque, 
        exclude=True
    )

    status_flags: StatusFlags = Field(default_factory=StatusFlags)

    class Config:
        arbitrary_types_allowed = True
