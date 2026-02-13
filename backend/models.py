from pydantic import BaseModel

# --- Data Models ---
class StoryPrompt(BaseModel):
    """The user's initial prompt for the story."""
    prompt: str

class GeneratedStory(BaseModel):
    """The generated story plot."""
    story_id: int
    story_plot: str
