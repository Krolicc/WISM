
<template>
  <div class="action-type-picker">
    <div 
      v-for="action in actions"
      :key="action.type"
      class="action-icon-wrapper"
      :class="{ selected: modelValue === action.type }"
      :title="action.meta.name"
      @click.stop="$emit('update:modelValue', action.type)"
      >
      <div class="icon"
        v-html="action.meta.icon"
      ></div>
      
      <div v-if="action.meta.helperIcon" class="category-icon"
        v-html="action.meta.helperIcon"
      ></div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { PropType } from 'vue';
import type { ActionType } from '../../lib/action-meta';

interface ModifyingAction {
  type: ActionType;
  meta: {
    name: string;
    icon: string;
    helperIcon?: string;
  };
}

defineProps({
  actions: {
    type: Array as PropType<ModifyingAction[]>,
    required: true
  },
  modelValue: {
    type: String as PropType<ActionType>,
    required: true
  }
});

defineEmits(['update:modelValue']);
</script>

<style scoped>
.action-type-picker {
  display: flex;
  gap: 1rem;
}

.action-icon-wrapper {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 2px solid var(--border-color);
  position: relative;
  color: var(--sub-color);
}

.action-icon-wrapper:hover {
  background-color: var(--container-bg);
  transform: scale(1.1);
}

.action-icon-wrapper.selected {
  opacity: 0.25;
  pointer-events: none;
}

.action-icon-wrapper :deep(svg) {
  color: var(--sub-color);
}

.icon {
  overflow: hidden;
  height: 100%;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.category-icon {
  position: absolute;
  top: 0;
  left: 0;
  transform: translate(-50%, -50%);
}

</style>
