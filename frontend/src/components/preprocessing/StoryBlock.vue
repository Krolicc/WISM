<template>
  <div class="story-block-wrapper" >
    <span 
      v-if="isLabelVisible && !hasChildren"
      class="block-type-label"
      :style="{ color: block.color.solid }"
    >
      <b>{{ block.type }}</b>
    </span>

    <div 
      v-if="!hasChildren"
      :class="['story-block']" 
      :style="{ 
        backgroundColor: block.color.solid, 
        boxShadow: `0 0 10px 4px ${block.color.shadow}` 
      }"
      @mouseup="handleMouseUp" 
    >
      <div v-if="!isEditing" class="block-content" @click.ctrl.prevent="startEditing">
        <p class="block-text">{{ block.text }}</p>
      </div>
      <textarea
        v-else
        ref="textareaRef"
        v-model="editableText"
        @blur="saveChanges"
        @keydown.esc.prevent="cancelEditing"
        class="editing-textarea"
      ></textarea>
    </div>

    <div v-if="hasChildren" class="children-container">
      <StoryBlock
        v-for="(child, index) in block.children"
        :key="child.id"
        :block="child"
        :depth="depth + 1"
        :index="index"
        :previous-sibling-type="index > 0 ? block.children[index - 1].type : null"
        @text-selected="bubbleTextSelected"
      />
    </div>
    
    <div v-if="isSceneConnectorVisible" class="scene-connector">
      <div :class="['connector-dot', { 'is-linked': true }]" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, computed } from 'vue';
import type { Block, BlockType  } from '@/types/preprocessing';
import { useStoryStructuringStore } from '/src/stores/story-structuring';

const props = defineProps<{
  block: Block;
  depth: number;
  index: number;
  previousSiblingType: BlockType | null;
}>();

const emit = defineEmits<{
  (e: 'text-selected', payload: { blockId: string; blockType: Block['type']; text: string; }): void;
}>();

const store = useStoryStructuringStore();

const isEditing = ref(false);
const editableText = ref(props.block.text);
const textareaRef = ref<HTMLTextAreaElement | null>(null);

const hasChildren = computed(() => props.block.children && props.block.children.length > 0);
const isLabelVisible = computed(() => {
  if (props.depth === 0) return true;
  
  if (props.index === 0) return true;
  
  return props.block.type !== props.previousSiblingType;
});
const isSceneConnectorVisible = computed(() => props.block.type === 'Scene' && !hasChildren.value);

async function startEditing() {
  if (hasChildren.value || window.getSelection()?.toString().trim()) return;
  isEditing.value = true;
  editableText.value = props.block.text;
  await nextTick();
  textareaRef.value?.focus();
}

function saveChanges() {
  if (!isEditing.value) return;
  store.updateBlockText(props.block.id, editableText.value);
  isEditing.value = false;
}

function cancelEditing() {
  isEditing.value = false;
}

function handleMouseUp(): void {
  if (isEditing.value || hasChildren.value) return;
  const selection = window.getSelection();
  const selectedText = selection?.toString().trim();
  if (selectedText) {
    emit('text-selected', {
      blockId: props.block.id,
      blockType: props.block.type,
      text: selectedText,
    });
  }
}

function bubbleTextSelected(payload: any) {
  emit('text-selected', payload);
}
</script>

<style scoped>
.story-block-wrapper {
  position: relative;
}

.block-type-label {
  display: block;
  font-size: 0.75em;
  font-weight: bold;
  text-transform: uppercase;
  padding-left: 12px;
  margin-bottom: -4px;
}

.story-block {
  border-radius: 8px;
  padding: 12px;
  color: white;
}

.block-content {
  cursor: pointer;
}

.block-text {
  margin: 0;
  font-size: 1em;
  white-space: pre-wrap;
}

.children-container {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.editing-textarea {
  width: 100%;
  padding: 8px;
  border-radius: 4px;
  border: 1px solid #777;
  background-color: #2c2c2c;
  color: white;
  font-family: inherit;
  font-size: inherit;
}

.scene-connector {
  position: absolute;
  bottom: -16px;
  left: 50%;
  transform: translateX(-50%);
  height: 24px;
  display: flex;
  align-items: center;
  z-index: 10;
}
.connector-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid #666;
  background-color: transparent;
}
.connector-dot.is-linked {
  background-color: #666;
}
</style>
