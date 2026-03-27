
import { ref } from 'vue';
import { defineStore } from 'pinia';

// Определяем возможные режимы просмотра
export type ViewMode = 'list' | 'graph' | 'style_library' | 'entities';

export const useViewModeStore = defineStore('viewMode', () => {
  // --- STATE ---
  // По умолчанию будем показывать 'list' (списочное представление)
  const activeView = ref<ViewMode>('entities');

  // --- ACTIONS ---
  
  /**
   * Устанавливает активный режим просмотра.
   * @param view - Режим для активации ('list' или 'graph')
   */
  function setView(view: ViewMode) {
    activeView.value = view;
  }

  return {
    activeView,
    setView,
  };
});
