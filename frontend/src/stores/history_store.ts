
import { ref, computed } from 'vue';
import { defineStore } from 'pinia';
import type { Action } from '../types/actions';

// Запись в глобальной истории
export interface HistoryEntry {
  action: Action;
  timestamp: number;
}

// --- Type Guards ---

export const useHistoryStore = defineStore('history', () => {
  // --- STATE ---
  const actionStack = ref<HistoryEntry[]>([]);
  const redoStack = ref<HistoryEntry[]>([]);

  // --- COMPUTED ---

  const log = computed((): Action[] => {
    return actionStack.value.map(entry => entry.action);
  });

  // --- ACTIONS ---

  function dispatch(action: Action) {
    actionStack.value.push({
      action,
      timestamp: Date.now(),
    });
    if (redoStack.value.length > 0) {
      redoStack.value = [];
    }
    console.log(`[History] Action dispatched: ${action.type}`);
  }

  function undo() {
    const lastActionEntry = actionStack.value.pop();
    if (!lastActionEntry) {
      console.log('[History] Nothing to undo.');
      return;
    }
    redoStack.value.push(lastActionEntry);
    console.log(`[History] Undoing action: ${lastActionEntry.action.type}`);
  }

  function redo() {
    const actionToRedo = redoStack.value.pop();
    if (!actionToRedo) {
      console.log('[History] Nothing to redo.');
      return;
    }
    actionStack.value.push(actionToRedo);
    console.log(`[History] Redoing action: ${actionToRedo.action.type}`);
  }

  return {
    log,
    
    // Public methods
    dispatch,
    undo,
    redo,
  };
});
