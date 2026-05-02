import type { StoryNode } from '../types';
import { YjsService } from './yjs_service';

interface DataSchemaContent {
  nodes: StoryNode;
}

export const yjsServiceContent = new YjsService<DataSchemaContent>(
  `ws://${window.location.host}/ws/crdt/content/`, 
  ['nodes'],
  'http://backend:8000'
);

export const apiBase = 'http://backend:8000';