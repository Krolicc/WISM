import { defineStore } from 'pinia';
import { ref } from 'vue';
import { api } from '../services/api';
import type { Story, Chapter } from '../types/index';

export const useContentStore = defineStore('content', () => {
  const stories = ref<Story[]>([]);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  // --- Internal helper to handle loading and errors ---
  async function callApi<T>(apiCall: () => Promise<T>): Promise<T | null> {
    isLoading.value = true;
    error.value = null;
    try {
      return await apiCall();
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'An unknown error occurred.';
      return null;
    } finally {
      isLoading.value = false;
    }
  }

  // --- Store Update Actions (for real-time updates) ---

  function updateStoryInStore(story_id: string, updatedStory: Story) {
    const index = stories.value.findIndex(s => s.id === updatedStory.id);
    if (index !== -1) {
      stories.value[index] = updatedStory;
    }
  }

  function updateChapterInStore(story_id: string, updatedChapter: Chapter) {
    for (const story of stories.value) {
      if (story.id === story_id) {
        const chapterIndex = story.chapters.findIndex(c => c.id === updatedChapter.id);
        if (chapterIndex !== -1) {
          story.chapters[chapterIndex] = updatedChapter;
          return;
        }
      }
    }
  }

  // --- API-facing actions ---

  async function fetchAll() {
    await callApi(async () => {
      stories.value = await api.getAllStories();
    });
  }

  async function createAndGenerateStory(prompt: string) {
    const newStory = await callApi(() => api.generateStory(prompt));
    if (newStory) {
      // The API now returns the fully generated story, so we just add it.
      stories.value.push(newStory);
    }
  }

  async function regenerateFrame(frameId: string) {
    // const updatedFrame = await callApi(() => regenerateFrameAPI(frameId));
    // if (updatedFrame) {
    //   // Find and update the specific frame in the nested structure
    //   for (const story of stories.value) {
    //     for (const chapter of story.chapters) {
    //       const scene = chapter.scenes.find(s => s.frames.some(f => f.id === frameId));
    //       if (scene) {
    //         const frameIndex = scene.frames.findIndex(f => f.id === frameId);
    //         if (frameIndex !== -1) {
    //           scene.frames[frameIndex] = updatedFrame;
    //           return; // Exit once found and updated
    //         }
    //       }
    //     }
    //   }
    // }
  }

  return {
    stories,
    isLoading,
    error,
    fetchAll,
    createAndGenerateStory,
    regenerateFrame,
    updateStoryInStore,
    updateChapterInStore,
  };
});