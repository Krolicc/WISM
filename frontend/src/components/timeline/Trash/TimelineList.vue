<template>
  <div v-if="items.length !== 0">
    <TimelineInsertion
      :id=items[0]
      :level="vertNavStore.viewingLevel"
      :parentId=items[0].parentId
      :isBefore=false
    />

    <div v-for="item in items" :key="item.id">
      <TimelineItem :item="item" class="unselect"/>

      <TimelineInsertion
        :class="{ dimmed: uiStateStore.expandedFlagPanelOwnerId == item.id }"
        :id="item.id"
        :level="vertNavStore.viewingLevel"
        :parentId="item.parentId"
        :isBefore=true
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, defineAsyncComponent, PropType } from 'vue';
import { useContentManageStore } from '../../stores/content_manage';
import { useVerticalNavigationStore } from '../../stores/vertical_navigation';
import { useUIStateStore } from '../../stores/ui_state';
import type { TimelineList } from '../../stores/horizontal_navigation';
import type { EnrichedStoryNode } from '../../types/index';

// --- Components ---
const TimelineItem = defineAsyncComponent(() => import('./TimelineItem.vue'));
const TimelineInsertion = defineAsyncComponent(() => import('./TimelineInsertion.vue'));

// --- Props ---
const props = defineProps({
  item: {
    type: Object as PropType<TimelineList>,
    required: true,
  },
});

// --- Stores ---
const contentStore = useContentManageStore();
const vertNavStore = useVerticalNavigationStore();
const uiStateStore = useUIStateStore();

// --- Computed ---
const items = computed(() => {
  return props.item.sequence
    .map(item => contentStore.getNode(item.id))
    .filter((node): node is EnrichedStoryNode => node !== undefined);
});
</script>

<style scoped>
.dimmed {
  opacity: 0.05;
}
</style>
