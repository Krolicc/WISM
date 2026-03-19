
import { ref, computed } from 'vue';
import { defineStore } from 'pinia';
import { api } from '../services/api'; // We will update this API call
import { useNavigationStore } from './navigation';
import { GENERATION_FLAGS } from '../lib/generation-flags'

// --- Type Definitions for Orchestration Actions ---

type ActionType = 'generate' | 'regenerate' | 'delete'

interface BaseAction {
  id: string; // Unique ID for the action itself (e.g., generated with crypto.randomUUID())
  action_type: ActionType;
  level: 'story' | 'chapter' | 'scene' | 'frame';
  // Hierarchical order for sorting execution. Captured at the moment of creation.
  order: { chapter?: number; scene?: number; frame?: number }; 
}

export interface GenerateAction extends BaseAction {
  action_type: 'generate';
  params: {
    parent_id: string;
    idea: string;
    alternative_idea?: string
    count: number;
    before_id?: string; 
    after_id?: string; 
  };
}

export interface RegenerateAction extends BaseAction {
  action_type: 'regenerate';
  params: {
    id: string;
    idea: string; // The new prompt/idea for regeneration
    flag?: string;
  };
}

export interface DeleteAction extends BaseAction {
  action_type: 'delete';
  params: {
    id: string;
  };
}

export type OrchestrationAction = {
  crud: DeleteAction[]
  generate: (GenerateAction | RegenerateAction)[]
};

// --- Store Definition ---

