
import * as Y from 'yjs';
import { WebsocketProvider } from 'y-websocket';
import type { Frame, StoryNode } from '@/types'; 
import mockData from '../example_jsons/story-structure.json';
import { store } from '../stores/data_store'; 

// 1. Инициализируем главный Yjs-документ
export const ydoc = new Y.Doc();

// 2. Настраиваем WebSocket-провайдер для совместной работы.
//    - Мы используем локальный тестовый сервер, который предоставляет y-websocket.
//    - Откройте приложение в нескольких вкладках, и они будут синхронизироваться.
export const provider = new WebsocketProvider(
  'wss://1234-firebase-wism-1770010266998.cluster-4cmpbiopffe5oqk7tloeb2ltrk.cloudworkstations.dev/', 
  'wism-room',
  ydoc
);

// 3. Определяем общие CRDT-структуры, которые соответствуют вашим данным
export const nodes = ydoc.getMap<StoryNode>('nodes');
export const frames = ydoc.getMap<Frame>('frames');

// 4. Создаем Undo Manager для отмены/повтора действий
//    Он будет отслеживать изменения только в указанных структурах.
export const undoManager = new Y.UndoManager([nodes, frames]);

// 5. Логика для первоначальной загрузки mock-данных
//    Она сработает один раз, когда документ будет синхронизирован и пуст.
provider.on('sync', (isSynced: boolean) => {
  if (isSynced && nodes.size === 0) { 
    console.log('Yjs: Document is synced and empty. Loading mock data...');
    // Мы используем транзакцию, чтобы сгруппировать все начальные изменения в одно событие
    ydoc.transact(() => {
      Object.entries(mockData.nodes).forEach(([key, value]) => {
        // ПРЯМОЕ ПРИСВОЕНИЕ: SyncedStore сам очистит объект от .value
        store.nodes[key] = value as any; 
      });

      // Инициализируем фреймы
      Object.entries(mockData.frames).forEach(([key, value]) => {
        store.frames[key] = value as any;
      });
      console.log(`Yjs: Loaded ${nodes.size} nodes and ${frames.size} frames.`);
    });
  }
}); 

// Awareness-протокол позволяет отслеживать курсоры и статусы других пользователей.
export const awareness = provider.awareness;
