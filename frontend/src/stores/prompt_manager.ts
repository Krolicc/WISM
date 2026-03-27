
import { ref, reactive, computed } from 'vue';
import { defineStore } from 'pinia';

import type { PromptObject } from '../types/prompt';

export const usePromptManagerStore = defineStore('promptManager', () => {

  // State
  const activeObject = ref<null | Object>(null);
  const editablePrompt = computed((): PromptObject | null => activeObject.value?.detailed_prompt || null);
  const expandedIds = reactive(new Set())

  function handlePromptUpdate(newValue: PromptObject) {
  }

  const toggleSection = (id: string) => {
    if (expandedIds.has(id)) {
      expandedIds.delete(id);
    } else {
      expandedIds.add(id);
    }
  };

  const setActiveObject = (newObject: Object | null) => {
    activeObject.value = newObject;
  };


  return {
    editablePrompt,
    expandedIds,
    handlePromptUpdate,
    setActiveObject,
    toggleSection,
  };
});
