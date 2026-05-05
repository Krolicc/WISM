<template>
  <div class="flag-panel-container">
    <FlagButton
      v-if="activeFlag"
      class="active-flag-button"
      :flag="activeFlag"
      :is-active="true"
      @click="toggleExpand"
    />

    <Transition name="slide-up">
      <div v-if="isExpanded" class="flags">
        <FlagButton
          v-for="flag in Object.values(flags)"
          :key="flag.id"
          :flag="flag"
          :is-inactive="activeFlag == flag"
          @click.stop="selectFlag(flag.id)"
        />
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onUnmounted, PropType } from 'vue';
import { useUIStateStore } from '../../stores/ui_state';
import FlagButton from './FlagButton.vue';
import type { ActionFlagsMap, ActionFlag } from '../../lib/action-meta'; 

const props = defineProps({ 
  ownerId: {
    type: String,
    required: true,
  },
  activeFlag: Object as PropType<ActionFlag>,
  flags: {
    type: Object as PropType<ActionFlagsMap>,
    required: true,
  }
});

const emit = defineEmits<{
  (e: 'update:model-value', flagId: string): void, // Event to update the flag
}>();

const uiStateStore = useUIStateStore();
const isExpanded = ref(false);

watch(isExpanded, (newValue) => {
  if (newValue) {
    uiStateStore.setExpandedFlagPanel(props.ownerId);
  } else if (uiStateStore.expandedFlagPanelOwnerId === props.ownerId) {
    uiStateStore.setExpandedFlagPanel(null);
  }
});

onUnmounted(() => {
  if (uiStateStore.expandedFlagPanelOwnerId === props.ownerId) {
    uiStateStore.setExpandedFlagPanel(null);
  }
});

function selectFlag(flagId: string) {
  emit('update:model-value', flagId);
  isExpanded.value = false; // Collapse after selection
}

function toggleExpand() {
  isExpanded.value = !isExpanded.value;
}
</script>

<style scoped>
.flag-panel-container {
  position: relative; /* This is the positioning context for the absolute children */
  width: var(--button-size);
  height: var(--button-size);
  z-index: 10; /* Ensure the panel is above other timeline items */
  --gap: 8px;
  --button-size: 40px;
}

.flags {
  position: absolute;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  gap: var(--gap);
  z-index: -1; 
  top: calc(100% + var(--gap));
  right: 0
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.2s ease-out;
}

.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

</style>
