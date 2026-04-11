
import { BaseAction, ItemID } from '../base';

// "Передействие" - пока не ясно, что это, но тип есть :)
export type ReAction = BaseAction<'re_action', {
    id: ItemID;
}>;

// Изменение основного действия
export type ChangeReAction = BaseAction<'change_re_action', {
    id: ItemID;
    flag: any; // Тип флага пока не определен
}>;

// Изменение флага действия
export type ChangeReActionFlag = BaseAction<'change_re_action_flag', {
    id: ItemID;
    flag: any; // Тип флага пока не определен
}>;
