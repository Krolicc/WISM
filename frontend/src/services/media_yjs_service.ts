import type { Entity } from '../types/media';
import { YjsService } from './yjs_service';

interface DataSchemaMedia {
  entities: Entity;
}

const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
export const apiBase = 'http://media:8002';

export const yjsServiceMedia = new YjsService<DataSchemaMedia>(
  `${wsProtocol}://${window.location.host}/ws/crdt/media/`, 
  ['entities'],
  'http://media:8002'
);
