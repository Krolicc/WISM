import re
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from typing import List

from backend.config import settings
from backend.models import PlotPoint, ComicFrame, PlotResponse, FramesResponse

async def generate_plot(prompt: str) -> PlotResponse:
    """
    Generates a list of high-level plot points based on a user prompt.
    """
    try:
        # We specifically want a JSON output from the model
        parser = JsonOutputParser(pydantic_object=PlotResponse)

        llm = ChatGroq(
            model="llama3-70b-8192",
            temperature=0.7,
            groq_api_key=settings.groq_api_key,
            model_kwargs={
                "response_format": {"type": "json_object"} # Crucial for getting JSON output
            }
        )

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", "You are a master storyteller. Your task is to break down a user's idea into a compelling, structured plot for a short comic. Create 3-5 distinct plot points. For each plot point, provide a short, catchy title and a one or two-sentence description. Format your entire output as a single JSON object with a key 'plot_points' which contains a list of these points. Here are the required fields for each point: {format_instructions}"),
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
        # In case of an error, return an empty plot response
        return PlotResponse(plot_points=[])

async def generate_frames_for_plot_point(plot_point: PlotPoint) -> FramesResponse:
    """
    Generates a sequence of comic frames for a single plot point.
    """
    try:
        parser = JsonOutputParser(pydantic_object=FramesResponse)

        llm = ChatGroq(
            model="llama3-70b-8192",
            temperature=0.6,
            groq_api_key=settings.groq_api_key,
            model_kwargs={
                "response_format": {"type": "json_object"}
            }
        )

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", "You are a comic book writer and artist. Your job is to translate a single plot point into a sequence of 2-4 visual frames. For each frame, provide a detailed visual description (camera angles, character actions, setting) and any dialogue. Format the output as a JSON object with a 'frames' key containing a list of frame objects. Here are the required fields for each frame: {format_instructions}"),
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
