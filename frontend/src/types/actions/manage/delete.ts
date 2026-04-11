
import { BaseAction, ItemID } from '../base';

// Семантическое действие: Удаление Фрейма
export type DeleteNodeAction = BaseAction<'delete_node', {
  // ID фрейма, который нужно удалить
  id: ItemID;
}>;
