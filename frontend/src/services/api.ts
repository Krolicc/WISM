
import type { Story, OrchestrationAction, FullGraphResponse } from '../types/index';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://8000-firebase-wism-1770010266998.cluster-4cmpbiopffe5oqk7tloeb2ltrk.cloudworkstations.dev';

async function getAllStories(): Promise<Story[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/stories/`, {
    credentials: 'include',
  });
  if (!response.ok) {
    throw new Error(`Failed to fetch stories: ${response.statusText}`);
  }
  return await response.json();
}

async function generateStory(prompt: string): Promise<Story> {
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
  return await response.json();
}

async function orchestrateActions(story_id: string, actions: OrchestrationAction): Promise<any> {
  
  console.log(actions)

  const response = await fetch(`${API_BASE_URL}/api/v1/stories/${story_id}/orchestrate`, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify( actions ), // The backend expects an object with an 'actions' key
  });

  if (response.status !== 202) { // Backend returns 202 Accepted
    const errorBody = await response.json().catch(() => ({ message: response.statusText }));
    throw new Error(`Orchestration failed: ${errorBody.message || response.statusText}`);
  }

  return response.json(); // May contain a task ID or other info
}

async function getFullGraph(): Promise<FullGraphResponse> {
    const response = await fetch(`${API_BASE_URL}/api/v1/graph/full`, {
        credentials: 'include',
    });
    if (!response.ok) {
        throw new Error(`Failed to fetch graph data: ${response.statusText}`);
    }
    return await response.json();
}

export const api = {
    getAllStories,
    generateStory,
    orchestrateActions,
    getFullGraph,
};