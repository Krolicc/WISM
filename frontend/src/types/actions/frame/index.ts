
import { CreateFrameAction } from './create';
import { UpdateTitleAction, UpdateDescriptionAction, UpdateDetailedPromptAction } from './update';
import { DeleteFrameAction } from './delete';

// Общий тип для всех действий с фреймами
export type FrameAction =
    | CreateFrameAction
    | UpdateTitleAction
    | UpdateDescriptionAction
    | UpdateDetailedPromptAction
    | DeleteFrameAction;
