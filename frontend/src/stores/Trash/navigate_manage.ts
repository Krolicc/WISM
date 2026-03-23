import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useContentManageStore } from './content_manage';

type Level = 'story'|'arc'|'chapter'|'scene'|'frame'|'graph';

// This map defines the default "drill down" behavior.
const childLevelMap: Record<string, Level> = {
    story: 'arc',
    arc: 'chapter',
    chapter: 'scene',
    scene: 'frame',
};

export const useNavigationManageStore = defineStore('navigation_manage', () => {
  const contentStore = useContentManageStore();

  // --- STATE ---
  const activeHierarchy = ref<string[]>([]);
  const isNavigating = ref(false); 
  const viewingLevel = ref<Level>('story');

  // --- GETTERS ---
  const activeNodeId = computed(() => activeHierarchy.value.at(-1) || null);
  const activeNode = computed(() => activeNodeId.value ? contentStore.getNode(activeNodeId.value) : null);
  const breadcrumbs = computed(() => activeHierarchy.value.map(id => contentStore.getNode(id)).filter(Boolean));

  // --- PRIVATE HELPERS ---
  function isLevelDisabled(level: string): boolean {
    switch (level) {
        case 'arc':
        case 'chapter':
            return !breadcrumbs.value.some(node => node.type === 'story');
        case 'scene':
            return !breadcrumbs.value.some(node => node.type === 'chapter');
        case 'frame':
            return !breadcrumbs.value.some(node => node.type === 'scene');
        default:
            return false;
    }
  }

  // --- ACTIONS ---

  async function initialize(storyId: string) {
    isNavigating.value = true;
    await contentStore.fetchContext(storyId);
    activeHierarchy.value = [storyId];
    viewingLevel.value = 'story';
    isNavigating.value = false;
  }

  async function navigateToNode(nodeId: string) {
    if (activeNodeId.value === nodeId) return;
    isNavigating.value = true;

    const hierarchy = await contentStore.getHierarchyForNode(nodeId);

    await contentStore.fetchContext(nodeId);

    if (hierarchy.length > 0) {
      activeHierarchy.value = hierarchy;
      const targetNode = contentStore.getNode(nodeId);
      if (targetNode) {
        viewingLevel.value = targetNode.type as any;
      }
    } else {
      console.error(`Could not determine hierarchy for nodeId: ${nodeId}`);
    }
    isNavigating.value = false;
  }

  function navigateUp() {
    if (activeHierarchy.value.length > 1) {
      activeHierarchy.value.pop();
      if(activeNode.value) viewingLevel.value = activeNode.value.type as any;
    }
  }

  async function navigateDown() {
    if (!activeNodeId.value || !activeNode.value?.hasChildren) return;

    isNavigating.value = true;
    const firstChildId = await contentStore.findFirstChildId(activeNodeId.value);

    if (firstChildId) {
      activeHierarchy.value.push(firstChildId);
      const childNode = contentStore.getNode(firstChildId);
      if(childNode) viewingLevel.value = childNode.type as any;
    } 
    isNavigating.value = false;
  }

  function navigateToLevel(level: Level) {
    viewingLevel.value = level;
    const targetNodeIndex = breadcrumbs.value.map(n => n.type).lastIndexOf(level);
    if (targetNodeIndex > -1) {
        activeHierarchy.value = activeHierarchy.value.slice(0, targetNodeIndex + 1);
    }
  }

  /**
   * Universal action to "drill down" into a node.
   * It sets the node as the active context and prepares to show its children.
   */
  async function drillDown(nodeId: string) {
    // 1. Set the full hierarchy for the selected node.
    await navigateToNode(nodeId);

    // 2. Determine the type of children to display.
    const parentNode = activeNode.value;
    if (parentNode && parentNode.type in childLevelMap) {
      const childLevel = childLevelMap[parentNode.type];
      // 3. Set the viewing level to the child type.
      navigateToLevel(childLevel);
    }
  }

  return {
    activeHierarchy,
    isNavigating,
    activeNodeId,
    activeNode,
    breadcrumbs,
    viewingLevel,
    initialize,
    navigateToNode,
    navigateUp,
    navigateDown,
    isLevelDisabled,
    navigateToLevel,
    drillDown,
  };
});
