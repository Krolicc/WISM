<template>
  <div class="pattern-card">
    <div class="pattern-function">{{ pattern.function }}</div>
    <p class="pattern-text">{{ pattern.text }}</p>
    <div class="pattern-actions">
      <button @click="copyText">Копировать</button>
      <button @click="useAsTemplate">Использовать как шаблон</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { StylePattern } from '../../types/style-pattern';

defineProps<{ pattern: StylePattern }>();

const copyText = () => {
  // Logic to copy pattern.text to clipboard
  console.log('Text copied!');
};

const useAsTemplate = () => {
  // Logic to use this pattern as a template for new content
  console.log('Using as a template!');
};
</script>

<style scoped>
.pattern-card {
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  padding: 1rem;
}
.pattern-function {
  font-weight: bold;
  font-size: 1.1em;
  margin-bottom: 8px;
  color: #333;
}
.pattern-text {
  margin-bottom: 12px;
  color: #555;
}
.pattern-actions button {
  margin-right: 8px;
}
</style>
