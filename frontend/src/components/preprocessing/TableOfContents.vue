<template>
  <div class="toc-container">
    <div class="toc-left-panel content-block">
      <TocTreeView
        :blocks="storyStore.blocks"
        :target-id="targetId"
        :active-action="activeAction"
        @set-target="setTarget"
      />
    </div>
    
    <div class="toc-right-panel">
      <TocActions
        :active-action="activeAction"
        :is-anything-selected="isAnythingSelected"
        :is-valid-selection="selectionMetadata.isValidForMove"
        :target-block="targetBlock"
        :source-type="selectionMetadata.type"
        @clear-selection="handleClearSelection"
        @start-action="startAction"
        @cancel-action="cancelAction"
        @execute="executeAction"
      />
      <TocSelection
        :selected-blocks="selectionStore.selectedBlocks"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useStoryStructuringStore, findBlock } from '/src/stores/story-structuring';
import { useSelectionStore } from '/src/stores/selection';
import { storeToRefs } from 'pinia';
import type { BlockType } from '@/types/preprocessing';

import TocTreeView from './TocTreeView.vue';
import TocActions from './TocActions.vue';
import TocSelection from './TocSelection.vue';

const storyStore = useStoryStructuringStore();
const selectionStore = useSelectionStore();
const { selectionMetadata } = storeToRefs(selectionStore);

const activeAction = ref<null | 'move' | 'merge'>(null);
const targetId = ref<string | null>(null);

const isAnythingSelected = computed(() => selectionStore.selectedBlockIds.size > 0);
const targetBlock = computed(() => targetId.value ? findBlock(storyStore.blocks, targetId.value) : null);

const firstSelectedBlockType = computed((): BlockType | null => {
  if (!isAnythingSelected.value) return null;
  const firstId = selectionStore.selectedBlockIds.values().next().value;
  const block = findBlock(storyStore.blocks, firstId);
  return block ? block.type : null;
});

function startAction(action: 'move' | 'merge') {
  activeAction.value = action;
  targetId.value = null;
}

function cancelAction() {
  activeAction.value = null;
  targetId.value = null;
}

function setTarget(id: string | null) {
  targetId.value = id;
}

function handleClearSelection() {
  selectionStore.clearSelection();
  cancelAction();
}

function executeAction(payload: { position: 'before' | 'after' | 'prepend' | 'append' }) {
  if (!targetId.value || !activeAction.value) return;
  
  selectionStore.executeMoveOrMerge({
    targetId: targetId.value,
    action: activeAction.value,
    position: payload.position
  });

  cancelAction();
}
</script>

<style scoped>
.toc-container {
  width: 100%;
  height: 100%;
  display: flex;
  gap: 10px;
  overflow: visible;
}

.toc-left-panel {
  width: 60%;
  height: 100%;
  overflow-y: auto;
}

.toc-right-panel {
  width: 40%;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 10px
}
</style>
