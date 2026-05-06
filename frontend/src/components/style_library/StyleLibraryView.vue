<template>
  <div class="style-library-container">
    <!-- Левая колонка: Ввод и управление -->
    <div class="left-panel content-block">
      <h2>Анализ стиля</h2>
      <p>Вставьте текст для анализа. Система разобьет его на функциональные блоки, которые можно переиспользовать.</p>
      
      <textarea 
        v-model="textToAnalyze"
        placeholder="Вставьте ваш текст сюда..."
        :disabled="store.isLoading"
      ></textarea>
      
      <div class="panel-actions">
        <button @click="handleAnalysis" :disabled="store.isLoading || !textToAnalyze.trim()">
          {{ store.isLoading ? 'Анализ...' : 'Анализировать' }}
        </button>
        <button @click="clearAll" class="button-secondary" :disabled="store.isLoading">
          Очистить
        </button>
      </div>

      <div v-if="store.error" class="error-message">
        {{ store.error }}
      </div>

      <div v-if="store.isLoading" class="loading-indicator">
        <p>Пожалуйста, подождите. LLM анализирует структуру вашего текста...</p>
      </div>
    </div>

    <!-- Правая колонка: Результаты -->
    <div class="right-panel content-block">
      <AnalyzedPatternsView />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onUnmounted } from 'vue';
import { useStyleLibraryStore } from '../../stores/style_library';
import AnalyzedPatternsView from './AnalyzedPatternsView.vue';

const store = useStyleLibraryStore();
const textToAnalyze = ref('');

const handleAnalysis = () => {
  store.analyzeText(textToAnalyze.value);
};

const clearAll = () => {
  textToAnalyze.value = '';
  store.clearAnalyzedPatterns();
};

// Очищаем состояние, когда компонент уничтожается, чтобы не видеть старые результаты
onUnmounted(() => {
  store.clearAnalyzedPatterns();
});
</script>

<style scoped>
.style-library-container {
  display: flex;
  flex-grow: 1;
  gap: 2rem;
  height: 100%;
}

.left-panel, .right-panel {
  padding: 2rem;
  height: 100%;
  box-sizing: border-box;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.left-panel {
  flex-basis: 40%;
  flex-shrink: 0;
  gap: 1.5rem;
}

.left-panel h2,
.left-panel p {
  margin: 0;
}

.right-panel {
  flex-basis: 60%;
}

textarea {
  flex-grow: 1; 
  margin-bottom: 1rem;
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  resize: none; /* Отключаем возможность изменения размера */
  background-color: var(--bg-color);
  color: var(--text-color);
}

.panel-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-bottom: 1rem;
}

.error-message {
  color: #d9534f;
  margin-bottom: 1rem;
}

.loading-indicator {
  text-align: center; 
  margin: 2rem 0; 
  color: var(--sub-color);
}
</style>
