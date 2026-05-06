<template>
  <div class="patterns-view">
    <div v-if="store.patterns.length > 0">
      <StylePatternCard 
        v-for="pattern in store.patterns" 
        :key="pattern.id" 
        :pattern="pattern"
      />
    </div>
    <div v-else class="no-results">
      <p>Здесь появятся результаты анализа вашего текста.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useStyleLibraryStore } from '../../stores/style_library';
import StylePatternCard from './StylePatternCard.vue';

const store = useStyleLibraryStore();
</script>

<style scoped>
.no-results {
  text-align: center;
  color: var(--sub-color);
  padding: 40px;
  border-radius: var(--border-radius);
  border: 2px dashed var(--border-color);
}

.patterns-view > div {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  flex-direction: column;
  gap: 1rem;
}
</style>
