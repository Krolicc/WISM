
<template>
  <div class="frame-timeline-wrapper">
    <div class="timeline-track">
      <div
        v-for="(frame, index) in frames"
        :key="frame.id"
        class="timeline-item"
        :class="{ active: index === currentFrameIndex }"
        @click="selectFrame(index)"
      >
        <div class="thumbnail-wrapper">
          <img
            v-if="frame.image_url"
            :src="frame.image_url"
            alt="Frame thumbnail"
            class="timeline-thumbnail"
          />
          <div v-else class="no-image-placeholder">
            <span>{{ index + 1 }}</span>
          </div>
        </div>
        <div class="timeline-dot"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Frame } from '../../types';

defineProps<{
  frames: Frame[];
  currentFrameIndex: number;
}>();

const emit = defineEmits<{
  (e: 'select-frame', index: number): void;
}>();

function selectFrame(index: number) {
  emit('select-frame', index);
}
</script>

<style scoped>
.frame-timeline-wrapper {
  width: 100%;
  padding: 1rem 0;
  background-color: var(--container-bg-darker);
  border-top: 1px solid var(--border-color);
  overflow-x: auto;
  flex-shrink: 0;
  scrollbar-width: none; 
  -ms-overflow-style: none; 
}

.timeline-track {
  position: relative;
  display: flex;
  /* justify-content: space-evenly; */
  align-items: flex-end;
  gap: 2rem;
  padding: 1rem 4rem;
  min-width: max-content; 
}

/* The line running through the dots */
.timeline-track::before {
  content: '';
  position: absolute;
  left: 4rem; /* Match padding */
  right: 4rem; /* Match padding */
  bottom: 5px; /* Vertically center in the dots */
  height: 2px;
  background-color: var(--border-color);
  z-index: 0;
}

.timeline-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem; /* Space between thumbnail and dot */
  cursor: pointer;
  position: relative;
  z-index: 1;
}

.thumbnail-wrapper {
  width: 140px;
  height: 80px;
  border-radius: var(--border-radius-small);
  background-color: var(--container-bg);
  overflow: hidden;
  box-shadow: var(--shadow-small);
  transition: all 0.2s ease;
  opacity: 0.5; /* Dull by default */
}

.timeline-thumbnail {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: bold;
  color: var(--sub-color);
}

.timeline-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background-color: var(--border-color);
  transition: background-color 0.2s ease, transform 0.2s ease;
}

/* --- Active & Hover States --- */

.timeline-item:hover .thumbnail-wrapper {
  opacity: 0.8;
  transform: translateY(-5px);
}

.timeline-item.active .thumbnail-wrapper {
  opacity: 1;
  transform: translateY(-5px) scale(1.05);
  box-shadow: 0 0 0 3px var(--main-color), var(--shadow);
}

.timeline-item.active .timeline-dot {
  background-color: var(--main-color);
  transform: scale(1.2);
}

</style>
