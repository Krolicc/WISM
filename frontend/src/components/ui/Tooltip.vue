<template>
  <transition name="fade">
    <div 
      v-if="tooltipStore.visible"
      class="tooltip-helper"
      :style="{ top: `${tooltipStore.position.top}px`, left: `${tooltipStore.position.left}px` }"
    >
      <span v-html="tooltipStore.content"></span>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { useTooltipStore } from './../../stores/tooltip';

const tooltipStore = useTooltipStore();
</script>

<style scoped>
.tooltip-helper {
  position: fixed; /* Use fixed to position relative to the viewport */
  background-color: var(--main-color);
  color: white;
  padding: 8px 12px;
  border-radius: var(--border-radius);
  font-size: 0.9rem;
  font-weight: 600;
  z-index: 1000;
  pointer-events: none; /* The tooltip itself should not be interactive */
  transform: translateY(-100%) translateX(-50%); /* Center the tooltip horizontally */
  white-space: pre-wrap; /* Allows newlines from v-html */
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-90%) translateX(-50%);
}
</style>
