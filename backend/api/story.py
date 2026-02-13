from fastapi import APIRouter
from backend.models import StoryPrompt, GeneratedStory
from backend.services import story_service
ц
router = APIRouter()

@router.post("/generate-story", response_model=GeneratedStory)
async def generate_story(prompt: StoryPrompt):
    """
    Receives a prompt and generates a story plot using an AI model.
    """
    # Call the story generation service
    generated_plot = await story_service.generate_story_from_prompt(prompt.prompt)
    
    # For now, we use a static story_id
    # In the future, this would be generated and stored in a database
    return GeneratedStory(story_id=1, story_plot=generated_plot)
