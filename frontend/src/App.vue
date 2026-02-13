<template>
  <div id="app-container">
    <header class="app-header">
      <div class="header-left">
        <h1 class="app-title">WISM</h1>
        <div v-if="activeProject" class="header-divider"></div>
        <div v-if="activeProject" class="project-title-dropdown">
          <span>{{ activeProject.prompt }}</span>
          <svg width="12" height="12" viewBox="0 0 24 24"><path d="M7 10l5 5 5-5z"/></svg>
        </div>
      </div>
      <div class="header-right">
        <ThemeSwitcher />
      </div>
    </header>

    <div class="app-body">
       <ActionsBar />
       <ProjectsSidebar />

      <main class="main-content">
        <!-- If a chapter is selected, show its scenes -->
        <template v-if="activeChapter">
          <Scene 
            v-for="scene in activeChapter.scenes"
            :key="scene.id"
            :scene="scene"
            :project-id="activeProject.id"
          />
          <div v-if="activeChapter.isLoading" class="spinner-message">🌀 Generating scenes...</div>
           <div v-if="!activeChapter.isLoading && activeChapter.scenes.length === 0" class="welcome-message content-block">
            <h2>{{ activeChapter.title }}</h2>
            <p>This chapter has no scenes yet. Click "Generate Scenes" in the sidebar to create them.</p>
        </div>
        </template>

        <!-- If only a project is selected, show chapter selection message -->
        <div v-else-if="activeProject" class="welcome-message content-block">
            <h2>{{ activeProject.prompt }}</h2>
            <p>Select a Chapter from the left sidebar to see its scenes, or create a new one.</p>
        </div>

        <!-- Default welcome message -->
         <div v-else class="welcome-message content-block">
            <h2>Welcome to WISM</h2>
            <p>Create a new project from the sidebar to begin.</p>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useProjectsStore } from './stores/projects'
import { useNavigationStore } from './stores/navigation'
import ActionsBar from './components/ActionsBar.vue'
import ProjectsSidebar from './components/ProjectsSidebar.vue'
import Scene from './components/Scene.vue'
import ThemeSwitcher from './components/ThemeSwitcher.vue'

const projectsStore = useProjectsStore()
const navStore = useNavigationStore()

const activeProject = computed(() => projectsStore.activeProject)
const activeChapter = computed(() => projectsStore.activeChapter)

</script>

<style>
/* --- GLOBAL RESET --- */
button,
input,
textarea,
select {
  font-family: inherit;
  font-size: 100%;
  line-height: 1.15;
  margin: 0;
  padding: 0;
  border: none;
  background: none;
  color: inherit;
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
  background-color: transparent;
}

button { 
  text-align: inherit;
}

/* --- GLOBAL STYLES --- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
:root { --border-radius: 5px; --shadow: 0 4px 12px rgba(0, 0, 0, 0.05); }
[data-theme="light"] { --main-color: #52958C; --sub-color: #A0B3BD; --container-bg: #FFFFFF; --text-color: #121416; --bg-color: #F1F3F5; --border-color: #DEE2E6; }
[data-theme="dark"] { --main-color: #52958C; --sub-color: #5A6D7A; --container-bg: #2A303C; --text-color: #ecf0f1; --bg-color: #1E222A; --border-color: #495057; }
body { font-family: 'Inter', sans-serif; margin: 0; background-color: var(--bg-color); color: var(--text-color); }
#app-container { display: flex; flex-direction: column; height: 100vh; }

.app-header { 
  width: 100%; 
  height: 60px; 
  display: flex; 
  align-items: center; 
  justify-content: space-between; 
  padding: 0 2rem; 
  background-color: var(--bg-color); 
  border-bottom: 1px solid var(--border-color); 
  z-index: 100; 
  box-sizing: border-box; 
  flex-shrink: 0;
}

.header-left { 
  display: flex; 
  align-items: center; 
  gap: 1.5rem;
}

.app-title { 
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0;
}

.header-divider { 
  width: 1px; 
  height: 24px; 
  background-color: var(--border-color); 
}

.project-title-dropdown { display: flex; align-items: center; cursor: pointer; font-weight: 600; }
.project-title-dropdown svg { margin-left: 8px; fill: currentColor; }

.app-body { display: flex; flex-grow: 1; overflow: hidden; }

.main-content { 
    flex-grow: 1; 
    padding: 2rem; 
    overflow-y: auto; 
    height: calc(100vh - 60px); /* Full height minus header */
}

.content-block { background-color: var(--container-bg); border-radius: var(--border-radius); box-shadow: var(--shadow); }

.welcome-message { padding: 2rem; text-align: center; margin: 2rem auto; max-width: 600px; }

.spinner-message { padding: 2rem; text-align: center; color: var(--sub-color); font-size: 1.2rem; }
</style>
