
import { BaseAction, ItemID } from '../base';

// Действие по изменению заголовка узла
export type UpdateTitleAction = BaseAction<'update_title', {
    id: ItemID; // ID узла
    value: string; // Новое значение заголовка
}>;

export type UpdateDescriptionAction = BaseAction<'update_description', {
    id: ItemID; // ID узла
    value: string; // Новое значение описания
}>;