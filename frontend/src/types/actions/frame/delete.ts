
import { BaseAction, ItemID } from '../base';

// Семантическое действие: Удаление Фрейма
export type DeleteFrameAction = BaseAction<'delete_frame', {
  // ID фрейма, который нужно удалить
  id: ItemID;
}>;
