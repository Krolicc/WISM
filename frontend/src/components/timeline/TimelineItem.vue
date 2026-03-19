<template>
  <div 
    class="timeline-item" 
    @mouseover="showDelete = true" 
    @mouseleave="showDelete = false"
  >
    <!-- Timeline Node (now a flex item) -->
    <div class="timeline-node">
        <div 
            class="timeline-circle"
            :class="{ selected: props.isSelected, interactive: props.isInteractive }"
            @click.stop="emit('toggle-regenerate', item.id)"
        >
            <span>{{ index + 1 }}</span>
        </div>
    </div>

    <!-- Item Content -->
    <div class="item-block" :class="{ active: active }" @click.stop="emit('select-item', item.id)">
        <h4 class="item-title">{{ item.title }}</h4>
        <span v-if="item.isLoading" class="spinner">🌀</span>
    </div>

    <!-- Flag Panel Wrapper -->
    <div v-if="props.isSelected || showDelete || props.isDeleted" class="flag-panel-wrapper">
      <FlagPanel v-if="props.isSelected" :model-value="flag" @update:model-value="emitUpdateFlag" />
      <button v-else @click.stop="emit('toggle-delete', item.id)" class="delete-item-btn" :class="{active: props.isDeleted}">
        <svg 
          xmlns="http://www.w3.org/2000/svg" 
          width="20" 
          height="20" 
          viewBox="0 0 24 24" 
          fill="none" 
          stroke="currentColor" 
          stroke-width="2" 
          stroke-linecap="round" 
          stroke-linejoin="round"
          class="delete-icon"
        >
          <polyline points="3 6 5 6 21 6"></polyline>
          <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import FlagPanel from '../ui/FlagPanel.vue';

const props = defineProps<{ 
    item: any,
    index: number,
    active: boolean,
    isSelected: boolean, 
    isDeleted: boolean, 
    isInteractive: boolean,
    flag: string, // The active flag for this item
}>();

const emit = defineEmits<{
  (e: 'update:flag', flagId: string): void, // Event to update the flag
  (e: 'select-item', id: string): void,
  (e: 'toggle-regenerate', itemId: string): void,
  (e: 'toggle-delete', itemId: string): void
}>();

const showDelete = ref(false);

function emitUpdateFlag(flagId: string) { emit('update:flag', flagId); }

</script>

<style scoped>
.timeline-item {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 5px 0;
    position: relative; /* Context for the line if ever needed */
}

.timeline-node {
    /* No more absolute positioning */
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    width: 40px;
}

.timeline-circle {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    border: 2px solid var(--border-color);
    color: var(--sub-color);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    font-size: 0.9rem;
    cursor: pointer;
    transition: all 0.2s;
}

.timeline-circle.interactive, .timeline-circle:hover {
    border-color: var(--main-color);
}

.timeline-circle:hover {
    transform: scale(1.1);
}

.timeline-circle.selected {
    background-color: var(--main-color);
    border-color: var(--main-color);
    color: white;
}

.item-block {
  background-color: var(--container-bg);
  border-radius: var(--border-radius);
  padding: 1rem 1.25rem;
  cursor: pointer;
  transition: border-color 0.2s;
  flex: 1 1 auto;
  min-width: 0; 
}

.item-block.active { 
  color: var(--main-color);
}

.item-title { 
  font-size: 1rem; 
  font-weight: 600; 
  margin: 0; 
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.flag-panel-wrapper {
  /* This is now a simple flex item. All positioning logic moves to FlagPanel.vue */
  flex-shrink: 0;
}

.delete-item-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: none;
  border-radius: var(--border-radius);
  cursor: pointer;
  transition: all 0.2s ease;
  padding: 0;
}

.delete-item-btn:hover,
.delete-item-btn.active {
  background: var(--main-color-red);
}

.delete-item-btn:hover .delete-icon,
.delete-item-btn.active .delete-icon{
  color: var(--bg-color);
}

.spinner { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
