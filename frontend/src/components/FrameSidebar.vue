<template>
  <div class="frame-sidebar" v-if="navStore.activeScene">
    <button @click="goBack" class="back-btn">BACK TO scene</button>
    <div class="scene-info content-block">
      <h2>{{ navStore.activeScene.title }}</h2>
      <p>{{ navStore.activeScene.description }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useNavigationStore } from '../stores/navigation';
const navStore = useNavigationStore();

function goBack() {
  navStore.exitFrameEditor();
}
</script>

<style scoped>
.frame-sidebar {
  height: fit-content;
  width: 280px;
  flex-shrink: 0;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.back-btn {
  background: none;
  border: none;
  background: var(--main-color);
  color: var(--bg-color);
  padding: 1.5rem;
  border-radius: var(--border-radius);
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
  font-weight: 700;
  font-size: 1.1rem;
}

.back-btn:hover {
  filter: brightness(110%); 
}

.scene-info {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.scene-info h2 {
  font-size: 1.5rem;
  margin: 0;
}

.scene-info p {
  color: var(--sub-color);
  font-size: 1rem;
  margin: 0;
}
</style>
