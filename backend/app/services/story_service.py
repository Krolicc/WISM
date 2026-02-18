# --- External Imports ---
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from typing import List, Any
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

# --- Internal App Imports ---
from ..core.config import settings
from .. import crud, models, schemas

# --- Pydantic Models for LangChain ---
def_uuid = lambda: str(uuid.uuid4())

class PlotPoint(BaseModel):
    """A single, high-level point in the story's plot."""
    title: str = Field(description="A short, catchy title for this plot point (e.g., 'The Discovery').")
    description: str = Field(description="A one or two-sentence description of what happens in this part of the story.")

class ComicFrame(BaseModel):
    """A single frame or panel in the comic book."""
    panel_number: int = Field(description="The sequence number of this frame within its scene (1, 2, 3,...).")
    description: str = Field(description="A detailed visual description of the scene, camera angle, and character actions. This will be used to generate the image.")
    dialogue: str = Field(description="The dialogue spoken by characters in this frame. Can be empty if there is no speech.", default="")

class PlotResponse(BaseModel):
    """Response model containing the generated plot points."""
    plot_points: List[PlotPoint]

class FramesResponse(BaseModel):
    """Response model containing the generated frames for a plot point."""
    frames: List[ComicFrame]


# --- LangChain Service Functions (adapted from original file) ---

def get_llm(model_name: str):
    return ChatGoogleGenerativeAI(
        model=model_name,
        temperature=0.7,
        google_api_key=settings.google_api_key,
        convert_system_message_to_human=True,
        response_mime_type="application/json"
    )

async def generate_plot(prompt: str) -> PlotResponse:
    """
    Generates a list of high-level plot points (Scenes) based on a user prompt.
    """
    try:
        parser = JsonOutputParser(pydantic_object=PlotResponse)
        llm = get_llm("gemini-1.5-flash") 

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", f"You are a master storyteller. Your task is to break down a user's idea into a compelling, structured plot for a short comic. Create 3-5 distinct plot points. For each plot point, provide a short, catchy title and a one or two-sentence description. You must format your entire output as a single, valid JSON object. Do not include any markdown formatting like ```json. The response should be only the JSON object. Here are the required fields: {{format_instructions}}"),
            ("user", "{user_prompt}")
        ])

        chain = prompt_template | llm | parser
        response_data = await chain.ainvoke({
            "user_prompt": prompt,
            "format_instructions": parser.get_format_instructions()
        })
        return PlotResponse(**response_data)

    except Exception as e:
        print(f"An error occurred in generate_plot: {e}")
        return PlotResponse(plot_points=[])

async def generate_frames_for_plot_point(plot_point: PlotPoint) -> FramesResponse:
    """
    Generates a sequence of comic frames (Panels) for a single plot point.
    """
    try:
        parser = JsonOutputParser(pydantic_object=FramesResponse)
        llm = get_llm("gemini-1.5-flash")

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", f"You are a comic book writer and artist. Your job is to translate a single plot point into a sequence of 2-4 visual frames. For each frame, provide a panel number, a detailed visual description (camera angles, character actions, setting), and any dialogue. You must format the output as a single, valid JSON object. Do not include any markdown formatting like ```json. The response should be only the JSON object. Here are the required fields: {{format_instructions}}"),
            ("user", "Based on the plot point titled '{plot_title}' with the description '{plot_description}', create the comic frames.")
        ])

        chain = prompt_template | llm | parser
        response_data = await chain.ainvoke({
            "plot_title": plot_point.title,
            "plot_description": plot_point.description,
            "format_instructions": parser.get_format_instructions()
        })
        return FramesResponse(**response_data)

    except Exception as e:
        print(f"An error occurred in generate_frames_for_plot_point: {e}")
        return FramesResponse(frames=[])


# --- Main Orchestration Function ---

async def generate_and_save_story_content(
    db: AsyncSession, *, story: models.Story, story_idea: str
) -> None:
    """
    Generates and saves the full story content (scenes and panels) from an idea.
    """
    print(f"Starting content generation for story '{story.title}'...")
    
    plot_response = await generate_plot(prompt=story_idea)
    if not plot_response.plot_points:
        print("Failed to generate plot points. Aborting.")
        return

    print(f"Generated {len(plot_response.plot_points)} plot points.")

    for i, plot_point in enumerate(plot_response.plot_points):
        scene_in = schemas.SceneCreate(
            title=plot_point.title,
            description=plot_point.description,
            scene_number=i + 1,
            story_id=story.id
        )
        db_scene = await crud.scene.create(db=db, obj_in=scene_in)
        print(f"  - Created Scene {db_scene.scene_number}: '{db_scene.title}'")

        frames_response = await generate_frames_for_plot_point(plot_point)
        if not frames_response.frames:
            print(f"  - Failed to generate frames for scene {db_scene.scene_number}. Continuing to next scene.")
            continue
        
        print(f"    - Generated {len(frames_response.frames)} frames.")

        for frame in frames_response.frames:
            panel_in = schemas.PanelCreate(
                panel_number=frame.panel_number,
                description=frame.description,
                dialogue=frame.dialogue,
                scene_id=db_scene.id
            )
            await crud.panel.create(db=db, obj_in=panel_in)
    
    print(f"Content generation for story '{story.title}' complete.")
