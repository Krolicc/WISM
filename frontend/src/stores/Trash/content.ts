import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { api } from '../services/api';
import type { Story, EnrichedStoryNode, StoryGraph } from '../types';
import storyStructure from '../example_jsons/story-structure.json';

const CONTEXT_WINDOW_SIZE = 51;

function getEnrichedNodes(graph: StoryGraph): Map<string, EnrichedStoryNode> {
  const enrichedNodes = new Map<string, EnrichedStoryNode>();
  const parentMap = new Map<string, string>();

  // Сначала находим всех родителей
  for (const edge of graph.edges) {
    if (edge.type === 'CONTAINS') {
      parentMap.set(edge.target, edge.source);
    }
  }

  // Затем создаем обогащенные узлы
  for (const node of graph.nodes) {
    enrichedNodes.set(node.id, {
      ...node,
      parent: parentMap.get(node.id) || null,
      branch_info: null, // Для визуального теста это не важно
    });
  }
  return enrichedNodes;
}

export const useContentStore = defineStore('content', () => {
  // --- STATE ---
  const fullGraph: StoryGraph = storyStructure as StoryGraph;
  const rootStoryNode = fullGraph.nodes.find(n => n.type === 'story');

  const stories = ref<Story[]>([rootStoryNode]);

  // Graph-level cache for the active story
  const nodes = ref<Map<string, EnrichedStoryNode>>(getEnrichedNodes(fullGraph));

  const initialContexts = new Map<string, string[]>();
  if (rootStoryNode) {
    initialContexts.set(rootStoryNode.id, ['S1', 'A1', 'A2', 'BSA1', 'A5']);
  }
  const contexts = ref<Map<string, string[]>>(initialContexts);

  // UI State
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  // --- GETTERS ---
  function getNode(id: string): EnrichedStoryNode | undefined {
    return nodes.value.get(id);
  }

  function getContextForNode(id: string): string[] | undefined {
    return contexts.value.get(id);
  }

  function getParentOfNode(id: string): EnrichedStoryNode | undefined {
    const node = nodes.value.get(id);
    if (!node || !node.parent) return undefined;
    return nodes.value.get(node.parent);
  }

  // --- PRIVATE HELPERS ---

  function _clearGraphCache() {
    nodes.value.clear();
    contexts.value.clear();
  }

  function _normalizeAndCache(contextNodes: EnrichedStoryNode[], centerNodeId: string) {
    for (const node of contextNodes) {
      nodes.value.set(node.id, node);
    }
    const ids = contextNodes.map(node => node.id);
    contexts.value.set(centerNodeId, ids);
  }

  // --- ACTIONS ---

  // Story Management Actions

  async function fetchAllStories() {
    isLoading.value = true;
    error.value = null;
    try {
      const storyList = await api.getStoryList(); // Assuming an endpoint to get just story metadata
      if (storyList) {
        stories.value = storyList;
      }
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'An unknown error occurred.';
    } finally {
      isLoading.value = false;
    }
  }

  async function createAndGenerateStory(prompt: string) {
    isLoading.value = true;
    error.value = null;
    try {
      const newStory = await api.generateStory(prompt);
      if (newStory) {
        stories.value.push(newStory);
        await setActiveStory(newStory.id);
      }
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'An unknown error occurred.';
    } finally {
      isLoading.value = false;
    }
  }

  // Graph/Context Actions

  async function fetchContext(nodeId: string, options: { force?: boolean } = {}) {
    // if (contexts.value.has(nodeId) && !options.force) {
    //   return;
    // }

    // isLoading.value = true;
    // error.value = null;

    // try {
    //   const contextData = await api.getSimulatedContext(nodeId, CONTEXT_WINDOW_SIZE);
    //   if (contextData) {
    //     _normalizeAndCache(contextData, nodeId);
    //   }
    // } catch (e) {
    //   error.value = e instanceof Error ? e.message : 'An unknown error occurred.';
    // } finally {
    //   isLoading.value = false;
    // }
  }

  function updateNode(updatedNode: EnrichedStoryNode) {
    nodes.value.set(updatedNode.id, updatedNode);
  }

  return {
    // State
    stories,
    nodes,
    contexts,
    isLoading,
    error,
    // Getters
    getNode,
    getContextForNode,
    getParentOfNode,
    // Actions
    fetchAllStories,
    createAndGenerateStory,
    fetchContext,
    updateNode,
  };
});