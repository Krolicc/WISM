import { defineStore } from 'pinia'
import { ref } from 'vue'

// The sidebar can now show Projects or Chapters
export type SidebarView = 'PROJECTS' | 'CHAPTERS'

export const useNavigationStore = defineStore('navigation', () => {
  const sidebarView = ref<SidebarView>('PROJECTS')
  
  // This will now store the ID of the selected Chapter
  const activeChapterId = ref<number | null>(null)

  function showProjects() {
    sidebarView.value = 'PROJECTS'
    activeChapterId.value = null // Reset chapter selection
  }

  function showChapters() {
    sidebarView.value = 'CHAPTERS'
  }

  function setActiveChapterId(id: number | null) {
    activeChapterId.value = id
  }

  return {
    sidebarView,
    activeChapterId,
    showProjects,
    showChapters,
    setActiveChapterId,
  }
})
