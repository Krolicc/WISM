
import { ref, computed } from 'vue';
import { defineStore } from 'pinia';
import { api } from '../services/api';
import { useContentManageStore } from './content_manage';
import { GENERATION_FLAGS } from '../lib/generation-flags';

// --- Type Definitions ---
type ActionType = 'generate' | 'regenerate' | 'delete';
export type StoryLevel = 'arc' | 'chapter' | 'scene';

interface BaseAction {
  action_type: ActionType;
  level: StoryLevel;
}

export interface GenerateAction extends BaseAction {
  action_type: 'generate';
  params: {
    parent_id: string;
    idea: string;
    alternative_idea?: string;
    count: number;
    id?: string;
    is_before: boolean;
  };
}

export interface RegenerateAction extends BaseAction {
  action_type: 'regenerate';
  params: { id: string; idea: string; flag?: string; };
}

export interface DeleteAction extends BaseAction {
  action_type: 'delete';
  params: { id: string; };
}

export type OrchestrationAction = GenerateAction | RegenerateAction | DeleteAction;
export type ApiPayload = { crud: DeleteAction[]; generate: (GenerateAction | RegenerateAction)[]; };

// --- Store Definition ---
export const useOrchestrationStore = defineStore('orchestration', () => {
  const actions = ref(new Map<string, OrchestrationAction[]>());
  const isProcessing = ref(false);
  const contentStore = useContentManageStore();

  // --- Private Helpers ---
  const _addAction = (key: string, action: OrchestrationAction) => {
    const existing = actions.value.get(key) || [];
    if (existing.some(a => a.action_type === action.action_type)) return;
    actions.value.set(key, [...existing, action]);
  };

  const _removeAction = (key: string, action_type: ActionType) => {
    const existing = actions.value.get(key);
    if (!existing) return;
    const filtered = existing.filter(a => a.action_type !== action_type);
    if (filtered.length > 0) actions.value.set(key, filtered);
    else actions.value.delete(key);
  };

  // --- Getters / Computed ---
  const preparedActions = computed((): ApiPayload => {
    const allActions = [...actions.value.values()].flat();
    const crud = allActions.filter(a => a.action_type === 'delete') as DeleteAction[];
    let generate = allActions.filter(a => a.action_type !== 'delete') as (GenerateAction | RegenerateAction)[];

    generate = generate.map(action => {
      if (action.action_type === 'regenerate' && action.params.flag) {
        const { flag, ...params } = action.params;
        const flagDesc = GENERATION_FLAGS.find(f => f.id === flag)?.description || flag;
        return { ...action, params: { ...params, idea: `${params.idea}. Additional instructions: ${flagDesc}` } };
      } else if (action.action_type === 'generate' && action.params.alternative_idea) {
        const { alternative_idea, ...params } = action.params;
        return { ...action, params: { ...params, idea: params.idea || alternative_idea } };
      }
      return action;
    });
    return { crud, generate };
  });

  // --- Public API ---
  const getAction = (key: string, action_type: ActionType) => actions.value.get(key)?.find(a => a.action_type === action_type);
  const isActionQueuedForItem = (itemId: string, action_type: ActionType) => !!getAction(itemId, action_type);
  const isNodeInteractive = (itemId: string) => actions.value.has(itemId);
  const clearActions = () => actions.value.clear();

  const toggleDeleteAction = (itemId: string, itemLevel: StoryLevel) => {
    if (isActionQueuedForItem(itemId, 'delete')) {
      _removeAction(itemId, 'delete');
    } else {
      _removeAction(itemId, 'regenerate');
      _addAction(itemId, { action_type: 'delete', level: itemLevel, params: { id: itemId } });
    }
  };

  const toggleRegenerateAction = (itemId: string, itemData: { title: string; description: string; level: StoryLevel; }) => {
    if (isActionQueuedForItem(itemId, 'regenerate')) {
      _removeAction(itemId, 'regenerate');
    } else {
      _removeAction(itemId, 'delete');
      _addAction(itemId, {
        action_type: 'regenerate',
        level: itemData.level,
        params: { id: itemId, idea: `${itemData.title}. ${itemData.description}`, flag: 'regenerate' },
      });
    }
  };

  const toggleGenerateAction = (options: { parentId: string; level: StoryLevel; beforeId?: string; }) => {
    const key = options.beforeId ?? options.parentId;
    if (getAction(key, 'generate')) {
      _removeAction(key, 'generate');
    } else {
      let alternativeIdea = `A logical new ${options.level}`;
      const beforeNode = contentStore.getNode(options.beforeId || '');
      if (beforeNode) {
        alternativeIdea += ` that comes after "${beforeNode.title}"`
        const parentContext = contentStore.getContext(beforeNode.parent || '') || [];
        const afterNodeId = parentContext[parentContext.indexOf(beforeNode.id) + 1];
        if (afterNodeId) {
          const afterNode = contentStore.getNode(afterNodeId);
          if(afterNode) alternativeIdea += ` and before "${afterNode.title}"`;
        }
      }
      _addAction(key, {
        action_type: 'generate', level: options.level,
        params: { parent_id: options.parentId, idea: '', alternative_idea: alternativeIdea, count: 1, before_id: options.beforeId }
      });
      _removeAction(key, 'delete'); // Cannot insert relative to a node that is being deleted
    }
  };

  const commitActions = async (storyId: string) => {
    if (actions.value.size === 0) return;
    if (!storyId) throw new Error("No active story selected.");
    isProcessing.value = true;
    try {
      await api.orchestrateActions(storyId, preparedActions.value);
      clearActions();
    } finally {
      isProcessing.value = false;
    }
  };

  return {
    actions, isProcessing, preparedActions,
    getAction, isActionQueuedForItem, isNodeInteractive,
    clearActions, commitActions,
    toggleDeleteAction, toggleRegenerateAction, toggleGenerateAction
  };
});
