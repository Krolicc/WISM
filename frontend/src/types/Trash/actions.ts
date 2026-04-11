
import type { ActionType } from '../lib/action-meta';

// Базовые типы для ясности
type ItemID = string;
type InsertRelation = 'before' | 'after';

// Общий "конверт" для каждого действия
interface BaseAction<T extends ActionType, P> {
  type: T;
  params: P;
}

// -------------------- ДЕЙСТВИЯ --------------------

// 1. Удаление
export type DeleteAction = BaseAction<'delete', {
  id: ItemID;
}>;

// 2. Создание (Ручное)
export type CreateManualAction = BaseAction<'create_manual', {
  content: object; // The actual Frame/Scene object to create
  target_id?: ItemID;
  relation?: InsertRelation;
}>;

// 3. Создание (Генерация)
export type CreateGenerateAction = BaseAction<'create_generate', {
  idea: string;
  flag?: string;
  count?: number;
  target_id?: ItemID;
  relation?: InsertRelation;
}>;

// 4. Перегенерация
export type RegenerateAction = BaseAction<'regenerate', {
  id: ItemID;
  idea: string;
  flag?: string;
  count?: number; // How many versions to generate
}>;

// 5. Переписывание (только текст)
export type RewriteAction = BaseAction<'rewrite', {
  id: ItemID;
  idea: string; // The prompt for rewriting
}>;

// 6. Генерация скелета
export type GenerateSkeletonAction = BaseAction<'generate_skeleton', {
  id: ItemID; // ID of the parent (e.g., Scene to generate Frames for)
  idea?: string;
  count: number;
  isDeep: boolean;
}>;

// 7. Перегенерация скелета
export type RegenerateSkeletonAction = BaseAction<'regenerate_skeleton', {
  id: ItemID; // ID of the parent
  idea?: string;
  count: number;
  isDeep: boolean;
}>;

// 8. Перемещение
export type MoveAction = BaseAction<'move', {
  source_id: ItemID;
  target_id: ItemID;
  relation: InsertRelation;
}>;

// 9. Обновление (прямое редактирование пользователем)
export type UpdateAction = BaseAction<'update', {
  id: ItemID;
  content: object; // A partial object with the fields to update
}>;


// Объединяем все в один тип, чтобы использовать в сторе
export type AppAction =
  | DeleteAction
  | CreateManualAction
  | CreateGenerateAction
  | RegenerateAction
  | RewriteAction
  | GenerateSkeletonAction
  | RegenerateSkeletonAction
  | MoveAction
  | UpdateAction;
