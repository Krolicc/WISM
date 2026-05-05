<template>
  <div class="branch-container">
    <div class="choice-block unselect">
      <p class="choice-question">
        <span v-if="item.question">{{ item.question }}</span>
        <span v-else class="placeholder-text">[Choice question not set]</span>
      </p>
      <div class="choices">
        <button
          v-for="(meta, node_id) in item.branches"
          :key="node_id"
          class="choice-button"
          :class="{ 'selected': node_id === item.selectedBranchId }"
          @click="handleChoice(node_id)"
        >
          <span v-if="meta.label">{{ meta.label }}</span>
          <span v-else class="placeholder-text">[Empty choice]</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { PropType } from 'vue';
import { useHorizontalNavigationStore } from '../../stores/horizontal_navigation';
import type { BranchSet } from '../../types';

// --- Props ---
const props = defineProps({
  item: {
    type: Object as PropType<BranchSet>,
    required: true
  }
});

// --- Store ---
const horizNavStore = useHorizontalNavigationStore();

// --- Methods ---
function handleChoice(newPathId: string) {
  if (newPathId !== props.item.selectedBranchId) {
    horizNavStore.makeChoice(props.item.id, newPathId);
  }
}
</script>

<style scoped>
.branch-container {
  border-left: 2px solid var(--accent-color-dimmed);
}

.choice-block {
  padding: 1rem 1rem;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.choice-question {
  margin: 0;
  color: var(--sub-color);
}

.choices {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
}

.choice-button {
  background-color: var(--bg-color-secondary);
  border: 1px solid var(--border-color);
  color: var(--text-color);
  padding: 0.4rem 0.8rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.2s ease;
  min-height: 34px; /* Ensure consistent height */
}

.choice-button:hover {
  color: var(--main-color);
  border-color: var(--main-color);
}

.choice-button.selected {
  background-color: var(--main-color);
  color: var(--bg-color);
  border-color: var(--main-color);
}

.placeholder-text {
  color: var(--sub-color);
  opacity: 0.8;
}
</style>
