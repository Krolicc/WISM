import { defineStore } from 'pinia'
import { ref, onMounted } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const theme = ref('light') // 'light' | 'dark'

  function toggleTheme() {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
    localStorage.setItem('theme', theme.value)
    document.documentElement.setAttribute('data-theme', theme.value)
  }

  // On app start, check for saved theme in localStorage or user's OS preference
  onMounted(() => {
    const savedTheme = localStorage.getItem('theme')
    const userPrefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches

    if (savedTheme) {
        theme.value = savedTheme
    } else if (userPrefersDark) {
        theme.value = 'dark'
    }

    document.documentElement.setAttribute('data-theme', theme.value)
  })

  return { theme, toggleTheme }
})
