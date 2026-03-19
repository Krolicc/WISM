<template>
  <div class="actions-bar-container">
    <div class="actions-bar content-block">
      <!-- Top Actions -->
      <div 
        class="action-item" 
        :class="{ active: navStore.level === 'story' }"
        @click="navStore.navigateStoryLevel('story')"
        title="Stories"
      >
        <!-- Stories Icon -->
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path>
          <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path>
        </svg>
      </div>

      <!-- Mid Actions (conditionally rendered) -->
      <div 
        class="action-item"
        :class="{ active: navStore.level === 'chapter' }"
        @click="navStore.activeStoryId && navStore.navigateStoryLevel('chapter')"
        title="Chapters"
        :data-disabled="!navStore.activeStoryId"
      >
        <!-- Chapters Icon -->
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
          <polyline points="14 2 14 8 20 8"></polyline>
        </svg>
      </div>

      <div 
        class="action-item"
        :class="{ active: navStore.level === 'scene' }"
        @click="navStore.activeChapterId && navStore.navigateStoryLevel('scene')"
        title="Scenes"
        :data-disabled="!navStore.activeChapterId"
      >
        <!-- Scenes Icon -->
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 8V20C21 20.5523 20.5523 21 20 21H2C1.44772 21 1 20.5523 1 20V8H21Z" />
          <path d="M21 8V12H1L1 8L21 8Z" />
          <path d="M2.00002 1L20 1C20.5523 1 21 1.44771 21 2V5L1.00002 5L1.00002 2C1.00002 1.44772 1.44773 1 2.00002 1Z" />
          <line x1="5.70711" y1="1.29289" x2="9.24264" y2="4.82843" />
          <line x1="10.7071" y1="1.29289" x2="14.2426" y2="4.82843" />
          <line x1="15.7075" y1="1.29289" x2="19.243" y2="4.82843" />
          <line y1="-1" x2="5" y2="-1" transform="matrix(0.707107 -0.707107 -0.707107 -0.707107 5 10.998)" />
          <line y1="-1" x2="5" y2="-1" transform="matrix(0.707107 -0.707107 -0.707107 -0.707107 10 11)" />
          <line y1="-1" x2="5" y2="-1" transform="matrix(0.707107 -0.707107 -0.707107 -0.707107 15 10.998)" />
        </svg>
      </div>

      <!-- Bottom Actions -->
      <div 
        class="action-item"
        :class="{ active: navStore.level === 'frame' }"
        @click="navStore.activeSceneId && navStore.navigateStoryLevel('frame')"
        title="Frames"
        :data-disabled="!navStore.activeSceneId"
      >
        <!-- Frames Icon -->
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="20" rx="2.18" ry="2.18"></rect><line x1="7" y1="2" x2="7" y2="22"></line><line x1="17" y1="2" x2="17" y2="22"></line><line x1="2" y1="12" x2="22" y2="12"></line><line x1="2" y1="7" x2="7" y2="7"></line><line x1="2" y1="17" x2="7" y2="17"></line><line x1="17" y1="17" x2="22" y2="17"></line><line x1="17" y1="7" x2="22" y2="7"></line></svg>
      </div>
    </div>

    <div class="actions-bar content-block">
      <div 
        class="action-item" 
        :class="{ active: navStore.level === 'graph' }"
        @click="navStore.navigateStoryLevel('graph')"
        title="Graph View"
      >
        <!-- Graph Icon -->
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="3"></circle>
          <path d="M12 15v5"></path>
          <path d="M12 4v5"></path>
          <path d="M19.07 19.07l-3.54-3.54"></path>
          <path d="M4.93 4.93l3.54 3.54"></path>
          <path d="M19.07 4.93l-3.54 3.54"></path>
          <path d="M4.93 19.07l3.54-3.54"></path>
        </svg>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useNavigationStore } from '../stores/navigation';
const navStore = useNavigationStore();
</script>

<style scoped>
.actions-bar-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: start;
  gap: 1.5rem;
}

.actions-bar {
  height: fit-content;
  width: 70px; /* More space */
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-block: .8125rem;
  gap: 1.5rem; /* More spacing */
  z-index: 200;
  flex-shrink: 0;
}

.action-item {
  width: 44px;
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
