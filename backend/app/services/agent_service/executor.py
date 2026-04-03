
import json
import uuid
import inspect
from typing import List, Dict, Any, get_type_hints
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.agent_service.agent_tools import EntityAgentTools
from app.services.tools.llm_provider import get_llm
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from app.services.agent_service.helpers import get_python_type_to_json_schema

class AgentExecutor:
    """
    Manages the agentic workflow by orchestrating the interaction between the LLM
    and the available tools. It dynamically inspects tools and provides them to the LLM.
    """

    def __init__(self, db: AsyncSession, story_id: uuid.UUID, source_node_id: uuid.UUID):
        self.db = db
        self.story_id = story_id
        self.source_node_id = source_node_id
        self.tools_instance = EntityAgentTools(db=db)
        self.llm = get_llm(model_name="gemini-1.5-flash", temperature=0.0)
        self.tools = self._discover_tools()
        self.llm_with_tools = self.llm.bind_tools(self.tools)

    def _discover_tools(self) -> List[Dict[str, Any]]:
        """Dynamically constructs a list of tools for the LLM by inspecting EntityAgentTools methods."""
        tool_definitions = []
        for name, method in inspect.getmembers(self.tools_instance, predicate=inspect.ismethod):
            if name.startswith('_'):
                continue

            docstring = inspect.getdoc(method)
            if not docstring:
                continue

            sig = inspect.signature(method)
            type_hints = get_type_hints(method)

            parameters_schema = {"type": "object", "properties": {}, "required": []}
            for param_name, param in sig.parameters.items():
                if param_name in ['self', 'db', 'story_id', 'source_node_id', 'node_id']:
                    continue
                
                param_type = type_hints.get(param_name)
                param_schema = get_python_type_to_json_schema(param_type)
                
                parameters_schema["properties"][param_name] = param_schema
                if param.default is inspect.Parameter.empty:
                    parameters_schema["required"].append(param_name)

            tool_definitions.append({
                "type": "function",
                "function": {
                    "name": name,
                    "description": docstring,
                    "parameters": parameters_schema
                }
            })
        return tool_definitions

    async def _execute_tool_call(self, tool_call: Dict[str, Any]) -> Any:
        """Executes a single tool call requested by the LLM with automatic context injection."""
        tool_name = tool_call["function"]["name"]
        tool_args = json.loads(tool_call["function"]["arguments"])
        
        tool_method = getattr(self.tools_instance, tool_name)
        sig = inspect.signature(tool_method)

        if 'story_id' in sig.parameters:
            tool_args['story_id'] = self.story_id
        if 'source_node_id' in sig.parameters:
            tool_args['source_node_id'] = self.source_node_id
        if 'node_id' in sig.parameters:
            tool_args['node_id'] = self.source_node_id

        # Convert UUID strings from LLM to UUID objects where needed
        for param_name, hint in get_type_hints(tool_method).items():
            if (str(hint) == '~UUID' or hint is uuid.UUID) and param_name in tool_args:
                if isinstance(tool_args[param_name], str):
                    tool_args[param_name] = uuid.UUID(tool_args[param_name])

        return await tool_method(**tool_args)

    async def run(self, text_to_analyze: str):
        """Main execution loop for the agent."""
        print(f"AGENT EXECUTOR: Starting analysis of text from node {self.source_node_id}")
        
        system_prompt = f"""
        You are a highly intelligent AI assistant designed to build a knowledge graph from a piece of text. 
        Your primary goal is to identify all named entities (characters, locations, items, concepts), extract key facts about them, and link them to the source text.
        You MUST follow this workflow precisely:
        1.  **Identify Entities**: Read the text and identify all potential entities.
        2.  **Search Before Creating**: For EACH potential entity, you MUST use the `search_for_entity` tool to check if it already exists in the knowledge base. This is the most important rule to prevent duplicates.
        3.  **Decide to Create or Use**:
            - If `search_for_entity` returns a high-confidence match, use the returned entity ID for all subsequent actions.
            - If `search_for_entity` returns no matches or only low-confidence matches, you MUST use the `create_new_entity` tool to create a new one. Use the newly created ID for subsequent actions.
        4.  **Add Facts**: Once you have an entity ID (either from searching or creating), use the `add_information_to_entity` tool to add any new, atomic facts you've learned from the text about that entity.
        5.  **Link to Source**: For EVERY entity you have processed (both found and created), you MUST use the `link_entity_to_node` tool to create a connection between the entity and the text from which it was extracted. This is mandatory.
        6.  **Work Methodically**: Process one entity completely (Search -> Create/Use -> Add Facts -> Link) before moving to the next. You can make multiple tool calls in a single turn to achieve this.
        7.  **Completion**: Once you are certain you have processed every entity in the text and performed all the required steps (Search, Create/Use, Add Facts, Link), and only then, respond with a final message in the format: "Analysis complete. Processed N entities." where N is the number of entities you handled.
        You are analyzing text for story ID `{self.story_id}` and it comes from source node ID `{self.source_node_id}`. These contextual IDs are handled for you.
        Do not hallucinate or make up information. Stick to the text provided.
        """

        messages = [
            HumanMessage(content=system_prompt, name="system"),
            HumanMessage(content=text_to_analyze, name="user")
        ]

        while True:
            print("\n--- AGENT: Invoking LLM ---")
            ai_response = await self.llm_with_tools.ainvoke(messages)
            messages.append(ai_response)

            if not ai_response.tool_calls:
                print("--- AGENT: LLM finished reasoning. ---")
                print(f"Final Response: {ai_response.content}")
                break
            
            print(f"--- AGENT: LLM requested {len(ai_response.tool_calls)} tool calls. ---")
            
            tool_messages = []
            for tool_call in ai_response.tool_calls:
                tool_name = tool_call['function']['name']
                print(f"  - Requesting tool: {tool_name}")
                print(f"  - Arguments: {tool_call['function']['arguments']}")
                
                try:
                    result = await self._execute_tool_call(tool_call)
                    # Improved result serialization
                    if isinstance(result, list) and all(hasattr(item, '__dict__') for item in result):
                        serializable_result = [item.__dict__ for item in result]
                    elif hasattr(result, '__dict__'):
                        serializable_result = result.__dict__
                    else:
                        serializable_result = str(result)

                    tool_messages.append(ToolMessage(
                        content=json.dumps({"result": serializable_result}, default=str), 
                        tool_call_id=tool_call['id'],
                        name=tool_name
                    ))
                    print(f"  - Tool '{tool_name}' executed.")
                except Exception as e:
                    print(f"  - ERROR executing tool '{tool_name}': {e}")
                    tool_messages.append(ToolMessage(
                        content=json.dumps({"error": str(e)}),
                        tool_call_id=tool_call['id'],
                        name=tool_name
                    ))
            
            messages.extend(tool_messages)
