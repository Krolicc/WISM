<template>
  <div class="frame-editor content-block" v-if="navStore.activeScene" @keydown="handleKeydown" tabindex="0">
    <!-- Header Controls -->
    <div class="editor-header">
      <div class="view-controls">
        <span v-if="navStore.activeScene.frames.length > 0">
          Frame {{ currentFrameIndex + 1 }} of {{ navStore.activeScene.frames.length }}
        </span>
      </div>
      <button @click="navStore.exitFrameEditor()" class="close-btn">Close Editor</button>
    </div>

    <!-- Main Content -->
    <div class="editor-main-content" v-if="activeFrame">
      <div class="frame-content-area">
        <div class="frame-display-row">
          <div class="image-container">
            <div v-if="activeFrame.isLoading" class="loading-overlay"><div class="spinner"></div></div>
            <img v-if="activeFrame.image_url" :src="activeFrame.image_url" alt="Frame image" />
            <div v-else class="no-image">No Image</div>
            <div class="frame-actions">
              <button class="icon-btn" @click="contentStore.regenerateFrame(activeFrame.id)" :disabled="activeFrame.isLoading" title="Regenerate Image">&#x21bb;</button>
              <button class="icon-btn" @click="isEditingDetails = true" title="Toggle Details Editor">&#9998;</button>
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
        :is-saving="contentStore.isLoading"
        @update:is-open="isEditingDetails = $event"
        @update:prompt="handlePromptUpdate"
        @save="handleSave"
      />
    </div>
    
    <div v-if="!activeFrame && navStore.activeScene" class="empty-message">
      This scene has no frames yet. Generate them from the scene dashboard.
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue';
import { useNavigationStore } from '../stores/navigation';
import { useContentStore } from '../stores/content';
import { usePromptManager } from '../composables/usePromptManager';
import type { Frame } from '../types';
import FrameDetailsSidebar from './timeline/FrameDetailsSidebar.vue';

const navStore = useNavigationStore();
const contentStore = useContentStore();

const currentFrameIndex = ref(0);
const isEditingDetails = ref(false);

const activeFrame = computed<Frame | null>(() => {
  if (navStore.activeScene && navStore.activeScene.frames.length > 0) {
    const sortedFrames = [...navStore.activeScene.frames].sort((a, b) => a.order - b.order);
    return sortedFrames[currentFrameIndex.value] || null;
  }
  return null;
});

const { editablePrompt, handlePromptUpdate, saveDetailedPrompt } = usePromptManager(activeFrame);

watch(() => navStore.activeScene, () => {
  currentFrameIndex.value = 0;
  isEditingDetails.value = false;
});

async function handleSave() {
  try {
    await saveDetailedPrompt();
    alert('Detailed prompt saved!');
    isEditingDetails.value = false; // Close sidebar on successful save
  } catch (error) {
    console.error('Error saving detailed prompt:', error);
    alert('Failed to save detailed prompt.');
  }
}

const nextFrame = () => {
  if (navStore.activeScene && currentFrameIndex.value < navStore.activeScene.frames.length - 1) {
    currentFrameIndex.value++;
  }
};

const prevFrame = () => {
  if (currentFrameIndex.value > 0) {
    currentFrameIndex.value--;
  }
};

const handleKeydown = (event: KeyboardEvent) => {
  if (isEditingDetails.value) return; // Don't navigate when sidebar is open

  if (event.key === 'ArrowRight') {
    event.preventDefault();
    nextFrame();
  } else if (event.key === 'ArrowLeft') {
    event.preventDefault();
    prevFrame();
  }
};

onMounted(() => {
    nextTick(() => {
        const editor = document.querySelector('.frame-editor') as HTMLElement;
        if(editor) editor.focus();
    });
});

</script>

<style scoped>
/* --- Main Layout --- */
.frame-editor {
  flex-grow: 1;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  outline: none; 
  position: relative;
  overflow: hidden;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  flex-shrink: 0;
}

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

/* Other styles are now in FrameDetailsSidebar.vue */

.image-container img { max-width: 100%; max-height: 100%; object-fit: contain; display: block;}
.no-image, .empty-message { display:flex; align-items:center; justify-content:center; height:100%; color: var(--sub-color); background-color: var(--container-bg); width: 100%; text-align: center; }
.empty-message { padding: 2rem; }
.loading-overlay { position: absolute; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 10; }
.spinner { border: 4px solid #f3f3f3; border-top: 4px solid var(--main-color); border-radius: 50%; width: 30px; height: 30px; animation: spin 1s linear infinite; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
.frame-actions { position: absolute; bottom: 0.5rem; right: 0.5rem; display: flex; gap: 0.5rem; background: rgba(0,0,0,0.6); padding: 0.5rem; border-radius: var(--border-radius); }
.icon-btn { background: none; color: white; border: none; border-radius: 50%; width: 30px; height: 30px; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; transition: background-color 0.2s; }
.icon-btn:hover { background-color: rgba(255, 255, 255, 0.2); }
.close-btn { background: var(--container-bg); color: var(--text-color); padding: 0.5rem 1rem; border-radius: var(--border-radius); cursor: pointer; border: 1px solid var(--border-color); }
</style>