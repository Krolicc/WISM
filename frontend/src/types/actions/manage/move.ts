
import { BaseAction, ItemID } from '../base';

// Действие по перемещению узла
export type MoveNodeAction = BaseAction<'move_node', {
    id: ItemID; // ID перемещаемого узла
    target_id: ItemID; // ID узла, относительно которого происходит перемещение
    type: 'before' | 'after'; // Тип перемещения
}>;
