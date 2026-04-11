
import { BaseAction, ItemID } from '../base';

// Действие по созданию нового фрейма
export type CreateFrameAction = BaseAction<'create_frame', {
    id: ItemID; // ID создаваемого фрейма (генерируется на клиенте)
    after_id: ItemID; // ID фрейма, после которого нужно вставить новый
}>;
