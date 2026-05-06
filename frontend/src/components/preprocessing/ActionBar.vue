<template>
  <div class="action-bar" :class="{ 'is-toc-open': isTocOpen }">
    
    <div class="left-section">
      <button class="toc-toggle-button" @click="$emit('toggle-toc')">
        ☰ Оглавление
      </button>
    </div>

    <div class="center-section" :class="{ 'actions-disabled': !isTextSelected }">
      <button 
        v-for="button in availableButtons" 
        :key="button.type" 
        @click="$emit('create', button.type)"
        :style="{ backgroundColor: button.color }"
        :disabled="!isTextSelected"
        class="action-button"
      >
        {{ button.type }}
      </button>
    </div>

    <div class="right-section">
    </div>

  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { BlockType } from '@/types/preprocessing';

const props = defineProps<{
  isTextSelected: boolean;
  parentType: BlockType | null;
  isTocOpen: boolean; // New prop
}>();

defineEmits<{
  (e: 'create', type: Exclude<BlockType, 'source'>): void;
  (e: 'toggle-toc'): void;
}>();

const ALL_BUTTONS = [
  { type: 'Arc', color: '#E57373' },
  { type: 'Chapter', color: '#81C784' },
  { type: 'Scene', color: '#64B5F6' },
] as const;

const availableButtons = computed(() => {
  return ALL_BUTTONS.map(btn => ({ 
    ...btn, 
    disabled: !props.isTextSelected
  }));
});
</script>

<style scoped>
.action-bar {
  background-color: var(--bg-color);
  box-shadow: var(--shadow);
  padding: 10px 15px;
  border-radius: var(--border-radius); /* Default rounding */
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.3s ease;
  height: 54px;
  box-sizing: border-box;
  position: relative;
  z-index: 10; /* Ensure it's above the content area */
}

.left-section, .right-section {
  flex: 1;
}

.right-section {
  display: flex;
  justify-content: flex-end;
}

.center-section {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  transition: opacity 0.3s ease;
}

.center-section.actions-disabled {
  opacity: 0.4;
  pointer-events: none;
}

.toc-toggle-button {
  background-color: #4a5162;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 5px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s ease;
}

.toc-toggle-button:hover {
  background-color: #5a6275;
}

.action-button {
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 5px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s ease;
}

.action-button:hover:not(:disabled) {
  filter: brightness(1.2);
}
</style>
