import uuid
from typing import Any, Dict, Optional, List

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.tools import get_llm
from .prompt import construct_prompt_template
from app.core.config import settings

async def generate_content_from_prompt(
    task: str,
    prompt: str, 
    context: str,
    llm_schema: dict,
    model_name: str,
    count: int = 1, 
    temperature: float = 0.7, 
) -> Optional[BaseModel]:
    """
    Generates structured content from an LLM, enriching the prompt with context.
    """
    pydantic_schema = llm_schema["schema"]
    list_name = llm_schema.get("name")

    # Construct the final prompt and parser for the LLM
    prompt_template, parser = construct_prompt_template(
        model_name=model_name,
        task=task, 
        pydantic_schema=pydantic_schema, 
        list_name=list_name
    )
    
    prompt_variables = {
        "count": count, 
        "prompt": prompt,
        "context": context,
        "format_instructions": parser.get_format_instructions()
    }

    try:
        llm = get_llm(settings.google_ai_model_version, temperature=temperature)
        chain = prompt_template | llm | parser
        # Use .ainvoke for async execution and proper error propagation
        response_data = await chain.ainvoke(prompt_variables)
        # The parser already returns a Pydantic object, no need to re-validate
        return response_data
    except Exception as e:
        # Catching specific parsing or validation errors is better, but this is a safeguard
        print(f"An error occurred in the LLM generation chain for {model_name}: {e}")
        return None

