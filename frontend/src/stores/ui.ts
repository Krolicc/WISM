import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useProjectsStore } from './projects'

export interface Tab {
  id: string // Unique ID, e.g., 'story' or 'plotpoint-5'
  title: string
  type: 'story' | 'plotpoint'
  projectId: number // To which project this tab belongs
  plotPointId?: number // Only for tabs of type 'plotpoint'
}

const SIDEBAR_MIN_WIDTH = 280;
const SIDEBAR_MAX_WIDTH = 600;

export const useUiStore = defineStore('ui', () => {
  // --- STATE ---
  const sidebarWidth = ref(320)
  const isResizing = ref(false)
  
  // A dictionary to hold tabs for each project
  const openTabsByProject = ref<Record<number, Tab[]>>({})
  const activeTabIdByProject = ref<Record<number, string>>({})

  const projectsStore = useProjectsStore()

  // --- GETTERS (for the ACTIVE project) ---
  const openTabs = computed(() => {
    const activeProjectId = projectsStore.activeProjectId
    return activeProjectId ? openTabsByProject.value[activeProjectId] || [] : []
  })

  const activeTab = computed(() => {
    const activeProjectId = projectsStore.activeProjectId
    if (!activeProjectId) return null
    const activeTabId = activeTabIdByProject.value[activeProjectId]
    return openTabs.value.find(t => t.id === activeTabId) || null
  })

  // --- ACTIONS ---
  function initializeTabsForProject(projectId: number) {
    if (!openTabsByProject.value[projectId]) {
      const storyTab: Tab = { id: `story-${projectId}`, title: 'Storyline', type: 'story', projectId };
      openTabsByProject.value[projectId] = [storyTab];
      activeTabIdByProject.value[projectId] = storyTab.id;
    }
  }

  function openTabForPlotPoint(plotPointId: number, title: string) {
    const activeProjectId = projectsStore.activeProjectId
    if (!activeProjectId) return;

    const tabId = `plotpoint-${plotPointId}`;
    const existingTab = openTabs.value.find(t => t.id === tabId);

    if (!existingTab) {
      const newTab: Tab = { id: tabId, title, type: 'plotpoint', projectId: activeProjectId, plotPointId };
      openTabsByProject.value[activeProjectId].push(newTab);
    }
    activeTabIdByProject.value[activeProjectId] = tabId;
  }

  function closeTab(tabId: string) {
    const activeProjectId = projectsStore.activeProjectId
    if (!activeProjectId) return;

    const tabs = openTabsByProject.value[activeProjectId]
    const tabIndex = tabs.findIndex(t => t.id === tabId)

    if (tabIndex === -1 || tabs[tabIndex].type === 'story') return; // Can't close the main story tab

    // Determine new active tab
    if (activeTabIdByProject.value[activeProjectId] === tabId) {
      activeTabIdByProject.value[activeProjectId] = tabs[tabIndex - 1].id;
    }

    tabs.splice(tabIndex, 1);
  }

  function setActiveTab(tabId: string) {
    if (projectsStore.activeProjectId) {
      activeTabIdByProject.value[projectsStore.activeProjectId] = tabId;
    }
  }
  
  function startResizing() {
    isResizing.value = true;
  }

  function stopResizing() {
    isResizing.value = false;
  }

  function handleResize(event: MouseEvent) {
    if (!isResizing.value) return;
    // 60px is the width of the new actions sidebar we will create
    const newWidth = event.clientX - 60;
    if (newWidth >= SIDEBAR_MIN_WIDTH && newWidth <= SIDEBAR_MAX_WIDTH) {
      sidebarWidth.value = newWidth;
    }
  }

  return {
    sidebarWidth,
    isResizing,
    openTabs,
    activeTab,
    initializeTabsForProject,
    openTabForPlotPoint,
    closeTab,
    setActiveTab,
    startResizing,
    stopResizing,
    handleResize,
  }
})
