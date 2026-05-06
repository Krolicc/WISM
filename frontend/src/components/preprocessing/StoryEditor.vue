<template>
  <div class="story-editor">
    <div class="main-content">
      <StoryBlock
        v-for="(block, index) in store.blocks"
        :key="block.id" 
        :block="block"
        :depth="0"
        :index="index"
        :previous-sibling-type="null"
        @text-selected="emit('text-selected', $event)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useStoryStructuringStore } from '/src/stores/story-structuring';
import StoryBlock from './StoryBlock.vue';
import type { BlockType } from '@/types/preprocessing';

const store = useStoryStructuringStore();

const emit = defineEmits<{
  (e: 'text-selected', data: { blockId: string; blockType: BlockType; text: string; }): void;
}>();
</script>

<style scoped>
.story-editor {
  font-family: sans-serif;
  overflow-y: auto; /* IMPORTANT: Scroll happens here */
  flex-grow: 1;
  padding: 1rem;
  height: 100%; /* Ensure it fills the container */
  box-sizing: border-box;
}

.main-content {
  width: 100%;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 13px;
  margin: 0 auto;
  overflow-y: visible;
}
</style>
