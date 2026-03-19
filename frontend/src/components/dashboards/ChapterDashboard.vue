<template>
  <div class="dashboard-container" v-if="navStore.activeChapter">
    <div class="dashboard-header">
      <h1>{{ navStore.activeChapter.title }}</h1>
      <button @click="manageChapter" class="edit-btn">Manage Scenes</button>
    </div>
    <p class="chapter-description">{{ navStore.activeChapter.description || 'No description yet.' }}</p>
    
    <div class="list-section">
      <h2>Scenes</h2>
      <div class="list-container">
        <div 
          v-for="scene in navStore.activeChapter.scenes" 
          :key="scene.id" 
          class="list-item content-block"
        >
          <div class="item-content">
            <h4>{{ scene.title }}</h4>
            <p class="item-description">{{ scene.description }}</p>
          </div>
        </div>
         <div v-if="!navStore.activeChapter.scenes || navStore.activeChapter.scenes.length === 0" class="empty-list-message">
          This chapter has no scenes yet.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useNavigationStore } from '../../stores/navigation';
const navStore = useNavigationStore();

function manageChapter() {
  if (navStore.activeChapterId) {
    navStore.navigateToScenes(navStore.activeChapterId);
  }
}
</script>

<style scoped>
/* Using the same styles as StoryDashboard for consistency */
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

.chapter-description {
  font-size: 1.1rem;
  color: var(--sub-color);
  max-width: 80ch;
}

.list-section h2 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

.list-item {
  padding: 1rem 1.5rem;
  margin-bottom: 1rem;
}

.item-content h4 {
  margin: 0 0 0.5rem 0;
}

.item-description {
  margin: 0;
  font-size: 0.9rem;
  color: var(--sub-color);
  max-width: 80ch;
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
