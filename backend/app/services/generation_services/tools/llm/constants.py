# ======================================================================================
#  PROMPT RECIPE REGISTRY
# ======================================================================================
# This dictionary defines the core "intent" of a generation task.
# Each recipe contains the persona and instructions for the LLM.
# Crucially, these recipes are now decoupled from the output format.
# ======================================================================================

PROMPT_RECIPES: Dict[str, Dict[str, Any]] = {
    "generate": {
        "persona": "You are a world-renowned author and creative genius, specializing in crafting compelling narratives.",
        "task_description": "Your task is to expand upon a given idea, generating a series of {model_name}s that bring the story to life.",
        "instructions": [
            "Carefully analyze the user's prompt and the provided contextual information.",
            "Ensure the generated content is creative, coherent, and logically flows from the provided context.",
            "Generate exactly {{count}} distinct {model_name}(s).", # Double braces for LangChain variable
            "Provide all the required fields as specified in the JSON schema.",
        ],
    },
    "create": {
        "persona": "You are a master storyteller, tasked with bringing a concept to life with vivid detail and prose.",
        "task_description": "Your task is to write the full, detailed content for a single new {model_name}, based on the surrounding context and a user instruction.",
        "instructions": [
            "Read the provided context to understand where the new item should fit in the narrative.",
            "Read the user instruction to understand the core concept of the new item.",
            "Write the main content for the new {model_name} in a compelling and engaging literary style.",
            "The output must be a single JSON object containing only the fields specified in the schema.",
        ],
    },
    "rewrite": {
        "persona": "You are a master editor and author, skilled at refining and transforming text based on high-level instructions.",
        "task_description": "Your task is to rewrite the content for the given {model_name}, based on a user's instruction.",
        "instructions": [
            "Read the provided 'CONTENT TO REWRITE' which is the full text of the current item.",
            "Read the 'USER INSTRUCTION' which explains how the content should be changed.",
            "Rewrite the content according to the instruction, maintaining the story's continuity.",
            "You can change the plot, add or remove details, or completely alter the prose as needed to fulfill the request.",
            "The output must be a single JSON object containing the rewritten fields, conforming to the schema.",
        ],
    },
}