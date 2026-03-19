import { defineStore } from 'pinia';
import { ref, onBeforeUnmount } from 'vue';
import { useContentStore } from './content';
import { useToasts } from './toast';

export const useSocketStore = defineStore('socket', () => {
  const contentStore = useContentStore();
  const toastStore = useToasts();
  const socket = ref<WebSocket | null>(null);
  const isConnected = ref(false);
  const currentStoryId = ref<string | null>(null);

  const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || 'wss://8000-firebase-wism-1770010266998.cluster-4cmpbiopffe5oqk7tloeb2ltrk.cloudworkstations.dev';

  function disconnect() {
    if (socket.value) {
      socket.value.close();
      socket.value = null;
    }
    isConnected.value = false;
    currentStoryId.value = null;
  }

  function connect(storyId: string) {
    // If already connected to this story, do nothing
    if (isConnected.value && currentStoryId.value === storyId) return;
    
    // If connected to a different story, disconnect first
    if (socket.value) disconnect();

    currentStoryId.value = storyId;
    const url = `${WS_BASE_URL}/ws/${storyId}`;
    
    try {
      socket.value = new WebSocket(url);

      socket.value.onopen = () => {
        console.log(`WebSocket connected to story: ${storyId}`);
        isConnected.value = true;
      };

      socket.value.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          const { type, data, story_id } = payload;

          switch (type) {
            case 'STORY_UPDATED':
              contentStore.updateStoryInStore(data);
              toastStore.showToast("Chapter Generated");
              break;
            case 'CHAPTER_UPDATED':
              contentStore.updateChapterInStore(story_id, data);
              toastStore.showToast("Scene Generated");
              break;
            default:
              toastStore.showToast(`Unknown socket message type: ${type}`);
          }
        } catch (e) {
          console.error('Failed to parse WebSocket message:', e);
        }
      };

      socket.value.onclose = (event) => {
        isConnected.value = false;
        console.log('WebSocket disconnected', event.reason);
        // Optional: Implement reconnection logic here if needed
      };

      socket.value.onerror = (error) => {
        console.error('WebSocket error:', error);
        isConnected.value = false;
      };

    } catch (e) {
      console.error('Failed to establish WebSocket connection:', e);
    }
  }

  onBeforeUnmount(() => {
    disconnect();
  });

  return {
    isConnected,
    currentStoryId,
    connect,
    disconnect
  };
});