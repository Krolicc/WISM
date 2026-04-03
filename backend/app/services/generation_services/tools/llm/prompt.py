from pydantic import BaseModel
from typing import Optional, Type, Tuple, Dict, Any

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate

from .constants import PROMPT_RECIPES

def construct_prompt_template(
    task: str,
    model_name: str,
    pydantic_schema: Type[BaseModel],
    list_name: Optional[str] = None,
) -> Tuple[ChatPromptTemplate, JsonOutputParser]:

    recipe = PROMPT_RECIPES.get(task)
    if not recipe:
        raise ValueError(f"Unknown prompt task: '{task}'. Available tasks: {list(PROMPT_RECIPES.keys())}")

    parser = JsonOutputParser(pydantic_object=pydantic_schema)
    system_prompt_parts = []

    # 1. Persona & Task
    system_prompt_parts.append(recipe["persona"])
    system_prompt_parts.append(recipe["task_description"].format(model_name=model_name))

    # 2. Context
    system_prompt_parts.append("**Contextual Information:**\n{context}")

    # 3. Instructions
    instructions = [inst.format(model_name=model_name) for inst in recipe["instructions"]]
    instruction_block = "**Instructions:**\n" + "\n".join(
        f"{i+1}. {inst}" for i, inst in enumerate(instructions)
    )
    system_prompt_parts.append(instruction_block)

    # 4. Output Format (Determined by `list_name`, not the recipe)
    if list_name:
        output_format_block = (
            f"Your entire output must be a single, valid JSON object. The main key of this object should be '{list_name}', "
            f"and its value should be an array of the {model_name} objects."
        )
    else:
        output_format_block = (
            "Your entire output must be a single, valid JSON object that adheres to the provided schema."
        )

    system_prompt_parts.append(
        f"**Output Format:**\n{output_format_block}\n\n"
        "**JSON Schema:**\n{format_instructions}"
    )

    # 5. Footer
    system_prompt_parts.append("Begin generation now.")

    # --- Assemble Final Template ---
    system_template = "\n\n".join(system_prompt_parts)
    user_template = "{prompt}"

    prompt_template = ChatPromptTemplate.from_messages(
        [("system", system_template), ("user", user_template)]
    )

    return prompt_template, parser
