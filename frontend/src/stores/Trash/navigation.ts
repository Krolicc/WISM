import { defineStore } from 'pinia';
import { computed, ref } from 'vue';
import { useContentStore } from './content';
import type { EnrichedStoryNode } from '../types';

export const useNavigationStore = defineStore('navigation', () => {
  const contentStore = useContentStore();

  // --- STATE ---

  /**
   * The single source of truth for "where" the user is.
   * It stores the ID of the node currently in focus.
   */
  const activeNodeId = ref<string | null>(null);

  /**
   * The active view mode, kept for UI control (e.g., sidebar buttons).
   * Can be updated automatically by navigation or set manually.
   */
  const level = ref<'story' | 'arc' | 'chapter' | 'scene' | 'frame' | 'graph'>('story');

  // --- GETTERS ---

  /**
   * The full, enriched object for the currently active node.
   * Fetches the node directly from the content store's cache.
   */
  const activeNode = computed((): EnrichedStoryNode | null => {
    if (!activeNodeId.value) return null;
    return contentStore.nodes.get(activeNodeId.value) || null;
  });

  /**
   * The list of nodes to be displayed in the main timeline view.
   * It gets the context for the active node from the content store.
   */
  const currentTimeline = computed((): EnrichedStoryNode[] => {
    if (!activeNode.value) return [];

    const contextIds = contentStore.getContextForNode(activeNode.value.id);
    if (!contextIds) return [];

    // Map IDs to full node objects from the master node map
    return contextIds
      .map(id => contentStore.nodes.get(id))
      .filter(Boolean) as EnrichedStoryNode[];
  });

  /**
   * The breadcrumb trail, calculated by walking up the parent chain from the active node.
   */
  const breadcrumbs = computed((): EnrichedStoryNode[] => {
    const trail: EnrichedStoryNode[] = [];
    let currentNode = activeNode.value;

    while (currentNode) {
      trail.unshift(currentNode);
      currentNode = contentStore.getParentOfNode(currentNode.id);
    }
    return trail;
  });


  // --- ACTIONS ---
  const navigateStoryLevel = (new_level: 'story' | 'arc' | 'chapter' | 'scene' | 'frame' | 'graph') => {
    
    
    level.value = new_level;
  }

  async function navigateToNode(nodeId: string | null) {
    if (!nodeId) return;
    
    activeNodeId.value = nodeId;
    await contentStore.fetchContext(activeNodeId.value);

    // Automatically update the UI level based on the new node's type
    const newNode = activeNode.value;
    if (newNode?.type) {
      const type = newNode.type.toLowerCase();

      switch (type) {
        case 'story':
          level.value = 'arc';
          break;

        case 'arc':
          level.value = 'chapter';
          break;

        case 'chapter':
          level.value = 'scene';
          break;
        
        case 'scene':
          break;
        
        default:
          break;
      }
    }
  }

  /**
   * Directly sets the view level, for UI controls like the sidebar.
   * @param newLevel The new level to set.
   */
  function setLevel(newLevel: 'story' | 'arc' | 'chapter' | 'scene' | 'frame' | 'graph') {
    level.value = newLevel;
  }

  /**
   * Initializes the store by navigating to the root node of the story.
   */
  async function initialize() {
    await navigateToNode(contentStore.rootNodeId);
  }

  return {
    // State
    activeNodeId,
    level,
    // Getters
    activeNode,
    currentTimeline,
    breadcrumbs,
    // Actions
    navigateStoryLevel,
    navigateToNode,
    setLevel,
    initialize,
  };
});