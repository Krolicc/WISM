<template>
  <div class="timeline-container list-container">
    <!-- Top insertion area -->
    <InsertionPoint
      v-if="!getAction(0, 'generate')" 
      :index="0"
      @add="queueInsertion(0, undefined, navStore.currentItemList[0]?.id)"
    />
    <InsertionForm 
      v-else
      :action="getAction(0, 'generate')"
      @remove="removeAction(0, 'generate')" 
    />

    <div v-for="(item, index) in navStore.currentItemList" :key="item.id">
      <TimelineItem 
        :item="item"
        :index="index" 
        :active="item.id === activeItemId"
        :is-selected="isActionQueuedForItem(item.id, 'regenerate')" 
        :is-deleted="isActionQueuedForItem(item.id, 'delete')"
        :is-interactive="isNodeInteractive(index)"
        :flag="(getAction(index, 'regenerate') as RegenerateAction)?.params.flag"
        @update:flag="(flagId) => updateFlag(index, flagId)"
        @toggle-regenerate="toggleRegenerateAction(index, item.id)"
        @toggle-delete="toggleDeleteAction(index, item.id)"
        @select-item="selectItem"
      />

      <!-- Insertion area below item -->
      <InsertionPoint 
        v-if="!getAction(index + 1, 'generate')" 
        :index="index + 1" 
        @add="queueInsertion(index + 1, item.id, navStore.currentItemList[index + 1]?.id)"
        :active="false"
      />
      <!-- isLineActive(index) -->
      <InsertionForm 
        v-else 
        :action="getAction(index + 1, 'generate')"
        @remove="removeAction(index + 1, 'generate')"
      />
    </div>
    <div v-if="isLoading" class="spinner-message">
      <!-- 🌀 {{ isProcessing ? 'Applying changes...' : 'Loading content...' }} -->
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineAsyncComponent } from 'vue';
import { GenerateAction, RegenerateAction, useOrchestrationStore } from '../../stores/orchestration';
import { useNavigationStore } from '../../stores/navigation';

// --- Stores ---
const navStore = useNavigationStore();
const {
  getAction,
  queueInsertion,
  removeAction,
  isActionQueuedForItem,
  isNodeInteractive,
  toggleRegenerateAction,
  toggleDeleteAction,
  commitActions,
} = useOrchestrationStore();

// --- Components ---
const InsertionPoint = defineAsyncComponent(() => import('./InsertionPoint.vue'));
const InsertionForm = defineAsyncComponent(() => import('./InsertionForm.vue'));
const TimelineItem = defineAsyncComponent(() => import('./TimelineItem.vue'));

// --- Props & Emits ---
const props = defineProps<{ 
    activeItemId: string | null,
    isLoading: boolean,
}>();

const emit = defineEmits<{(e: 'select', id: string): void}>();

// --- Computed properties to link UI with the store ---

// const isLineActive = (index: number) => { if (props.items.length < index + 2) return false; return isRegenerating(props.items[index]?.id) && isRegenerating(props.items[index + 1]?.id); };

// --- Action Dispatchers (The UI now calls these functions) ---

const updateFlag = (index: number, flagId: string) => {
  const action = getAction(index, 'regenerate') as RegenerateAction
  action.params.flag = flagId
}

const selectItem = (id: string) => {
  emit('select', id);
};


// --- The simplified, single-purpose generate function ---
async function generate() {
  try {
    await commitActions();
    // Optionally show a success toast
  } catch (error) {
    console.error("Generation failed:", error);
    // Optionally show an error toast
  }
}

// Expose the generate function to the parent component
defineExpose({ generate });

</script>

<style scoped>
.timeline-container { overflow-y: auto; flex-grow: 1; overflow-x: hidden; }
.spinner-message { padding: 1rem; text-align: center; color: var(--sub-color); }
</style>
