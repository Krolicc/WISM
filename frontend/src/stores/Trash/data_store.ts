import { syncedStore, enableVueBindings } from "@syncedstore/core";
import * as Vue from "vue";
import { ydoc } from "../services/yjs_service";
import type { StoryNode, Frame, GenerationRequest } from "@/types";

// The shape of our store. The keys 'nodes' and 'frames' MUST match
// the names used in `ydoc.getMap()` in yjs_service.ts.

enableVueBindings(Vue);

const storeShape = {
    nodes: {} as Record<string, StoryNode>,
    frames: {} as Record<string, Frame>,
    generationRequests: {} as Record<string, GenerationRequest>
};

// Create a reactive store that is automatically connected to our existing ydoc.
export const store = syncedStore(storeShape, ydoc);

console.log(store);

// For debugging:
(window as any).store = store;
