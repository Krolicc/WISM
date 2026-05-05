<template>
  <button 
    class="flag-button"
    :class="{ 'active': isActive, 'inactive': isInactive }"
    v-tooltip-helper="flag.name"
  >
    <span v-html="flag.icon"></span>
  </button>
</template>

<script setup lang="ts">
import type { GenerationFlag } from '../../lib/generation-flags';

defineProps<{ 
  flag: GenerationFlag,
  isActive: boolean,
  isInactive: boolean,
}>();
</script>

<style scoped>
.flag-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background-color: var(--container-bg);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  cursor: pointer;
  transition: all 0.2s ease;
  padding: 0;
  color: var(--sub-color);
}

.flag-button:hover {
  background-color: var(--bg-color);
  border-color: var(--main-color);
  color: var(--main-color);
}

.flag-button.active {
  background-color: var(--main-color);
  border-color: var(--main-color);
  color: white;
}

.flag-button.inactive {
  opacity: .25;
  pointer-events: none;
}

.flag-button span {
  display: inherit; /* To make sure the SVG inside aligns well */
  align-items: inherit;
  justify-content: inherit;
}

.flag-button :deep(svg) {
  width: 22px;
  height: 22px;
}
</style>
