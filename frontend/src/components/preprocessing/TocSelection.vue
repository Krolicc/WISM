<template>
  <div class="selection-panel content-block">
    <p v-if="selectedBlocks.length === 0" class="placeholder-text">
      Кликните на элемент для выбора. <br />
      Ctrl/Cmd + клик для мультивыбора.
    </p>
    <ul v-else class="selected-list">
      <li v-for="block in selectedBlocks" :key="block.id" class="selected-item">
        <span class="selected-item-icon" :style="{ color: block.color.solid }">■</span>
        <span class="selected-item-text">{{ block.text }}</span>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import type { Block } from '@/types/preprocessing';

defineProps<{
  selectedBlocks: Block[];
}>();
</script>

<style scoped>
.selection-panel { flex-grow: 1; padding: 15px; overflow-y: auto; }
.placeholder-text { color: #777; font-style: italic; text-align: center; margin-top: 20px; font-size: 0.9em; line-height: 1.4; }
.selected-list { list-style: none; padding: 0; margin: 0; }
.selected-item { display: flex; align-items: center; background-color: #333; padding: 6px 10px; border-radius: 3px; margin-bottom: 5px; }
.selected-item-icon { margin-right: 8px; font-size: 1.2em; }
.selected-item-text { font-size: 0.9em; color: #ddd; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
</style>
