
import { defineStore } from 'pinia';
import { ref, onBeforeUnmount } from 'vue';
import { useContentManageStore, StoryNode } from './content_manage';
import { useToasts } from './toast';

export const useSocketStore = defineStore('socket', () => {
  const contentStore = useContentManageStore();
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
    if (isConnected.value && currentStoryId.value === storyId) return;
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
          const { type, data } = payload;

          if (type.endsWith('_UPDATED')) {
            // This assumes the `data` payload is a valid StoryNode object.
            // We will need to add the `addOrUpdateNode` action to the content store.
            (contentStore as any).addOrUpdateNode(data as StoryNode);

            const nodeType = (data as StoryNode).type || 'Item';
            const readableType = nodeType.charAt(0).toUpperCase() + nodeType.slice(1);
            toastStore.showToast(`${readableType} was updated.`);

          } else {
            console.warn(`Unknown socket message type: ${type}`);
            toastStore.showToast(`Received an unknown update from the server.`);
          }
        } catch (e) {
          console.error('Failed to parse WebSocket message:', e);
        }
      };

      socket.value.onclose = (event) => {
        isConnected.value = false;
        console.log('WebSocket disconnected', event.reason);
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
