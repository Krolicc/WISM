
// --- Base Graph Node --- 

export type BaseNodeContent = {
  title: string;
  description?: string;
  overview?: string;
}

export interface BaseNode {
  id: string;
  type: string;
  content: BaseNodeContent;
  parent_id: string | null;
  next_ids: string[];
  prev_ids: string[];
  children_ids: string[];
}

// --- Discriminated Union for Story Nodes ---

export interface Story {
  id: string;
  type: "story";
  title: string;
  description?: string;
  overview?: string;
  children_ids: string[];
}

export interface Arc extends BaseNode {
  type: 'arc';
}

export interface Chapter extends BaseNode {
  type: 'chapter';
}

export interface Scene extends BaseNode {
  type: 'scene';
}

export interface BranchSet {
  id: string;
  type: 'branchSet';
  title: string;
  question: string;
  parent_id: string | null;
  next_ids: string[];
  prev_ids: string[];
  branches: Record<string, { label: string }>;
  selectedBranchId?: string;
}

export interface Frame {
  id: string;
  type: 'frame';
  use_detailed_prompt: boolean;
  detailed_prompt: Record<string, any>; // JSON object
  image_url?: string;
  common_description?: string;
  source_text_range: { start: number; end: number } | null;
  width?: number;
  height?: number;
}

// The union of all possible node types
export type StoryNode = Arc | Chapter | Scene | BranchSet;

// --- Graph Structure ---
export interface StoryEdge {
  source: string;
  target: string;
  type: 'CONTAINS' | 'NEXT';
}

export interface StoryGraph {
  nodes: StoryNode[];
  edges: StoryEdge[];
}


// --- Orchestration Types ---

export interface OrchestrationAction {
  crud: Record<string, any>[];
  generate: Record<string, any>[];
}

// --- Generic Graph Types (for raw graph data) ---

export interface GraphNode {
  element_id: string;
  labels: string[];
  properties: {
    name: string;
    description: string;
    [key: string]: any;
  };
  x?: number;
  y?: number;
}

export interface GraphRelationship {
  source: string;
  target: string;
  type: string;
  properties: {
    description: string;
    [key: string]: any;
  };
}

export interface FullGraphResponse {
  nodes: GraphNode[];
  relationships: GraphRelationship[];
}
