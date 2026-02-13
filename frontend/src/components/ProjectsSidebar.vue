<template>
  <div class="sidebar">
    <!-- Projects View -->
    <template v-if="navStore.sidebarView === 'PROJECTS'">
      <button @click="handleCreateNewProject" class="new-project-btn">NEW PROJECT</button>
      <div class="list-container">
        <div 
          v-for="project in projectsStore.projects"
          :key="project.id"
          class="project-block content-block"
          :class="{ active: project.id === projectsStore.activeProjectId }"
          @click="selectProject(project.id)"
        >
          <h3 class="project-prompt">{{ project.prompt }}</h3>
          <span v-if="project.isLoading" class="spinner">🌀</span>
        </div>
      </div>
    </template>

    <!-- Chapters View -->
    <template v-else-if="navStore.sidebarView === 'CHAPTERS' && activeProject">
       <button @click="handleGenerateScenes" class="new-plot-point-btn">GENERATE SCENES</button>
      <div class="list-container">
        <div 
          v-for="chapter in activeProject.chapters"
          :key="chapter.id"
          class="plot-point-block content-block" 
          :class="{ active: chapter.id === navStore.activeChapterId }"
          @click="navStore.setActiveChapterId(chapter.id)"
        >
           <h4 class="plot-point-title">{{ chapter.title }}</h4>
           <span v-if="chapter.isLoading" class="spinner">🌀</span>
        </div>
         <div v-if="activeProject.isLoading" class="spinner-message">🌀 Generating chapters...</div>
      </div>
    </template>

  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useProjectsStore } from '../stores/projects'
import { useNavigationStore } from '../stores/navigation'

const projectsStore = useProjectsStore()
const navStore = useNavigationStore()

const activeProject = computed(() => projectsStore.activeProject)
const activeChapter = computed(() => projectsStore.activeChapter)

function selectProject(id: number) {
  projectsStore.setActiveProject(id)
  // The store action now handles switching the view
}

function handleCreateNewProject() {
  const prompt = window.prompt("Enter the new comic idea:")
  if (prompt) {
    projectsStore.createNewProject(prompt)
  }
}

function handleGenerateScenes() {
    if(activeProject.value && activeChapter.value) {
        projectsStore.generateScenesForChapter(activeProject.value.id, activeChapter.value.id)
    }
}

</script>

<style scoped>
.sidebar {
  width: 340px; /* Wider for more space */
  flex-shrink: 0;
  background-color: var(--bg-color);
  border-right: 1px solid var(--border-color);
  padding: 2rem;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 60px); /* Full height minus header */
}

.list-container { overflow-y: auto; flex-grow: 1; margin-top: 1.5rem; }

.new-project-btn, .new-plot-point-btn {
  width: 100%;
  padding: 1.25rem;
  font-size: 1.1rem;
  font-weight: 700;
  border-radius: var(--border-radius);
  cursor: pointer;
  transition: filter 0.2s;
  flex-shrink: 0;
}
.new-project-btn { background-color: var(--main-color); color: white; }
.new-plot-point-btn { background-color: var(--sub-color); color: white; }
.new-project-btn:hover, .new-plot-point-btn:hover { filter: brightness(110%); }

.content-block {
  background-color: var(--container-bg);
  border-radius: var(--border-radius);
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  padding: 1.25rem 1.5rem;
  margin-bottom: 1.25rem;
  border: 1px solid var(--border-color);
  cursor: pointer;
  transition: border-color 0.2s, box-shadow 0.2s;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.content-block:hover { border-color: var(--sub-color); }
.content-block.active { border-color: var(--main-color); box-shadow: 0 4px 12px rgba(0,0,0,0.08); }

.project-prompt, .plot-point-title { 
  font-size: 1rem; 
  font-weight: 600; 
  margin: 0; 
  white-space: nowrap; 
  overflow: hidden; 
  text-overflow: ellipsis; 
  padding-right: 1rem;
}

.spinner { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.spinner-message { padding: 1rem; text-align: center; color: var(--sub-color); }
</style>
