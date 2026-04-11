
import { CreateNodeAction, GenerateNodeAction } from './create';
import { MoveNodeAction } from './move';
import { UpdateTitleAction, UpdateDescriptionAction } from './update';
import { ReAction, ChangeReAction, ChangeReActionFlag } from './re-action';
import { DeleteNodeAction } from './delete';

// Общий тип для всех действий по управлению структурой
export type ManageAction =
  | CreateNodeAction
  | GenerateNodeAction
  | MoveNodeAction
  | UpdateTitleAction
  | UpdateDescriptionAction
  | ReAction
  | DeleteNodeAction
  | ChangeReAction
  | ChangeReActionFlag;
