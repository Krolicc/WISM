
import type { Story, StoryGraph, OrchestrationAction } from '../types/index';

const API_BASE_URL = 'http://backend:8000' 

async function getWsAuthToken(url: string): Promise<string> {
    const response = await fetch(url, {
        method: 'POST',
        // credentials: 'include',
        headers: {
            'accept': 'application/json',
        }
    });
    if (!response.ok) {
        throw new Error(`Failed to get WebSocket auth token: ${response.statusText}`);
    }
    return await response.json();
}

async function getStories(): Promise<Story[]> {
  const url = `${API_BASE_URL}/api/v1/stories/`;

  const response = await fetch(url, {
    credentials: 'include',
  });

  if (!response.ok) {
    throw new Error(`Failed: ${response.statusText}`);
  }

  return await response.json();
}

async function generateStory(prompt: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/v1/stories/`, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'accept': 'application/json',
    },
    body: JSON.stringify({ prompt, child_count: 3 }),
  });
  if (!response.ok) {
    throw new Error(`Failed to create and generate story: ${response.statusText}`);
  }
}

async function orchestrateActions(story_id: string, actions: OrchestrationAction): Promise<any> {
  console.log("[Real API] Orchestrating actions for story:", story_id, actions);
  const response = await fetch(`${API_BASE_URL}/api/v1/stories/${story_id}/orchestrate`, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify(actions),
  });

  if (response.status !== 202) { 
    const errorBody = await response.json().catch(() => ({ message: response.statusText }));
    throw new Error(`Orchestration failed: ${errorBody.message || response.statusText}`);
  }

  return response.json(); 
}

async function getBootstrap(url: string): Promise<Uint8Array> {
    const response = await fetch(url, {
        method: 'GET',
        credentials: 'include',
    });
    if (!response.ok) {
        throw new Error(`Failed to get story bootstrap: ${response.statusText}`);
    }
    const data = await response.arrayBuffer();
    return new Uint8Array(data);
}

async function hydrateNode(storyId: string, nodeId: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/v1/yjs/hydrate-node?story_id=${storyId}&node_id=${nodeId}`, {
        method: 'POST',
        credentials: 'include',
    });
    if (!response.ok) {
        throw new Error(`Failed to hydrate node: ${response.statusText}`);
    }
}


export const api = {
    getStories,
    generateStory,
    orchestrateActions,
    getBootstrap,
    hydrateNode,
    getWsAuthToken
};
