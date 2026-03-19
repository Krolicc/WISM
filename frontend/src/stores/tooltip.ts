import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useTooltipStore = defineStore('tooltip', () => {
  const visible = ref(false);
  const content = ref('');
  const position = ref({ top: 0, left: 0 });

  function show(newContent: string, rect: DOMRect) {
    content.value = newContent;
    // Position the tooltip centered above the element
    position.value = {
      top: rect.top - 8, // 8px offset from the element
      left: rect.left + rect.width / 2,
    };
    visible.value = true;
  }

  function hide() {
    visible.value = false;
  }

  return { visible, content, position, show, hide };
});
