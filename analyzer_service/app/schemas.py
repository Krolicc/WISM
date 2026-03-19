
from pydantic import BaseModel, Field
from typing import List

# --- Sub-Schemas for Properties ---
# By creating specific models for properties, we enforce a stricter structure,
# ensuring that the LLM provides all the necessary fields, including descriptions.

class NodeProperties(BaseModel):
    """
    Defines the structured properties for a Node.
    'name' is mandatory and unique. 'description' provides context from the scene.
    """
    name: str = Field(description="The unique, human-readable identifier for the node.")
    description: str = Field(description="A brief description of the node based ONLY on the information in the current scene.")

class RelationshipProperties(BaseModel):
    """
    Defines the structured properties for a Relationship.
    'description' provides context for the connection.
    """
    description: str = Field(description="A brief explanation of the relationship based ONLY on the information in the current scene.")


# --- Knowledge Graph Schemas ---

class Node(BaseModel):
    """
    Represents a node in the knowledge graph.
    Now uses the strict NodeProperties model.
    """
    label: str = Field(description="The category or type of the node (e.g., 'Character', 'Location', 'Item', 'Event').")
    properties: NodeProperties = Field(description="The structured attributes of the node.")

class Relationship(BaseModel):
    """
    Represents a directed edge between two nodes in the knowledge graph.
    Now uses the strict RelationshipProperties model.
    """
    source_node_name: str = Field(description="The 'name' property of the source node.")
    source_node_label: str = Field(description="The 'label' of the source node.")
    target_node_name: str = Field(description="The 'name' property of the target node.")
    target_node_label: str = Field(description="The 'label' of the target node.")
    type: str = Field(description="The type of the relationship (e.g., 'INTERACTS_WITH').")
    properties: RelationshipProperties = Field(description="The structured attributes of the relationship.")

class KnowledgeGraph(BaseModel):
    """
    Represents the full knowledge graph extracted from a piece of text.
    It contains a list of all identified nodes and their relationships.
    """
    nodes: List[Node] = Field(description="A list of all unique nodes (entities) found in the text.")
    relationships: List[Relationship] = Field(description="A list of all relationships between the nodes.")
