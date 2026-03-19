<template>
  <div id="app-container">
    <header class="app-header">
      <div class="header-left content-block">
        <h1 
          class="app-title" 
          @click="goHome"
        >
          WISM
        </h1>
      </div>
      <div v-if="breadcrumb.length" class="header-center content-block">
        <div class="breadcrumb">
          <span 
            v-for="(item, index) in breadcrumb"
            :key="index"
            class="breadcrumb-item"
            :class="{active: item.level === navStore.level}"
            @click="item.action"
          >
            {{ item.title }}
            <span v-if="index < breadcrumb.length - 1" class="breadcrumb-separator">🢒</span>
          </span>
        </div>
      </div>
      <div class="header-right content-block">
        <ThemeSwitcher />
      </div>
    </header>

    <div class="app-body">
      <ActionsBar />

      <!-- Default View -->
      <template v-if="navStore.level !== 'frame' && navStore.level !== 'graph'">
        <StoriesSidebar />
        <main class="main-content content-block">
          <SceneDashboard v-if="navStore.activeScene" />
          <ChapterDashboard v-else-if="navStore.activeChapter" />
          <StoryDashboard v-else-if="navStore.activeStory" />
          <div v-else class="welcome-message">
            <h2>Welcome to WISM</h2>
            <p>Create a new story to begin.</p>
          </div>
        </main>
      </template>

      <!-- Frame Editor View -->
      <template v-else-if="navStore.level === 'frame'">
        <FrameSidebar />
        <FrameEditor />
      </template>

      <!-- Graph View -->
      <template v-else-if="navStore.level === 'graph'">
        <GraphView />
      </template>
    </div>
    
    <Tooltip />
    <ToastContainer />
    <ActionHint />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, watch } from 'vue';
import { useContentStore } from './stores/content';
import { useNavigationStore } from './stores/navigation';
import { useSocketStore } from './stores/socket';
import type { Action } from './stores/actionHint';
import ActionsBar from './components/ActionsBar.vue';
import StoriesSidebar from './components/StoriesSidebar.vue';
import ThemeSwitcher from './components/ThemeSwitcher.vue';
import StoryDashboard from './components/dashboards/StoryDashboard.vue';
import ChapterDashboard from './components/dashboards/ChapterDashboard.vue';
import SceneDashboard from './components/dashboards/SceneDashboard.vue';
import FrameSidebar from './components/FrameSidebar.vue';
import FrameEditor from './components/FrameEditor.vue';
import GraphView from './components/GraphView.vue';
import Tooltip from './components/ui/Tooltip.vue';
import ToastContainer from './components/ui/ToastContainer.vue';
import ActionHint from './components/ui/ActionHint.vue';

const contentStore = useContentStore();
const navStore = useNavigationStore();
const socketStore = useSocketStore();

const breadcrumb = computed(() => {
  const trail = [];
  if (navStore.activeStory) {
    trail.push({ 
      title: navStore.activeStory.title, 
      level: 'chapter',
      action: () => navStore.selectStory(navStore.activeStory.id) });
    if (navStore.activeChapter) {
      trail.push({ 
        title: navStore.activeChapter.title, 
        level: 'scene',
        action: () => navStore.selectChapter(navStore.activeChapter.id) });
       if (navStore.activeScene) {
         trail.push({ 
          title: navStore.activeScene.title, 
          level: 'frame',
          action: () => navStore.selectScene(navStore.activeScene.id) });
       }
    }
  }
  return trail;
});

function goHome() {
    if (navStore.level === 'frame') {
        navStore.exitFrameEditor();
    } else {
        navStore.goBackToStories();
    }
}

watch(() => navStore.activeStoryId, (newStoryId) => {
  if (newStoryId) {
    socketStore.connect(newStoryId);
  } else {
    socketStore.disconnect();
  }
});

onMounted(() => {
  contentStore.fetchAll();
});
</script>

<style>
/* --- Imports and Global Styles --- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
:root { 
  --border-radius: 5px; 
  --shadow: 0 0 16px 4px rgba(160, 179, 189, .25);
  --main-color-green: #4CAF50;
  --main-color-red: #F44336;
}
[data-theme="light"] { --main-color: #52958C; --sub-color: #A0B3BD; --container-bg: #F1F3F5; --text-color: #121416; --bg-color: #F1F3F5; --border-color: #DEE2E6; }
[data-theme="dark"] { --main-color: #52958C; --sub-color: #5A6D7A; --container-bg: #1E222A; --text-color: #ecf0f1; --bg-color: #1E222A; --border-color: #495057; }
body { font-family: 'Inter', sans-serif; margin: 0; background-color: var(--bg-color); color: var(--text-color); }

#app-container { 
  display: flex; 
  flex-direction: column; 
  height: 100vh;
  padding: 2rem;
  gap: 2rem;
  box-sizing: border-box;
}
.app-header { 
  height: 54px;
  display: flex; 
  align-items: center; 
  flex-direction: row;
  gap: 1.5rem;
  flex-shrink: 0;
}

.app-header > div{
  height: 100%;
}

.header-left { 
  display: flex; 
  align-items: center;
  padding: 0 1.5rem;
}
.header-center {
  display: flex;
  justify-self: start;
  padding: 0 1rem;
}
.header-right {
  display: flex;
  align-items: center;
  margin-left: auto;
  padding: 0 .4375rem;
}

.app-title { font-size: 1.5rem; font-weight: 700; margin: 0; cursor: pointer;}
.breadcrumb { display: flex; align-items: center; font-weight: 600; }
.breadcrumb-item { cursor: pointer; }
.breadcrumb-item.active { color: var(--main-color); }
.breadcrumb-separator { margin: 0 .675rem 0 .5rem; }
.breadcrumb-item:has(+ .active) .breadcrumb-separator{ color: var(--main-color); }

.app-body { 
  display: flex; 
  flex-grow: 1; 
  gap: 2rem;
}
.main-content { 
  flex-grow: 1; 
  padding: 2rem; 
  overflow-y: auto;
}
.content-block { 
  background-color: var(--container-bg); 
  border-radius: var(--border-radius); 
  box-shadow: var(--shadow); 
}
.welcome-message { padding: 2rem; text-align: center; margin: auto; max-width: 600px; }
</style>