export const useOrchestrationStore = defineStore('orchestration', () => {
  const actions = ref<OrchestrationAction>({
    crud: [],
    generate: [],
  });
  const isProcessing = ref(false);

  const navStore = useNavigationStore();

  // --- Getters / Computed Properties ---

  /**
   * The core of the new logic: sorts actions for predictable execution.
   * 1. Deletions first.
   * 2. Then Inserts and Regenerations, sorted by their hierarchical order.
   * 3. Processes actions to clean up data before sending to the backend.
  */
  const sort_group = (group: (RegenerateAction | GenerateAction | DeleteAction)[]) => {
    const sorted = group.sort((a, b) => {
      if (a.action_type === 'delete' && b.action_type !== 'delete') return -1;
      if (a.action_type !== 'delete' && b.action_type === 'delete') return 1;

      const orderA = a.order;
      const orderB = b.order;

      if (orderA.chapter !== orderB.chapter) return (orderA.chapter ?? 0) - (orderB.chapter ?? 0);
      if (orderA.scene !== orderB.scene) return (orderA.scene ?? 0) - (orderB.scene ?? 0);
      if (orderA.frame !== orderB.frame) return (orderA.frame ?? 0) - (orderB.frame ?? 0);
      return 0;
    });

    return sorted.map(({ id, order, ...rest }) => {
      if (rest.action_type === 'regenerate') {
        const action = rest as RegenerateAction;
        if (action.params && action.params.flag) {
          const { flag, ...paramsWithoutFlag } = action.params;
          const flag_description = GENERATION_FLAGS.find(a => a.id === flag)?.description || flag;

          const updatedParams = {
            ...paramsWithoutFlag,
            idea: `${action.params.idea}. Additional instructions: ${flag_description}`,
          };

          return { ...rest, params: updatedParams };
        }
      } else if (rest.action_type === 'generate') {
        const action = rest as GenerateAction;
        if (action.params && action.params.alternative_idea) {
          const { alternative_idea, ...paramsWithoutAltIdea } = action.params;

          const updatedParams = {
            ...paramsWithoutAltIdea,
            idea: action.params.idea.length === 0 ? alternative_idea : action.params.idea,
          };

          return { ...rest, params: updatedParams };
        }
      }

      return rest;
    });
  }

  const sortedActions = computed(() => {
    return {
      crud: sort_group(actions.value.crud),
      generate: sort_group(actions.value.generate)
    }
  });

  // --- Actions ---

  function isCRUDAction(action_type: string) : 'crud' | 'generate' {
    return ['delete'].includes(action_type) ? 'crud' : 'generate'
  }

  /**
   * Queues an action to be performed.
   */
  function queueAction(action: BaseAction) {
    const action_type = action.action_type
    const group_type = isCRUDAction(action_type)

    // Prevent duplicate actions (e.g., deleting the same item twice)
    if (!actions.value[group_type].some(a => a.id === action.id)) {
      actions.value[group_type].push(action);
    }
  }

  /**
   * Removes an action from the queue.
   */
  function removeAction(index: number, action_type: ActionType) {
    const id = getActionID(index, action_type);
    const group_type = isCRUDAction(action_type)

    actions.value[group_type] = actions.value[group_type].filter(a => a.id !== id);
  }

  /**
   * Clears all pending actions.
   */
  function clearActions() {
    actions.value = {
      crud: [],
      generate: [],
    };
  }

  /**
   * The main function to send the sorted list of actions to the backend.
   */
  async function commitActions() {
    if ((sortedActions.value.crud.length + sortedActions.value.generate.length) === 0) {
      console.log("No actions to commit.");
      return;
    }

    const activeStoryId = navStore.activeStoryId;
    if (!activeStoryId) {
      throw new Error("No active story selected.");
    }

    isProcessing.value = true;
    try {
      // This is the single, powerful API call we're aiming for.
      // We will need to adjust `orchestrateActions` to accept this params.
      await api.orchestrateActions(activeStoryId, sortedActions.value);
      
      // On success, clear the queue.
      clearActions();
      console.log("Orchestration successfully committed.");

    } catch (error) {
      console.error("Failed to commit orchestration actions:", error);
      // Optionally, we could implement retry logic or allow the user to see the error.
      throw error; // Re-throw for the component to handle
    } finally {
      isProcessing.value = false;
    }
  }

  const getActionID = (index: number, type: ActionType): string => {
    const order = getHierarchicalOrder(index);
    let id = '';

    switch (navStore.level) {
      case 'frame': 
        id = `${order.chapter}-${order.scene}-`;
        break;
      case 'scene': 
        id = `${order.chapter}-`;
    }

    id += `${index}-${type}`;

    return id;
  }

  const getAction = (index: number, action_type: ActionType) : DeleteAction | GenerateAction | RegenerateAction | undefined => {
    const id = getActionID(index, action_type);
    const group_type = isCRUDAction(action_type)

    return actions.value[group_type].find(
      a => a.id === id
    );
  }
  
  const isActionQueuedForItem = (itemId: string, action_type: ActionType): boolean => {
    const group_type = isCRUDAction(action_type)

    return actions.value[group_type].some(a => a.params.id === itemId && a.action_type === action_type);
  };
  
  const isNodeInteractive = (index: number): boolean => {
    if (navStore.currentItemList === undefined) return false;
    
    const itemId = navStore.currentItemList[index]?.id;
    return actions.value.generate.some(a => {
      if (a.action_type === 'generate') {
        return a.params.before_id === itemId || a.params.after_id === itemId;
      }
      return a.params.id === itemId;
    });
  };

  // Get the hierarchical order for sorting
  const getHierarchicalOrder = (index: number) => {
    const scene = navStore.activeScene;
    const chapter = navStore.activeChapter;

    switch (navStore.level) {
      case 'frame': return { chapter: chapter?.order, scene: scene?.order, frame: navStore.currentItemList[index]?.order };
      case 'scene': return { chapter: chapter?.order, scene: navStore.currentItemList[index]?.order };
      case 'chapter': return { chapter: navStore.currentItemList[index]?.order };
      default: return {};
    }
  };

  const queueInsertion = (index: number, beforeId?: string, afterId?: string) => {
    const level = navStore.level;
    const beforeItem = beforeId ? navStore.currentItemList.find((i: any) => i.id === beforeId) : undefined;
    const afterItem = afterId ? navStore.currentItemList.find((i: any) => i.id === afterId) : undefined;
    let alternativeIdea = `Нужна ${level}, которая является логическим связующим`;
    if (beforeItem) {
      alternativeIdea += ` после "${beforeItem.title}. ${beforeItem.description}"`;
    }
    if (afterItem) {
      if (beforeItem) {
        alternativeIdea += ' и';
      }
      alternativeIdea += ` перед "${afterItem.title}. ${afterItem.description}"`;
    }
    
    const action: GenerateAction = {
      id: getActionID(index, 'generate'),
      action_type: 'generate',
      level: level,
      order: getHierarchicalOrder(index),
      params: {
        parent_id: navStore.parentId as string,
        idea: '',
        alternative_idea: alternativeIdea,
        count: 1,
        before_id: beforeId,
        after_id: afterId,
      },
    };
    queueAction(action);
  };

  const toggleRegenerateAction = (index: number, itemId: string) => {
    const existingAction = actions.value.generate.find(a => a.params.id === itemId && a.action_type === 'regenerate');
    if (existingAction) {
      removeAction(index, 'regenerate');
    } else {
      removeAction(index, 'delete');

      const itemIndex = navStore.currentItemList.findIndex((i: any) => i.id === itemId);
      const item = navStore.currentItemList[itemIndex]
      const idea = `${item.title}. ${item.description}`

      queueAction({
        id: getActionID(index, 'regenerate'),
        action_type: 'regenerate',
        level: navStore.level,
        order: getHierarchicalOrder(itemIndex),
        params: { id: itemId, idea: idea , flag: 'regenerate' },
      });
    }
  };

  const toggleDeleteAction = (index: number, itemId: string) => {
    const existingAction = actions.value.crud.find(a => a.params.id === itemId && a.action_type === 'delete');
    if (existingAction) {
      removeAction(index, 'delete');
    } else {
      const itemIndex = navStore.currentItemList.findIndex((i: any) => i.id === itemId);
      queueAction({
        id: getActionID(index, 'delete'),
        action_type: 'delete',
        level: navStore.level,
        order: getHierarchicalOrder(itemIndex),
        params: { id: itemId },
      });
    }
  };

  return {
    // State
    actions,
    isProcessing,
    // Getters
    sortedActions,
    // Actions
    getActionID,
    getAction,
    isActionQueuedForItem,
    isNodeInteractive,
    queueAction,
    removeAction,
    clearActions,
    commitActions,
    toggleDeleteAction,
    toggleRegenerateAction,
    queueInsertion,
  };
});
