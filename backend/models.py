
from pydantic import BaseModel, Field
from typing import List
import uuid

def_uuid = lambda: str(uuid.uuid4())

class PlotPoint(BaseModel):
    """A single, high-level point in the story's plot."""
    id: str = Field(default_factory=def_uuid)
    title: str = Field(description="A short, catchy title for this plot point (e.g., 'The Discovery').")
    description: str = Field(description="A one or two-sentence description of what happens in this part of the story.")

class ComicFrame(BaseModel):
    """A single frame or panel in the comic book."""
    id: str = Field(default_factory=def_uuid)
    panel: int = Field(description="The sequence number of this frame (1, 2, 3,...).")
    description: str = Field(description="A detailed visual description of the scene, camera angle, and character actions. This will be used to generate the image.")
    dialogue: str = Field(description="The dialogue spoken by characters in this frame. Can be empty if there is no speech.", default="")

class GeneratePlotRequest(BaseModel):
    """Request model for generating the initial plot."""
    prompt: str

class GenerateFramesRequest(BaseModel):
    """
    Request model for generating frames for a single plot point.
    The user might have edited the plot point, so we receive it as a payload.
    """
    plot_point: PlotPoint

class PlotResponse(BaseModel):
    """Response model containing the generated plot points."""
    plot_points: List[PlotPoint]

class FramesResponse(BaseModel):
    """Response model containing the generated frames for a plot point."""
    frames: List[ComicFrame]
