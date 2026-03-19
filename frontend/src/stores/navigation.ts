import { defineStore } from 'pinia';
import { computed, ref } from 'vue';
import { useContentStore } from './content';
import type { Story, Chapter, Scene } from '../types/index';

export const useNavigationStore = defineStore('navigation', () => {
  const contentStore = useContentStore();

  // STATE
  const level = ref<'story' | 'chapter' | 'scene' | 'frame' | 'graph'>('story');
  const activeStoryId = ref<string | null>(null);
  const activeChapterId = ref<string | null>(null);
  const activeSceneId = ref<string | null>(null);

  // GETTERS
  const currentItemList = computed(()=> {
    if (level.value === 'chapter' && activeStory) return activeStory.value?.chapters || [];
    if (level.value === 'scene' && activeChapter) return activeChapter.value?.scenes || [];
    return [];
  });

  const parentId = computed((): string | null => {
    switch(level.value) {
      case 'chapter': return activeStoryId.value;
      case 'scene': return activeChapterId.value;
      case 'frame': return activeSceneId.value;
    }

    return null;
  })

  const activeStory = computed((): Story | null => {
    if (!activeStoryId.value) return null;
    return contentStore.stories.find(s => s.id === activeStoryId.value) || null;
  });

  const activeChapter = computed((): Chapter | null => {
    if (!activeChapterId.value || !activeStory.value) return null;
    return activeStory.value.chapters.find(c => c.id === activeChapterId.value) || null;
  });

  const activeScene = computed((): Scene | null => {
    if (!activeSceneId.value || !activeChapter.value) return null;
    return activeChapter.value.scenes.find(s => s.id === activeSceneId.value) || null;
  });

  // ACTIONS
  function selectStory(storyId: string) {
    activeStoryId.value = storyId;
    activeChapterId.value = null;
    activeSceneId.value = null;
    level.value = 'chapter';
  }

  function selectChapter(chapterId: string) {
    activeChapterId.value = chapterId;
    activeSceneId.value = null;
    level.value = 'scene';
  }

  function selectScene(sceneId: string) {
    activeSceneId.value = sceneId;
    // No change in level here; stays on 'scene' to show the list
  }

  function enterFrameEditor(sceneId: string) {
    selectScene(sceneId);
    level.value = 'frame';
  }

  function exitFrameEditor() {
    level.value = 'scene';
  }

  function goBackToStories() {
    level.value = 'story';
    activeStoryId.value = null;
    activeChapterId.value = null;
    activeSceneId.value = null;
  }

  function navigateStoryLevel(newLevel: 'story' | 'chapter' | 'scene' | 'frame' | 'graph') {
    level.value = newLevel;
  }

  return {
    currentItemList,
    level,
    parentId,
    activeStoryId,
    activeChapterId,
    activeSceneId,
    activeStory,
    activeChapter,
    activeScene,
    selectStory,
    selectChapter,
    selectScene,
    enterFrameEditor,
    exitFrameEditor,
    goBackToStories,
    navigateStoryLevel,
  };
});
