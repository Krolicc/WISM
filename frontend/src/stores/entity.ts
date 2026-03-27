
import { ref, computed, onUnmounted } from 'vue';
import * as Vue from "vue";
import { defineStore } from 'pinia';
import { syncedStore, enableVueBindings } from "@syncedstore/core";
import { Entity, ViewMode } from '../types/media';
import { yjsServiceMedia } from '../services/media_yjs_service';

enableVueBindings(Vue);
export const store = syncedStore({ 
  entities: {} as Record<string, Entity> 
}, yjsServiceMedia.ydoc);

export const useEntityStore = defineStore('entity', () => {
  // --- STATE ---
  const activeView = ref<ViewMode>('character');
  const entities = computed(() => store.entities)

  // --- ACTIONS ---
  function setView(view: ViewMode) {
    activeView.value = view;
  }

  yjsServiceMedia.initialize('1');
  // --- LIFECYCLE ---
  onUnmounted(() => {
    // Optionally, you might want to destroy the yjsService instance if the store is torn down.
    // mediaYjsService.destroy();

  });

  return {
    activeView,
    entities,
    setView,
  };
});
