<template>
  <transition name="hint-fade">
    <div v-if="state.visible" class="action-hint-container">
      <div v-for="(action, index) in state.actions" :key="index" class="action-line">
        <span class="keys">
          <template v-for="(keySequence, seqIndex) in action.keys" :key="seqIndex">
            <!-- This is the group of keys like ['Ctrl', 'L'] -->
            <span class="key-sequence">
              <template v-for="(key, keyIndex) in keySequence" :key="keyIndex">
                <kbd>{{ key }}</kbd>
                <span v-if="keyIndex < keySequence.length - 1" class="separator">+</span>
              </template>
            </span>
            <!-- Add a comma separator between key sequences -->
            <span v-if="seqIndex < action.keys.length - 1" class="sequence-separator">,</span>
          </template>
        </span>
        <span class="description">{{ action.description }}</span>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { actionHintState as state } from '../../stores/actionHint';
</script>

<style scoped>
.action-hint-container {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  background-color: var(--container-bg);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  padding: 1rem;
  box-shadow: var(--shadow);
  z-index: 1002;
  max-width: 350px;
}

.action-line {
  display: flex;
  align-items: center;
  margin-bottom: 0.75rem;
}

.action-line:last-child {
  margin-bottom: 0;
}

.keys {
  display: flex;
  align-items: center;
  gap: 0.5rem; /* This now serves as the gap for the comma separator */
  margin-right: 1rem;
}

.key-sequence {
  display: flex;
  align-items: center;
  gap: 0.25rem; /* small gap for '+' */
}

kbd {
  background-color: var(--bg-color);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  padding: 0.2rem 0.5rem;
  font-family: 'Inter', sans-serif;
  font-size: 0.85rem;
  font-weight: 600;
  min-width: 20px;
  text-align: center;
  box-shadow: 0 1px 1px rgba(0,0,0,0.1);
}

.separator, .sequence-separator {
  color: var(--sub-color);
}

.description {
  font-size: 0.9rem;
  color: var(--text-color);
}

/* --- Animation --- */
.hint-fade-enter-active,
.hint-fade-leave-active {
  transition: opacity 0.2s ease-in-out, transform 0.2s ease-in-out;
}

.hint-fade-enter-from,
.hint-fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>
