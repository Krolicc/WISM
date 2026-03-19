<template>
  <div class="dashboard-container" v-if="navStore.activeScene">
    <div class="dashboard-header">
      <h1>{{ navStore.activeScene.title }}</h1>
      <button @click="editFrames" class="edit-btn">Edit Frames</button>
    </div>
    <p class="scene-description">{{ navStore.activeScene.description || 'No description yet.' }}</p>
    
    <div class="list-section">
      <h2>Frames</h2>
      <div class="list-container">
        <div class="empty-list-message">
          Frame generation is not yet implemented.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useNavigationStore } from '../../stores/navigation';
const navStore = useNavigationStore();

function editFrames() {
  if (navStore.activeScene) {
    navStore.enterFrameEditor(navStore.activeScene.id);
  }
}
</script>

<style scoped>
.dashboard-container {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 1rem;
}

.dashboard-header h1 {
  margin: 0;
  font-size: 2rem;
}

.edit-btn {
  background-color: var(--main-color);
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: var(--border-radius);
  font-weight: 600;
  cursor: pointer;
  transition: filter 0.2s;
}

.edit-btn:hover {
  filter: brightness(110%);
}

.scene-description {
  font-size: 1.1rem;
  color: var(--sub-color);
  max-width: 80ch;
}

.list-section h2 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

.empty-list-message {
  color: var(--sub-color);
  padding: 2rem;
  text-align: center;
  background-color: var(--container-bg);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow);
}
</style>
