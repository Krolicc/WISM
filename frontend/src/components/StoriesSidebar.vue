<template>
  <div class="sidebar">
    <!-- Header with the main action button -->
    <button @click="handleGenerate" class="generate-btn">Generate {{ generationTarget }}</button>

    <!-- Conditional View -->
    <StoriesView v-if="navStore.level === 'story'" ref="storiesViewRef" />
    
    <TimelineView 
        v-else-if="isTimelineView" 
        ref="timelineViewRef"
        :active-item-id="currentActiveItemId"
        :is-loading="isContentLoading"
        :context="timelineContext"
        @select="selectItem"
    />

  </div>
</template>

<script setup lang="ts">
import { ref, computed, defineAsyncComponent } from 'vue';
import { useContentStore } from '../stores/content';
import { useNavigationStore } from '../stores/navigation';

// Async components for code splitting
const StoriesView = defineAsyncComponent(() => import('./StoriesView.vue'));
const TimelineView = defineAsyncComponent(() => import('./timeline/TimelineView.vue'));

const contentStore = useContentStore();
const navStore = useNavigationStore();

// Refs to access child component methods
const storiesViewRef = ref<InstanceType<typeof StoriesView> | null>(null);
const timelineViewRef = ref<InstanceType<typeof TimelineView> | null>(null);

// --- Computed properties to feed the child components ---
const isTimelineView = computed(() => 
    (navStore.level === 'chapter' && navStore.activeStory) || 
    (navStore.level === 'scene' && navStore.activeChapter)
);

const generationTarget = computed(() => {
    if (navStore.level === 'story') return 'Story';
    if (navStore.level === 'chapter') return 'Chapters';
    if (navStore.level === 'scene') return 'Scenes';
    return '';
});

const currentActiveItemId = computed(() => {
    if (navStore.level === 'chapter') return navStore.activeChapterId;
    if (navStore.level === 'scene') return navStore.activeSceneId;
    return null;
});

const isContentLoading = computed(() => {
    if (navStore.level === 'chapter') return navStore.activeStory?.isLoading;
    if (navStore.level === 'scene') return navStore.activeChapter?.isLoading;
    return false;
});

// **NEW**: Computed property for the timeline context
const timelineContext = computed(() => {
    if (navStore.level === 'chapter') return navStore.activeStory;
    if (navStore.level === 'scene') return navStore.activeChapter;
    return null;
});

const selectItem = (id: string) => {
    if (navStore.level === 'chapter') navStore.selectChapter(id);
    if (navStore.level === 'scene') navStore.selectScene(id);
}

// --- Generation Logic ---

function handleGenerate() {
    if (navStore.level === 'story') {
        const description = storiesViewRef.value?.newStoryDescription;
        if (!description) {
            alert('Please enter a description for the new story.');
            return;
        }
        console.log('--- GENERATE STORY ---');
        console.log({ description });
        // await contentStore.createNewStory(description);
    } else if (isTimelineView.value) {
        timelineViewRef.value?.generate();
    }
}

</script>

<style scoped>
.sidebar {
  width: 400px;
  flex-shrink: 0;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  background-color: var(--bg-color);
}

.generate-btn {
    width: 100%;
    padding: 1rem;
    font-size: 1.1rem;
    font-weight: 700;
    border-radius: var(--border-radius);
    cursor: pointer;
    transition: filter 0.2s;
    background-color: var(--main-color);
    color: white;
    border: none;
}
.generate-btn:hover { filter: brightness(110%); }

</style>
