import os
from typing import Type
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

JSON_EXAMPLE = '''```json
{
  "nodes": [
    {
      "label": "Character",
      "properties": {
        "name": "Aragorn",
        "description": "A lone man standing on the summit of Weathertop, holding a sword."
      }
    },
    {
      "label": "Location",
      "properties": {
        "name": "Weathertop Summit",
        "description": "A windy summit where a confrontation is taking place."
      }
    },
    {
      "label": "Item",
      "properties": {
        "name": "Anduril",
        "description": "A sword possessed by Aragorn."
      }
    }
  ],
  "relationships": [
    {
      "source_node_name": "Aragorn",
      "source_node_label": "Character",
      "target_node_name": "Weathertop Summit",
      "target_node_label": "Location",
      "type": "IS_IN",
      "properties": {
        "description": "Aragorn is standing on the summit of Weathertop."
      }
    },
    {
      "source_node_name": "Aragorn",
      "source_node_label": "Character",
      "target_node_name": "Anduril",
      "target_node_label": "Item",
      "type": "POSSESSES",
      "properties": {
        "description": "Aragorn's hand is on the hilt of his sword, Anduril."
      }
    }
  ]
}
```'''

def load_prompt_template(file_name: str) -> str:
    """Loads a prompt template from a file in the same directory."""
    # Construct the absolute path to the file
    # This assumes the prompt file is in the same directory as this script
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, file_name)
    with open(file_path, 'r') as f:
        return f.read()

def construct_knowledge_graph_prompt(
    pydantic_schema: Type[BaseModel],
) -> tuple[ChatPromptTemplate, JsonOutputParser]:
    """
    Constructs a chat prompt template for knowledge graph extraction.
    """
    parser = JsonOutputParser(pydantic_object=pydantic_schema)

    # Load the system message from the markdown file
    # NOTE: The template file uses {{scene_text}} as its variable.
    system_template = load_prompt_template("prompt_template.md")

    # The user message is now just a placeholder for the scene text
    user_template = "{scene_text}"

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_template),
        ("user", user_template)
    ]).partial(
        json_example=JSON_EXAMPLE,
        format_instructions=parser.get_format_instructions()
    )

    return prompt, parser
