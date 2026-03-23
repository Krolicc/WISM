
import { ref, computed } from 'vue';
import { defineStore } from 'pinia';
// import { api } from '../services/api';
import { AppAction } from '../types/actions';
import { ActionResolver } from '../lib/ActionResolver';
import { useHistoryStore } from './history_store';

// --- Типы и Константы ---

export interface LogEntry {
  id: string; 
  action: AppAction;
  isCancelled: boolean;
}

const getActionId = (action: AppAction): string | null => {
    if ('id' in action.params) return action.params.id;
    if ('source_id' in action.params) return action.params.source_id;
    if ((action.type === 'create_manual' || action.type === 'create_generate') && action.params.target_id) {
        return action.params.target_id;
    }
    return null;
}

export const useOrchestrationManageStore = defineStore('orchestration_manage', () => {
    const historyStore = useHistoryStore(); 
    const log = ref<LogEntry[]>([]);
    const isProcessing = ref(false);

    const executablePlan = computed((): AppAction[] => {
        const resolver = new ActionResolver();

        for (const entry of log.value) {
            resolver.addEntry(entry);
        }
        return resolver.getFinalPlan();
    });

    const lastLogEntry = computed((): LogEntry | undefined => {
        return [...log.value].reverse().find(e => !e.isCancelled);
      });

    // --- API для управления логом --- 

    const dispatchAction = (action: AppAction) => {
        const entry: LogEntry = {
            id: crypto.randomUUID(),
            action: action,
            isCancelled: false,
        };
        log.value.push(entry);

        historyStore.pushToActionHistory(action, 'manage');

        return entry.id; 
    };

    const updateActionParams = (entryId: string, newParams: Partial<AppAction['params']>) => {
        const entryToUpdate = log.value.find(e => e.id === entryId);
        if (!entryToUpdate) return;

        if (lastLogEntry.value?.id === entryId) {
            entryToUpdate.action.params = { ...entryToUpdate.action.params, ...newParams };
        } else {
            const newAction = { 
                ...entryToUpdate.action, 
                params: { ...entryToUpdate.action.params, ...newParams }
            };
            dispatchAction(newAction);
        }
    };

    const cancelAction = (entryId: string, options?: { silent: boolean }) => {
        const entry = log.value.find(e => e.id === entryId);
        if (entry) entry.isCancelled = true;
        
        if (!options?.silent) {
            // Если отмена - это осмысленное действие, ее тоже можно логировать
            // Но пока что для UNDO мы это опустим, чтобы избежать циклов
        }
    };

    const redoAction = (entryId: string) => {
        const entry = log.value.find(e => e.id === entryId);
        if (entry) entry.isCancelled = false;
    };

    const undoLastAction = () => {
        if (lastLogEntry.value) cancelAction(lastLogEntry.value.id, { silent: true });
    };

    const undoAction = (actionToUndo: AppAction) => {
        // Находим соответствующую запись в логе по самому объекту действия
        // Это не очень надежно, если действия могут быть идентичными.
        // Более надежный способ - отменять ПОСЛЕДНЕЕ действие.
        const lastEntry = lastLogEntry.value;
        if (lastEntry && !lastEntry.isCancelled) {
            console.log(`[manage] Undoing last action: ${lastEntry.action.type}`);
            cancelAction(lastEntry.id, { silent: true }); // silent, т.к. history_store уже знает об этом
        } else {
            console.warn(`[manage] Could not find action to undo.`);
        }
    };

    const clearLog = () => {
        log.value = [];
    };

    const commitActions = async (storyId: string) => {
        const plan = executablePlan.value;
        if (plan.length === 0) return;
        if (!storyId) throw new Error("Не выбрана активная история.");

        isProcessing.value = true;
        try {
            console.log('Отправка на сервер вычисленного плана:', JSON.parse(JSON.stringify(plan)));
            // await api.orchestrateActions(storyId, plan);
            clearLog();
        } finally {
            isProcessing.value = false;
        }
    };

    // --- Геттеры для UI ---

    const getFinalActionForId = (itemId: string, options?: { includeCancelled: boolean }) => {
        const includeCancelled = options?.includeCancelled || false;
        return [...log.value].reverse().find(e => 
            (includeCancelled || !e.isCancelled) && 
            getActionId(e.action) === itemId
        );
    };

    const getFinalActionForIdByTypes = (itemId: string, types: AppAction['type'][], options?: { includeCancelled: boolean }) => {
        const includeCancelled = options?.includeCancelled || false;
        return [...log.value].reverse().find(e => 
            (includeCancelled || !e.isCancelled) &&
            getActionId(e.action) === itemId &&
            types.includes(e.action.type)
        );
    };

    const isActionQueued = (itemId: string, actionType: AppAction['type']) => {
        const finalAction = getFinalActionForId(itemId);
        return finalAction?.action.type === actionType;
    };

    return {
        log,
        executablePlan,
        isProcessing,
        lastLogEntry,
        dispatchAction,
        updateActionParams,
        cancelAction,
        redoAction,
        undoAction,
        isActionQueued,
        getFinalActionForId,
        getFinalActionForIdByTypes,
        clearLog,
        commitActions,
    };
});
