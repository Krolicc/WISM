
import { BaseAction, ItemID } from '../base';

// Типы узлов, которые мы можем создавать
export type NodeType = 'arc' | 'chapter' | 'scene';

// Общий интерфейс для всех действий по созданию
interface CreateNodeParams {
    id: ItemID; // ID создаваемого узла (генерируется на клиенте)
    type: NodeType;
    after_id: ItemID; // ID узла, после которого нужно вставить новый
    parent_id: ItemID;
}

// Создание нового узла
export type CreateNodeAction = BaseAction<'create_node', CreateNodeParams>;

// Восстановление ранее удаленного узла (из корзины)
export type GenerateNodeAction = BaseAction<'generate_node', CreateNodeParams>;

