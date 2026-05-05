<template>
  <div class="timeline-container list-container"> 
    <!-- <TimelineInsertion
      :id=horizNavStore.currentTimeline[0]
      :level="vertNavStore.viewingLevel"
      :parentId=horizNavStore.currentTimeline[0].parent_id
      :isBefore=false
    /> -->

    <div v-for="(item, id) in horizNavStore.currentTimeline" :key="id">
      <TimelineBranch v-if="item.type == 'branchSet'" :item="item" />
      <TimelineItem 
        v-else
        @contextmenu.prevent="contextMenuHandle($event, item)"
        :item="item" 
        class="unselect"
        @openContextMenu="contextMenuHandle($event, item)"
      />

      <InsertionPoint 
        @add="handlePointAdd(item.id)"
      />

      <!-- <TimelineInsertion
        :class="{ dimmed: uiStateStore.expandedFlagPanelOwnerId == item.id }"
        :id="item.id"
        :level="vertNavStore.viewingLevel"
        :parentId="item.parent_id"
        :isBefore=true
      /> -->
    </div>

    <!-- <div v-if="listData.isLoading" class="spinner-message">
       🌀 Loading content...
    </div> -->
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useHorizontalNavigationStore } from '../../stores/horizontal_navigation';
import { useVerticalNavigationStore } from '../../stores/vertical_navigation';
import { useOrchestrationManageStore } from '../../stores/orchestration_manage';
import { useContextMenuStore, type ContextMenuItem } from '../../stores/context_menu';
import { ACTION_META, getExpActions, ActionType } from '../../lib/action-meta';
import { useUIStateStore } from '../../stores/ui_state';
import TimelineBranch from './TimelineBranch.vue';
import InsertionPoint from './InsertionPoint.vue';
import TimelineItem from './TimelineItem.vue';
import type { StoryNode } from '../../types';

// --- Stores ---
const vertNavStore = useVerticalNavigationStore();
const horizNavStore = useHorizontalNavigationStore();
const orchManageStore = useOrchestrationManageStore();
const contextMenuStore = useContextMenuStore();
const uiStateStore = useUIStateStore();

// --- State ---
const contextMenuItem = ref<StoryNode | null>(null);


function handlePointAdd(id: string, isParent: boolean = false) {
  orchManageStore.createManualNode(vertNavStore.viewingLevel, id, isParent);
}

function contextMenuHandle(event: MouseEvent, item: StoryNode) {
  contextMenuItem.value = item;

  showMenuFromButton(event);
}

const getContextMenuItems = computed((): ContextMenuItem[] => {
  if (contextMenuItem.value == null) return []

  const expActions = getExpActions();
  return expActions.map(action => {
    let actionCallback = () => console.log(`Action ${action.type} not implemented for ${contextMenuItem.value.id}`);
    
    // Here we map our specific action type to the store function
    if (action.type === 'alternate_node') {
      actionCallback = () => orchManageStore.createBranchFromNode(contextMenuItem.value.id);
    }

    return {
      id: action.type,
      text: action.meta.name,
      action: actionCallback,
      // disabled: item.someCondition // Future-proofing
    };
  });
});

const contextMenuConfig = computed(() => {
  if (contextMenuItem.value?.type === 'branchSet') return []; 

  return getContextMenuItems.value;
});

function showMenuFromButton(event: MouseEvent) {
  const buttonElement = event.currentTarget as HTMLElement;
  const rect = buttonElement.getBoundingClientRect();
  contextMenuStore.open({
    items: contextMenuConfig,
    position: { x: rect.left, y: rect.bottom + 5 },
    placement: 'bottom-start'
  });
}


// --- Exposed generate function for parent ---
async function generate() {
  try {
    // Pass the story ID to the commitActions function
    const storyId = vertNavStore.breadcrumbs.find(b => b.type === 'story')?.id;
    if (storyId) {
      // await commitActions(storyId);
    } else {
      console.error("Generation failed: Could not find story ID.");
    }
  } catch (error) {
    console.error("Generation failed:", error);
  }
}

defineExpose({ generate });

</script>

<style scoped>
.dimmed {
  opacity: 0.05;
}

.timeline-container { 
  overflow-y: auto; 
  flex-grow: 1; 
  overflow-x: hidden; 
  padding: 0.5rem 1rem;
  scrollbar-width: none; 
  -ms-overflow-style: none;
}

.spinner-message { 
  padding: 1rem; 
  text-align: center; 
  color: var(--sub-color); 
}
</style>
