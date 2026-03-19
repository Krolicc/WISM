
export interface Frame {
  id: string;
  common_description: string | null;
  detailed_prompt: Record<string, any>; // Represents a JSON object
  use_detailed_prompt: boolean;
  image_url: string | null;
  order: number;
  isLoading?: boolean;
}

export interface Scene {
  id: string;
  title: string;
  description: string | null;
  frames: Frame[];
  order: number;
  isLoading?: boolean;
}

export interface Chapter {
  id: string;
  title: string;
  description: string | null;
  scenes: Scene[];
  order: number;
  isLoading?: boolean;
}

export interface Character {
  id: string;
  name: string;
  description: string | null;
}

export interface Story {
  id: string;
  title: string;
  description: string | null;
  chapters: Chapter[];
  characters: Character[];
  isLoading?: boolean;
}

// --- Orchestration Types ---

export interface OrchestrationAction {
  crud: Record<string, any>[];
  generate: Record<string, any>[];
}

// --- Graph Types ---

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
