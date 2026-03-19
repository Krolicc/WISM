<template>
  <button @click="themeStore.toggleTheme" class="theme-switcher" :title="`Switch to ${themeStore.theme === 'light' ? 'Dark' : 'Light'} Mode`">
    <span v-if="themeStore.theme === 'light'">🌙</span>
    <span v-else>☀️</span>
  </button>
</template>

<script setup lang="ts">
import { useThemeStore } from '../stores/theme'

const themeStore = useThemeStore()
</script>

<style scoped>
.theme-switcher {
  background-color: transparent;
  color: var(--text-color);
  border: none;
  width: 40px;
  height: 40px;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 1.25rem;
  padding: 0;
}
.theme-switcher:hover {
  background-color: var(--bg-color);
  filter: brightness(100%);
}
</style>
