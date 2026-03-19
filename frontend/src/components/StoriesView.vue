<template>
  <div>
    <div class="new-story-panel">
      <textarea v-model="newStoryDescription" placeholder="Enter the new comic idea or a detailed prompt here..."></textarea>
    </div>
    <div class="list-container">
      <div 
        v-for="story in contentStore.stories"
        :key="story.id"
        class="item-block"
        :class="{ active: story.id === navStore.activeStoryId }"
        @click="navStore.selectStory(story.id)"
      >
        <h3>{{ story.title }}</h3>
        <span v-if="story.isLoading" class="spinner">🌀</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useContentStore } from '../stores/content';
import { useNavigationStore } from '../stores/navigation';

const contentStore = useContentStore();
const navStore = useNavigationStore();

const newStoryDescription = ref('');

defineExpose({ newStoryDescription });

// Reset description when view changes
watch(() => navStore.level, () => {
    newStoryDescription.value = '';
});
</script>

<style scoped>
.new-story-panel textarea {
    width: 100%;
    box-sizing: border-box;
    min-height: 100px;
    padding: 0.75rem;
    border-radius: var(--border-radius);
    border: 1px solid var(--border-color);
    background-color: var(--container-bg);
    color: var(--text-color);
    resize: vertical;
    margin-bottom: 1.5rem;
}

.list-container { 
  overflow-y: auto; 
  flex-grow: 1; 
}

.item-block {
  background-color: var(--container-bg);
  border-radius: var(--border-radius);
  padding: 1rem 1.25rem;
  cursor: pointer;
  border: 1px solid var(--border-color);
  transition: all 0.2s;
  margin-bottom: 10px;
}

.item-block:hover { 
  border-color: var(--main-color);
}

.item-block.active { 
  background-color: var(--main-color);
  color: white;
  border-color: var(--main-color);
}

.item-block h3 {
    font-size: 1rem; 
    font-weight: 600; 
    margin: 0;
}

.spinner { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
