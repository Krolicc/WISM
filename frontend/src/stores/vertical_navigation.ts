
import { ref, computed, watch } from 'vue';
import { defineStore } from 'pinia';
import { useContentManageStore } from './content_manage';
import { BaseNode, Story } from '../types/index'

// Defines the available levels for hierarchical navigation.
export type VerticalLevel = 'story' | 'arc' | 'chapter' | 'scene' | 'frame';

// This map defines the default "drill down" behavior.
const childLevelMap: Partial<Record<VerticalLevel, VerticalLevel>> = {
    story: 'arc',
    arc: 'chapter',
    chapter: 'scene',
    scene: 'frame',
};

const levelRanks: Record<VerticalLevel, number> = {
    story: 4,
    arc: 3,
    chapter: 2,
    scene: 1,
    frame: 0,
};


// This store manages the user's position within the story's hierarchy (vertical navigation).
export const useVerticalNavigationStore = defineStore('verticalNavigation', () => {
  const contentStore = useContentManageStore();

  // --- STATE ---
  // A stack of node IDs representing the path from the story root to the currently focused node.
  const activeHierarchy = ref<string[]>([]);
  // The level of children the UI should be trying to display.
  const viewingLevel = ref<VerticalLevel>('story');

  // --- GETTERS (COMPUTED) ---

  const activeNodeId = computed(() => activeHierarchy.value.at(-1) || null);
  const activeNode = computed((): BaseNode | Story | null => {
    const isStory = activeNodeId.value == activeHierarchy.value.at(0)
    return activeNodeId.value ? contentStore.getNode(activeNodeId.value, isStory) as BaseNode | Story : null
  });
  const breadcrumbs = computed(() => {
    if (activeHierarchy.value.length == 0) return [];
    const nodeIds = activeHierarchy.value.slice(0);
    const nodes = contentStore.getNodes(nodeIds);
    return [contentStore.getNode(activeHierarchy.value[0], true)].concat(nodes)
  });
  
  const currentChildren = computed(() => {
    if (!activeNode.value) return [];
    return contentStore.getNodes(activeNode.value.children_ids);
  });

  // --- ACTIONS ---

  function _updateViewingLevel() {
      if (activeNode.value && activeNode.value.type in childLevelMap) {
          viewingLevel.value = childLevelMap[activeNode.value.type as VerticalLevel]!;
      } else if (activeNode.value) {
          viewingLevel.value = activeNode.value.type as VerticalLevel;
      }
  }

  function initialize(hierarchy: string[]) {
    activeHierarchy.value = hierarchy;
    contentStore.selectNode(activeHierarchy.value.at(-1) || null);
    _updateViewingLevel();
  }

  function drillDown(nodeId: string, isStory: boolean = false) {
    const node = contentStore.getNode(nodeId, isStory) as BaseNode
    
    activeHierarchy.value.push(nodeId);
    contentStore.selectNode(nodeId, isStory);
    
    contentStore.navigateTo(node?.children_ids[0] || null);

    _updateViewingLevel();
  }

  /**
   * Navigates up the hierarchy.
   * If nodeId is provided, it will navigate up to that specific node in the breadcrumbs.
   * If no nodeId is provided, it will navigate up one level.
   */
  function navigateUp(nodeId?: string) {
    const targetIndex = nodeId ? activeHierarchy.value.indexOf(nodeId) : activeHierarchy.value.length - 2;

    if (targetIndex > -1) {
      activeHierarchy.value = activeHierarchy.value.slice(0, targetIndex + 1);
    } else if (!nodeId && activeHierarchy.value.length > 1) {
      activeHierarchy.value.pop();
    }

    contentStore.selectNode(activeHierarchy.value.at(-1) || null);
    _updateViewingLevel();
  }
  
  /**
   * Sets the viewing level and syncs the hierarchy to match.
   * e.g., if viewing 'scene' and set to 'arc', pops hierarchy back to the last arc.
   */
  function setViewingLevel(level: VerticalLevel) {
    viewingLevel.value = level;
    
    const targetNodeIndex = breadcrumbs.value.map(n => n.type).lastIndexOf(level);

    if (targetNodeIndex > -1) {
        const newHierarchy = activeHierarchy.value.slice(0, targetNodeIndex + 1);
        if(JSON.stringify(newHierarchy) !== JSON.stringify(activeHierarchy.value)) {
            activeHierarchy.value = newHierarchy;
            contentStore.selectNode(activeHierarchy.value.at(-1) || null);
        }
    }
  }

  const isLevelDisabled = (level: VerticalLevel): boolean => {
    if (!activeNode.value) {
        return level !== 'story';
    }
    const activeNodeRank = levelRanks[activeNode.value.type as VerticalLevel];
    const targetLevelRank = levelRanks[level];
    return targetLevelRank < activeNodeRank - 1;
  };

  watch(viewingLevel, (newLevel, oldLevel) => {
    if (!oldLevel || newLevel === oldLevel) return;
    let targetNodeId: string | null = null;

    const existingNode = breadcrumbs.value.find(n => n.type === newLevel);
    
    if (existingNode) {
      targetNodeId = existingNode.id;
    } else {
      targetNodeId = activeNode.value?.children_ids?.[0] || null;
    }

    if (targetNodeId !== activeNodeId.value) {
      contentStore.navigateTo(targetNodeId);
    }
  });
  
  return {
    // State
    activeHierarchy,
    viewingLevel,

    // Computed
    activeNodeId,
    activeNode,
    breadcrumbs,
    currentChildren,

    // Actions
    initialize,
    drillDown,
    navigateUp,
    setViewingLevel,
    isLevelDisabled
  };
});
