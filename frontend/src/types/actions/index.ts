
import { ManageAction } from './manage';
import { FrameAction } from './frame';

// Общий тип для всех действий
export type Action = ManageAction | FrameAction;

// Базовый тип для всех действий
export * from './base';

// Экспортируем все типы действий
export * from './manage';
export * from './frame';
