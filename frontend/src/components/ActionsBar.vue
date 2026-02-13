<template>
  <div class="actions-bar">
    <div 
      class="action-item" 
      :class="{ active: navStore.sidebarView === 'PROJECTS' }"
      @click="navStore.showProjects()"
      title="Projects"
    >
      <!-- Projects Icon -->
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path></svg>
    </div>
    <div 
      class="action-item"
      :class="{ active: navStore.sidebarView === 'CHAPTERS' }"
      @click="switchToChaptersView"
      title="Chapters"
      :data-disabled="!projectsStore.activeProjectId"
    >
      <!-- Chapters Icon -->
       <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect></svg>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useNavigationStore } from '../stores/navigation';
import { useProjectsStore } from '../stores/projects';

const navStore = useNavigationStore();
const projectsStore = useProjectsStore();

function switchToChaptersView() {
    if (projectsStore.activeProjectId) {
        navStore.showChapters();
    }
}

</script>

<style scoped>
.actions-bar {
  width: 70px; /* More space */
  height: 100vh;
  background-color: var(--bg-color);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 2rem;
  gap: 1.5rem; /* More spacing */
  z-index: 200;
  flex-shrink: 0;
}

.action-item {
  width: 44px; /* Larger click target */
  height: 44px;
  border-radius: var(--border-radius);
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  color: var(--sub-color);
  transition: all 0.2s;
}

.action-item:hover {
  color: var(--text-color);
}

.action-item.active {
  background-color: var(--container-bg);
  color: var(--main-color);
  box-shadow: var(--shadow);
}

.action-item[data-disabled="true"] {
  color: var(--border-color);
  cursor: not-allowed;
}
.action-item[data-disabled="true"]:hover {
    color: var(--border-color);
    background-color: transparent; /* Prevent hover effect */
}

</style>
