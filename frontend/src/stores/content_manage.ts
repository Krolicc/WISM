
import { ref, computed, watch } from 'vue';
import { defineStore } from 'pinia';
import type { StoryNode, Story } from '../types/index';
import { api } from '../services/api';
import { yjsServiceContent } from '../services/content_yjs_service';

export const useContentManageStore = defineStore('contentManage', () => {
  // --- STATE ---
  const selectedNodeId = ref<string | null>(null); // For selection in UI (e.g. inspector panel)
  const activeNodeId = ref<string | null>(null); // The 'camera' or current point in the timeline
  const activeStoryId = ref<string | null>(null);
  const storiesList = ref<Map<string, Story> | null>(null);

  // --- COMPUTED ---
  const selectedNode = computed((): StoryNode | undefined => {
    if (!selectedNodeId.value) return undefined;

    return yjsServiceContent.collections.nodes.get(selectedNodeId.value);
  });

  const activeStory = computed((): Story | undefined => {
    if (!activeStoryId.value || !storiesList.value) return undefined;

    return storiesList.value.get(activeStoryId.value);
  });

  const activeNode = computed((): StoryNode | undefined => {
    if (!activeNodeId.value) return undefined;

    return yjsServiceContent.collections.nodes.get(activeNodeId.value);
  });

  const stories = computed(() => {
    if (!storiesList.value) return [];
    return Array.from(storiesList.value.values());
  });

  // --- ACTIONS ---
  async function selectNode(nodeId: string | null, isStory: boolean = false) {
    if (isStory) {
      activeStoryId.value = nodeId;
      return;
    }
    selectedNodeId.value = nodeId;

    if (nodeId && activeStoryId.value) {
      const node = yjsServiceContent.collections.nodes.get(nodeId);

      if (node) {
        console.log(`Node ${nodeId} needs hydration. Requesting...`);
        try {
          await api.hydrateNode(activeStoryId.value, nodeId);
          console.log(`Hydration request for node ${nodeId} sent.`);
        } catch (error) {
          console.error(`Failed to hydrate node ${nodeId}:`, error);
        }
      }
    }
  }

  function navigateTo(nodeId: string | null) {
    activeNodeId.value = nodeId;
  }

  function getNode(nodeId: string, isStory: boolean = false): Story | StoryNode | undefined {
    if (!storiesList.value) return undefined;
    return isStory ? storiesList.value.get(nodeId) : yjsServiceContent.collections.nodes.get(nodeId);
  }

  function getNodes(nodeIds: string[], deep: boolean = false): StoryNode[] {
    const initialNodes = nodeIds
        .map(id => getNode(id)) 
        .filter((n): n is StoryNode => n !== undefined);

    if (!deep) {
        return initialNodes;
    }

    return initialNodes.flatMap(node => {
        if (node.type === 'branchSet') {
            return (node.next_ids || [])
                .map(childId => getNode(childId)) 
                .filter((n): n is StoryNode => n !== undefined);
        } else {
            // Otherwise, keep the node itself.
            return [node];
        }
    });
  }

  async function fetchAllStories() {
    // isLoading.value = true;
    // error.value = null;
    try {
      const storyList = await api.getStories(); 
      if (storyList) {
        const storyMap = storyList.reduce((acc, item) => {
          acc.set(item.id, item);
          return acc;
        }, {} as Map<string, Story>);

        storiesList.value = storyMap;
      }
    } catch (e) {
      // error.value = e instanceof Error ? e.message : 'An unknown error occurred.';
    } finally {
      // isLoading.value = false;
    }
  }

  watch(activeStoryId, (newStoryId, oldStoryId) => {
    if (newStoryId) {
      console.log(`Active story changed to ${newStoryId}. Initializing Yjs...`);
      yjsServiceContent.initialize(newStoryId);
    } else if (oldStoryId) {
      // This runs when we navigate away from a story
      console.log(`No active story. Destroying Yjs connection...`);
      yjsServiceContent.destroy();
    }
  });


  return {
    // State
    selectedNodeId,
    activeNodeId,
    activeStoryId,

    // Computed
    stories,
    // Now we can just export the reactive object itself.
    // Components will be able to use it directly.
    nodes: yjsServiceContent.collections.nodes,
    selectedNode,
    activeNode,
    activeStory,

    // Actions
    getNode,
    getNodes,
    selectNode,
    navigateTo,
    fetchAllStories,
  };
});
