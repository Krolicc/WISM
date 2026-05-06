<template>
  <div class="editor-main-content" v-if="activeFrame">
    <div class="frame-content-area">
      <div class="frame-display-row">
        <div class="image-container">
          <div v-if="activeFrame.isLoading" class="loading-overlay"><div class="spinner"></div></div>
          <img v-if="activeFrame.image_url" :src="activeFrame.image_url" alt="Frame image" />
          <div v-else class="no-image">No Image</div>
          <div class="frame-actions">
            <button class="icon-btn" @click="$emit('regenerate-image')" :disabled="activeFrame.isLoading" title="Regenerate Image">&#x21bb;</button>
            <button class="icon-btn" @click="$emit('update:isEditingDetails', true)" title="Toggle Details Editor">&#9998;</button>
          </div>
        </div>
        <div class="description-wrapper">
           <p class="description">{{ activeFrame.common_description || 'No description provided.' }}</p>
        </div>
      </div>
    </div>

    <!-- Sidebar Details Editor -->
    <FrameDetailsSidebar
      :is-open="isEditingDetails"
      :prompt="editablePrompt"
      :is-saving="isSaving"
      @update:is-open="$emit('update:isEditingDetails', $event)"
      @update:prompt="$emit('update:prompt', $event)"
      @save="$emit('save')"
    />
  </div>
  
  <div v-if="!activeFrame && activeNode" class="empty-message">
    This scene has no frames yet. Generate them from the scene dashboard.
  </div>
</template>

<script setup lang="ts">
import { Frame } from '../../types/index';
import FrameDetailsSidebar from './FrameDetailsSidebar.vue';

defineProps<{
  activeFrame: Frame | null;
  isEditingDetails: boolean;
  editablePrompt: string;
  isSaving: boolean;
  activeNode: any; // Assuming activeNode is passed from parent
}>();

defineEmits<{
  (e: 'update:isEditingDetails', value: boolean): void;
  (e: 'update:prompt', value: string): void;
  (e: 'save'): void;
  (e: 'regenerate-image'): void;
}>();
</script>

<style scoped>
.editor-main-content {
  position: relative;
  flex-grow: 1;
  overflow: hidden;
}

.frame-content-area {
  height: 100%;
  overflow-y: auto; 
}

.frame-display-row {
  display: flex;
  gap: 1.5rem;
}

.image-container {
  flex: 3;
  min-width: 300px;
  aspect-ratio: 16 / 9;
  background-color: #000;
  border-radius: var(--border-radius);
  position: relative;
  box-shadow: var(--shadow-heavy);
  border: 1px solid var(--border-color);
}

.description-wrapper { flex: 2; }
.description { color: var(--sub-color); font-size: 1.1rem; line-height: 1.6; }

.image-container img { max-width: 100%; max-height: 100%; object-fit: contain; display: block;}
.no-image, .empty-message { display:flex; align-items:center; justify-content:center; height:100%; color: var(--sub-color); background-color: var(--container-bg); width: 100%; text-align: center; }
.empty-message { padding: 2rem; }
.loading-overlay { position: absolute; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 10; }
.spinner { border: 4px solid #f3f3f3; border-top: 4px solid var(--main-color); border-radius: 50%; width: 30px; height: 30px; animation: spin 1s linear infinite; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
.frame-actions { position: absolute; bottom: 0.5rem; right: 0.5rem; display: flex; gap: 0.5rem; background: rgba(0,0,0,0.6); padding: 0.5rem; border-radius: var(--border-radius); }
.icon-btn { background: none; color: white; border: none; border-radius: 50%; width: 30px; height: 30px; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; transition: background-color 0.2s; }
.icon-btn:hover { background-color: rgba(255, 255, 255, 0.2); }
</style>
