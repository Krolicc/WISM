
import { Frame } from './index';
import { DeleteAction } from './actions';

// Базовый тип для ID, чтобы было чисто
type ItemID = string;

// Общий "конверт", аналогичный тому, что в actions.ts
interface BaseAction<T extends string, P> {
  type: T;
  params: P;
}

// -------------------- ДЕЙСТВИЯ, СПЕЦИФИЧНЫЕ ДЛЯ КАДРОВ --------------------

// 1. Создание Кадра (из текста)
export type CreateFrameAction = BaseAction<'create_frame', {
    id: ItemID; // Временный, клиентский ID для отслеживания
    scene_id: ItemID; // ID родительской сцены, к которой он будет привязан
    prompt: string;
    source_text_range: { start: number; end: number };
}>;

// 2. Обновление Кадра
export type UpdateFrameAction = BaseAction<'update_frame', {
    id: ItemID;
    content: Partial<Omit<Frame, 'id' | 'type'>>;
}>;


// Объединяем все действия, связанные с кадрами, в один тип
// Он будет использоваться в новом orchestration_frame_manager
export type FrameAction =
    | CreateFrameAction
    | UpdateFrameAction
    | DeleteAction; // Переиспользуем универсальное действие удаления из глобальных actions
