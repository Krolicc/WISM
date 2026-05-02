import * as Y from 'yjs';
import { WebsocketProvider } from 'y-websocket';
import { api } from './api';

export class YjsService<T extends Record<string, any>> {
  public ydoc: Y.Doc;
  public collections: { [K in keyof T]: Y.Map<T[K]> }; // Динамические коллекции
  public undoManager: Y.UndoManager;
  private provider: WebsocketProvider | null = null;
  private baseUrl: string;
  private apiBase: string;

  constructor(endpoint: string, keys: (keyof T)[], apiBase: string) {
    this.ydoc = new Y.Doc();
    this.baseUrl = endpoint;
    this.apiBase = apiBase;
    
    // Динамически создаем Y.Map для каждого ключа
    const collections = {} as any;
    keys.forEach(key => {
      collections[key] = this.ydoc.getMap(key as string);
    });
    
    this.collections = collections;
    this.undoManager = new Y.UndoManager(Object.values(this.collections));
  }

  async initialize(roomId: string) {
    if (this.provider) this.destroy();

    const token = await api.getWsAuthToken(`${this.apiBase}/api/v1/auth/ws-token?story_id=${roomId}`);

    this.provider = new WebsocketProvider(
      this.baseUrl, 
      roomId, 
      this.ydoc, 
      { 
        params: { token },
        connect: true 
      }
    );

    // Полезно для отладки
    this.provider.on('status', (event: any) => {
      console.log(`Yjs Status for ${roomId}: ${event.status}`); 
    });

    this.ydoc.on('subdocs', ({ loaded, added, removed }) => {
      added.forEach(subdoc => {
        subdoc.load(); 
      });
    });
  }

  destroy() {
    this.provider?.destroy();
    this.ydoc.destroy();
  }
}