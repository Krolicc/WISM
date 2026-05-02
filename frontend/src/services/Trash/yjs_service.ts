
import * as Y from 'yjs';
import { WebsocketProvider } from 'y-websocket';
import type { Frame, StoryNode } from '@/types';
import { api } from './api'; // Импортируем наш api сервис

export const ydoc = new Y.Doc();
export const nodes = ydoc.getMap<StoryNode>('nodes');
export const frames = ydoc.getMap<Frame>('frames');
export const undoManager = new Y.UndoManager([nodes, frames]);

let provider: WebsocketProvider | null = null;

export async function initializeYjs(storyId: string) {
  if (provider) {
    if (provider.roomname === storyId) {
      return;
    }
    destroyYjs(); 
  }
  console.log(`Initializing Yjs for story: ${storyId}...`);

  try {
    // 1. Получаем начальное состояние документа с бэкенда
    console.log(`Fetching bootstrap for story ${storyId}...`);
    const bootstrap = await api.getStoryBootstrap(storyId);
    
    // 2. Применяем его к нашему Y.Doc
    Y.applyUpdate(ydoc, bootstrap);
    console.log(`Bootstrap applied. Nodes: ${nodes.size}, Frames: ${frames.size}`);

  } catch (error) {
    console.error("Failed to get or apply bootstrap:", error);
    // Если не удалось загрузить начальное состояние, мы все равно можем 
    // продолжить и получить данные через WebSocket, но это будет медленнее.
  }

  // 3. Получаем токен авторизации
  const token = await api.getWsAuthToken(storyId);

  // 4. Подключаемся к WebSocket с токеном
  const wsUrl = `ws://${window.location.host}/ws/crdt/`;
  provider = new WebsocketProvider(wsUrl, storyId, ydoc, { params: { token } });

  provider.on('sync', (isSynced: boolean) => {
    if (isSynced) {
      console.log(`Yjs: Synced with room ${storyId}. Nodes: ${nodes.size}, Frames: ${frames.size}`);
    } 
  });
  provider.on('status', (event: { status: string }) => {
    console.log(`Yjs connection status: ${event.status}`);
  });
}

export function destroyYjs() {
  if (provider) {
    console.log('Destroying Yjs provider...');
    provider.disconnect();
    provider.destroy();
    provider = null;
  }
  // Очищаем документ при выходе, чтобы не было смешивания данных
  // Нужно будет создать новый ydoc при следующей инициализации.
  const newDoc = new Y.Doc();
  ydoc.destroy();
  Object.assign(ydoc, newDoc);
}

