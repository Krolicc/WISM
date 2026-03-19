<template>
  <transition name="slide-right">
    <div class="frame-details-sidebar" v-if="isOpen">
      <div class="sidebar-header">
        <h3>Detailed Prompt</h3>
        <button @click="closeSidebar" class="close-sidebar-btn">&times;</button>
      </div>
      <div class="sidebar-content">
        <PromptEditor v-if="prompt" :model-value="prompt" @update:model-value="handleUpdate" />
      </div>
      <button @click="save" class="save-btn" :disabled="isSaving">Save Details</button>
    </div>
  </transition>
</template>

<script setup lang="ts">
import PromptEditor from '../PromptEditor.vue';
import type { PromptObject } from '../../lib/prompt-templates';

const props = defineProps<{ 
  isOpen: boolean,
  prompt: PromptObject | null,
  isSaving: boolean
}>();

const emit = defineEmits<{
  (e: 'update:isOpen', value: boolean): void,
  (e: 'update:prompt', value: PromptObject): void,
  (e: 'save'): void
}>();

function closeSidebar() {
  emit('update:isOpen', false);
}

function handleUpdate(newValue: PromptObject) {
  emit('update:prompt', newValue);
}

function save() {
  emit('save');
}
</script>

<style scoped>
/* --- Sidebar --- */
.frame-details-sidebar {
  position: absolute;
  top: 0; right: 0; bottom: 0;
  width: 45%;
  max-width: 600px;
  background-color: var(--bg-color);
  box-shadow: -3px 0 15px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  z-index: 100;
  border-left: 1px solid var(--border-color);
  border-radius: var(--border-radius);
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--border-color);
}

.sidebar-header h3 { margin: 0; font-size: 1.25rem; }

.close-sidebar-btn {
  background: none; border: none; font-size: 1.75rem;
  cursor: pointer; color: var(--sub-color);
}

.sidebar-content {
  flex-grow: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

.save-btn {
  background-color: var(--main-color);
  color: white;
  padding: 0.75rem;
  margin: 1.5rem;
  border-radius: var(--border-radius);
  font-weight: 600;
  cursor: pointer;
  flex-shrink: 0;
  border: none;
}

/* --- Animations --- */
.slide-right-enter-active, .slide-right-leave-active {
  transition: transform 0.35s ease-in-out;
}
.slide-right-enter-from, .slide-right-leave-to {
  transform: translateX(100%);
}
</style>
