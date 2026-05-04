import type { AppAction, UpdateAction } from '@/types/actions';

interface LogEntry {
  id: string;
  action: AppAction;
  isCancelled: boolean;
}

function getActionEntityId(entry: LogEntry): string | null {
  const { action, id: entryId } = entry;

  if (action.type === 'create_manual' || action.type === 'create_generate') {
    return entryId;
  }

  const { params } = action as any;

  if (action.type === 'move') {
    return params.source_id ?? null;
  }

  return params.id ?? null;
}

/**
 * `ReAction` - это действия, связанные с регенерацией контента.
 * Они не влияют на `update` и наоборот.
 */
function isReAction(type: string): boolean {
  const reActionTypes: AppAction['type'][] = [
    'regenerate',
    'rewrite',
    'generate_skeleton',
    'regenerate_skeleton'
  ];
  return reActionTypes.includes(type as AppAction['type']);
}

export class ActionResolver {
  private readonly actionGroups = new Map<string, LogEntry[]>();

  public addEntry(entry: LogEntry): void {
    const key = getActionEntityId(entry);
    if (!key) return;

    if (!this.actionGroups.has(key)) {
      this.actionGroups.set(key, []);
    }
    this.actionGroups.get(key)!.push(entry);
  }

  public getFinalPlan(): AppAction[] {
    const finalActions: AppAction[] = [];
    for (const group of this.actionGroups.values()) {
      const resolved = this.resolveGroup(group);
      finalActions.push(...resolved);
    }
    return finalActions;
  }

  private resolveGroup(group: LogEntry[]): AppAction[] {
    const effectiveEntries = group.filter(entry => !entry.isCancelled);
    if (effectiveEntries.length === 0) {
      return [];
    }

    // Группы с create_* действиями изолированы и просты.
    if (effectiveEntries[0].action.type.startsWith('create_')) {
      return [effectiveEntries[effectiveEntries.length - 1].action];
    }

    const effectiveActions = effectiveEntries.map(entry => entry.action);

    // Три независимых трека для каждого типа состояний
    let trackUpdate: UpdateAction | null = null;
    let trackReAction: AppAction | null = null;
    let trackDelete: AppAction | null = null;

    for (const currentAction of effectiveActions) {
      if (currentAction.type === 'update') {
        // Правило: update (О) update -> сливаем данные
        if (!trackUpdate) {
          trackUpdate = currentAction;
        } else {
          const mergedContent = { ...trackUpdate.params.content, ...currentAction.params.content };
          trackUpdate = { ...currentAction, params: { ...currentAction.params, content: mergedContent } };
        }
        // Правило: update (П) delete -> "воскрешаем" сущность
        trackDelete = null;
      } 
      else if (isReAction(currentAction.type)) {
        // Правило: ReAction (П) ReAction -> последний побеждает
        trackReAction = currentAction;
        // Правило: ReAction (П) delete -> "воскрешаем" регенерацией
        trackDelete = null;
      } 
      else if (currentAction.type === 'delete') {
        // Правило: delete (П) всё остальное
        trackDelete = currentAction;
        trackUpdate = null;
        trackReAction = null;
      } 
      else {
        // Для остальных, как 'move', применяем простое перекрытие.
        // Они сбрасывают все, кроме delete (если delete был последним).
        if (!trackDelete) {
            trackUpdate = null;
            trackReAction = currentAction;
        }
      }
    }

    // Собираем итоговый результат из треков
    if (trackDelete) {
      return [trackDelete];
    }
    
    return [trackUpdate, trackReAction].filter((a): a is AppAction => a !== null);
  }
}
