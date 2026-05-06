<template>
  <div class="modal-overlay">
    <div class="modal-content">

      <ActionBar 
        :is-text-selected="selection.isActive"
        :parent-type="selection.sourceBlockType"
        :is-toc-open="isTocOpen" 
        @create="handleCreateBlock"
        @toggle-toc="handleToggleToc"
      />

      <div class="content-area">
        <StoryEditor 
          v-show="!isTocOpen" 
          @text-selected="handleTextSelected"
        />
        
        <TableOfContents 
          v-show="isTocOpen" 
          @close="isTocOpen = false" 
        />
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import type { BlockType } from '@/types/preprocessing';
import { useStoryStructuringStore } from '/src/stores/story-structuring';
import { useSelectionStore } from '/src/stores/selection'; // New import
import StoryEditor from './StoryEditor.vue';
import ActionBar from './ActionBar.vue';
import TableOfContents from './TableOfContents.vue';

const storyStore = useStoryStructuringStore();
const selectionStore = useSelectionStore(); // New store instance

const isTocOpen = ref(false);

const selection = reactive({
  isActive: false,
  sourceBlockId: null as string | null,
  sourceBlockType: null as BlockType | null,
  text: ''
});

function handleTextSelected(data: { blockId: string; blockType: BlockType; text: string; }) {
  selection.isActive = true;
  selection.sourceBlockId = data.blockId;
  selection.sourceBlockType = data.blockType;
  selection.text = data.text;
}

function handleToggleToc() {
  isTocOpen.value = !isTocOpen.value;
  if (isTocOpen.value) {
    selection.isActive = false;
    selection.sourceBlockId = null;
    selection.sourceBlockType = null;
    selection.text = '';
    window.getSelection()?.removeAllRanges();
  } else {
    selectionStore.clearSelection(); // Use the new store
  }
}

function handleCreateBlock(type: Exclude<BlockType, 'source'>): void {
  if (!selection.sourceBlockId || !selection.text) return;

  storyStore.createBlock(selection.sourceBlockId, selection.text, type);

  selection.isActive = false;
  selection.sourceBlockId = null;
  selection.sourceBlockType = null;
  selection.text = '';
  window.getSelection()?.removeAllRanges();
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  backdrop-filter: blur(10px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  width: 90%;
  max-width: 700px;
  height: 90%;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.content-area {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  overflow: visible;
}
</style>
