<template>
  <li class="toc-node">
    <div 
      class="node-item-wrapper"
      :class="{ 
        'is-target': isTarget, 
        'is-active-mode': activeAction,
        'is-potential-target': isPotentialTarget
      }"
    >
      <div 
        class="node-item"
        :class="{ 
          'is-selected': isSelected, 
          'is-disabled': isDisabled
        }"
        :style="{ paddingLeft: `${depth * 20}px` }"
        @click="handleClick"
      >
        <span 
          class="expansion-toggle"
          :class="{ 'is-visible': hasChildren }"
          @click.stop="toggleExpansion"
        >
          {{ isExpanded ? '▼' : '►' }}
        </span>
        <span class="node-icon" :style="{ color: block.color.solid }">{{ icon }}</span>
        <span class="node-text">{{ block.text }}</span>
      </div>
    </div>

    <ul v-if="isExpanded && hasChildren" class="toc-list">
      <TocNode
        v-for="child in block.children"
        :key="child.id"
        :block="child"
        :depth="depth + 1"
        :target-id="targetId"
        :active-action="activeAction"
        @set-target="(id) => $emit('set-target', id)"
      />
    </ul>
  </li>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import type { Block } from '@/types/preprocessing';
import { useSelectionStore } from '/src/stores/selection';
import TocNode from './TocNode.vue';

const props = defineProps<{
  block: Block;
  depth: number;
  targetId: string | null;
  activeAction: 'move' | 'merge' | null;
}>();

const emit = defineEmits<{
  (e: 'set-target', id: string | null): void
}>();

const selectionStore = useSelectionStore();

const isSelected = computed(() => selectionStore.selectedBlockIds.has(props.block.id));
const isTarget = computed(() => props.block.id === props.targetId);
const isDisabled = computed(() => props.activeAction && isSelected.value);
const isPotentialTarget = computed(() => props.activeAction && !isDisabled.value && !isTarget.value);

const isExpanded = ref(true);
const hasChildren = computed(() => props.block.children && props.block.children.length > 0);

const icon = computed(() => {
  switch (props.block.type) {
    case 'Arc': return 'A';
    case 'Chapter': return 'C';
    case 'Scene': return 'S';
    default: return '■';
  }
});

function handleClick() {
  if (props.activeAction) {
    if (!isDisabled.value) {
      emit('set-target', isTarget.value ? null : props.block.id);
    }
  } else {
    selectionStore.toggleSelection({ 
      blockId: props.block.id, 
      isMultiSelect: false // This part needs event listener for real multi-select
    });
  }
}

function toggleExpansion() {
  isExpanded.value = !isExpanded.value;
}
</script>

<style scoped>
/* Other styles */
.toc-node {
  list-style: none;
  margin-top: 2px;
  margin-bottom: 2px;
}

.node-item-wrapper {
  border-radius: 4px;
  transition: background-color 0.2s ease;
}

.node-item-wrapper.is-active-mode:not(.is-target) .node-item:hover {
  background-color: #3c4c3c; /* Gentle hover to indicate "selectable as target" */
}

.node-item-wrapper.is-target {
  background-color: #2c3e50; /* Highlight the entire target block */
  outline: 2px solid #4a90e2;
}

.node-item {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  user-select: none;
  transition: background-color 0.2s ease, opacity 0.2s ease;
}

.node-item.is-selected {
  background-color: #4a5162;
}

.node-item.is-disabled {
  background-color: transparent;
  opacity: .5;
  user-select: none;
  cursor: not-allowed;
}


.expansion-toggle {
  width: 16px;
  text-align: center;
  margin-right: 4px;
  color: #888;
  visibility: hidden;
}

.expansion-toggle.is-visible {
  visibility: visible;
}

.node-icon {
  font-weight: bold;
  font-size: 1.1em;
  margin-right: 10px;
}

.node-text {
  color: #c0c0c0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.toc-list {
  list-style: none;
  padding: 0;
  margin-top: 5px;
  margin-left: 20px;
}
</style>
