<template>
  <div class="insertion-point-wrapper" @mouseover="showButton = true" @mouseleave="showButton = false">
    <div class="timeline-line" :class="{ active: active }"></div>
    <button v-if="showButton" class="add-btn" @click="emitAdd">
      +
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const props = defineProps<{ 
  index: number,
  active?: boolean 
}>();
const emit = defineEmits<{(e: 'add', index: number): void }>();

const showButton = ref(false);

function emitAdd() {
  emit('add', props.index);
}
</script>

<style scoped>
.insertion-point-wrapper {
  position: relative;
  height: 24px; /* Height of the gap */
  padding-left: 40px; /* Match TimelineItem */
}

.timeline-line {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 19px; /* (40px - 2px) / 2 */
  width: 2px;
  background-color: var(--border-color);
  transition: background-color 0.2s;
}

.timeline-line.active {
  background-color: var(--main-color);
}

.add-btn {
  position: absolute;
  left: 9.5px; /* (40px - 21px) / 2 */
  top: 50%;
  transform: translateY(-50%);
  width: 21px;
  height: 21px;
  border-radius: 50%;
  background-color: var(--main-color);
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: bold;
  z-index: 3;
  box-shadow: 0 0 10px 2px var(--bg-color);
}

.insertion-point-wrapper:hover .timeline-line {
    background-color: var(--main-color);
}
</style>
