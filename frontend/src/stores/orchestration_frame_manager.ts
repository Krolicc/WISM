
import { ref, computed } from 'vue';
import { defineStore } from 'pinia';
import { FrameAction, CreateFrameAction, UpdateFrameAction } from '../types/frame_actions';
import { useHistoryStore } from './history_store';

// --- Типы и Константы ---

export interface FrameLogEntry {
  id: string;
  action: FrameAction;
  isCancelled: boolean;
}

const getActionId = (action: FrameAction): string => {
    return action.params.id;
}

// Определяем типы действий, которые перезаписывают друг друга
export const useOrchestrationFrameManagerStore = defineStore('orchestration_frame_manager', () => {
    const historyStore = useHistoryStore(); // Инициализируем
    const log = ref<FrameLogEntry[]>([]);
    const isProcessing = ref(false); // Для будущих API вызовов

    /**
     * Вычисляемый "план к выполнению".
     * 1. Отфильтровывает отмененные действия (undo).
     * 2. Разрешает конфликты, оставляя только финальное действие для каждого ID кадра.
     */
    const executablePlan = computed((): FrameAction[] => {
        const activeEntries = log.value.filter(e => !e.isCancelled);
        const finalActionMap = new Map<string, FrameAction>();

        for (const entry of activeEntries) {
            const action = entry.action;
            const id = getActionId(action);

            const existingAction = finalActionMap.get(id);

            // Логика разрешения конфликтов
            if (action.type === 'delete') {
                finalActionMap.set(id, action); // Удаление всегда имеет приоритет
                continue;
            }

            if (existingAction?.type === 'delete') {
                // Если объект был удален, а потом создается заново (редко, но возможно), 
                // то новое действие заменяет удаление.
                finalActionMap.set(id, action);
                continue;
            }
            
            // Если для одного ID есть несколько действий, они схлопываются
            if (action.type === 'update_frame' && existingAction?.type === 'update_frame') {
                // Мержим content из нескольких update'ов
                const mergedContent = { ...existingAction.params.content, ...action.params.content };
                const mergedAction: UpdateFrameAction = { ...existingAction, params: { ...existingAction.params, content: mergedContent } };
                finalActionMap.set(id, mergedAction);
                continue;
            }

            // Для всех остальных случаев (create, или первый update) - просто устанавливаем действие
            finalActionMap.set(id, action);
        }

        return Array.from(finalActionMap.values());
    });

    const lastLogEntry = computed((): FrameLogEntry | undefined => {
        return [...log.value].reverse().find(e => !e.isCancelled);
    });

    // --- API для управления логом --- 

    const dispatchAction = (action: FrameAction) => {
        const entry: FrameLogEntry = {
            id: crypto.randomUUID(), // ID для самой записи лога
            action: action,
            isCancelled: false,
        };
        log.value.push(entry);
        historyStore.pushToActionHistory(action, 'frame');
        return entry.id; 
    };

    const cancelAction = (entryId: string, options?: { silent: boolean }) => {
        const entry = log.value.find(e => e.id === entryId);
        if (entry) entry.isCancelled = true;
    };

    const undoLastAction = () => {
        if (lastLogEntry.value) cancelAction(lastLogEntry.value.id, { silent: true });
    };

    const undoAction = (actionToUndo: FrameAction) => {
        const lastEntry = lastLogEntry.value;
        if (lastEntry && !lastEntry.isCancelled) {
            console.log(`[frame] Undoing last action: ${lastEntry.action.type}`);
            cancelAction(lastEntry.id, { silent: true });
        } else {
            console.warn(`[frame] Could not find action to undo.`);
        }
    };

    const clearLog = () => {
        log.value = [];
    };


    // --- Геттеры для UI и других сторов ---

    const getFinalActionForId = (itemId: string) => {
        return executablePlan.value.find(action => getActionId(action) === itemId);
    };

    return {
        log,
        executablePlan,
        isProcessing,
        lastLogEntry,
        dispatchAction,
        cancelAction,
        undoAction,
        getFinalActionForId,
        clearLog,
    };
});
