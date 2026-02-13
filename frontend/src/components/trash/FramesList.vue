<template>
  <div class="frames-list-container">
    <div v-if="frames && frames.length > 0" class="frames-list">
      <div
        v-for="(frame, index) in frames"
        :key="frame.frame_id"
        class="frame-block"
        :class="{ active: activeFrameIndex === index }"
        @click="setActiveFrame(index)"
      >
        <img :src="frame.image_url" alt="Comic frame" class="frame-thumbnail" />
        <p class="frame-narration">{{ frame.narration }}</p>
      </div>
    </div>
    <div v-else class="no-frames-message">
      <p>No frames generated for this plot point yet.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, type PropType } from 'vue'
import type { Frame } from '../types'

defineProps({
  frames: {
    type: Array as PropType<Frame[]>,
    required: true
  }
})

const activeFrameIndex = ref<number | null>(null)

function setActiveFrame(index: number) {
  activeFrameIndex.value = index
}

</script>

<style scoped>
.frames-list-container {
  width: 100%;
}

.frames-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.frame-block {
  display: flex;
  align-items: center;
  background-color: var(--container-bg);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  padding: 1rem;
  cursor: pointer;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.frame-block:hover {
  border-color: var(--main-color);
}

.frame-block.active {
  border-color: var(--main-color);
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

.frame-thumbnail {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: var(--border-radius);
  margin-right: 1rem;
  flex-shrink: 0;
}

.frame-narration {
  margin: 0;
  font-size: 0.95rem;
  line-height: 1.5;
}

.no-frames-message {
  text-align: center;
  padding: 2rem;
  background-color: var(--container-bg);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow);
}
</style>
