
import { BaseAction, ItemID } from '../base';

export type UpdateTitleAction = BaseAction<'update_title', {
    id: ItemID; // ID фрейма
    value: string; // Новое значение заголовка
}>;

export type UpdateDescriptionAction = BaseAction<'update_description', {
    id: ItemID; // ID фрейма
    value: string; // Новое значение описания
}>;

export type UpdateDetailedPromptAction = BaseAction<'update_detailed_prompt', {
    id: ItemID; // ID фрейма
    value: object; // Новое значение детального промпта (объект)
}>;
