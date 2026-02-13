<template>
  <div class="scene-accordion content-block">
    <div class="scene-header" @click="toggleCollapse">
      <h3 class="scene-title">{{ scene.title }}</h3>
      <div class="scene-toggle-icon">
        <svg v-if="isCollapsed" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
        <svg v-else width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>
      </div>
    </div>
    <div v-if="!isCollapsed" class="scene-content">
        <div v-if="scene.frames && scene.frames.length > 0" class="frames-grid">
            <div v-for="frame in scene.frames" :key="frame.frame_id" class="frame-item">
                <img :src="frame.image_url" alt="Comic frame" class="frame-image">
                <p class="frame-narration">{{ frame.narration }}</p>
            </div>
        </div>
        <div v-else class="no-frames-message">
            <p>This scene has no frames yet.</p>
            <button class="generate-btn" @click.stop="generateFrames">Generate Frames</button>
        </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, type PropType } from 'vue'
import type { Scene } from '../types/index'
import { useProjectsStore } from '../stores/projects'

const props = defineProps({
  scene: {
    type: Object as PropType<Scene>,
    required: true
  },
  projectId: {
      type: Number,
      required: true
  },
  chapterId: { // We need chapterId to generate frames for the correct scene
      type: Number,
      required: true
  }
})

const projectsStore = useProjectsStore();
const isCollapsed = ref(true)

function toggleCollapse() {
  isCollapsed.value = !isCollapsed.value
}

function generateFrames() {
    console.log(`Generating frames for Project ID: ${props.projectId}, Chapter ID: ${props.chapterId}, Scene ID: ${props.scene.id}`);
    projectsStore.generateFramesForScene(props.projectId, props.chapterId, props.scene.id);
}

</script>

<style scoped>
.scene-accordion {
  margin-bottom: 2rem; /* More space between scenes */
}

.scene-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  padding: 1.25rem 1.5rem;
}

.scene-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
}

.scene-toggle-icon svg {
  color: var(--sub-color);
  transition: transform 0.2s;
}

.scene-header:hover .scene-toggle-icon svg {
    color: var(--text-color);
}

.scene-content {
  padding: 0 1.5rem 1.5rem 1.5rem;
  border-top: 1px solid var(--border-color);
  margin: 1.25rem 0 0 0;
}

.frames-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 1.5rem;
    padding-top: 1.5rem;
}

.frame-item {
    background-color: var(--bg-color);
    border-radius: var(--border-radius);
    overflow: hidden;
    border: 1px solid var(--border-color);
    box-shadow: var(--shadow);
}

.frame-image {
    width: 100%;
    aspect-ratio: 16 / 9;
    object-fit: cover;
    display: block;
}

.frame-narration {
    padding: 0.75rem 1rem;
    margin: 0;
    font-size: 0.9rem;
    line-height: 1.4;
}

.no-frames-message {
    text-align: center;
    padding: 3rem 1rem;
    color: var(--sub-color);
}
.generate-btn {
    margin-top: 1.5rem;
    background-color: var(--main-color);
    color: white;
    padding: 0.8rem 1.75rem;
    border-radius: var(--border-radius);
    cursor: pointer;
    font-weight: 600;
    font-size: 1rem;
    transition: filter 0.2s;
}
.generate-btn:hover {
    filter: brightness(110%);
}
</style>
