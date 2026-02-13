import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Project, Chapter, Scene, Frame } from '../types/index'
import { useNavigationStore } from './navigation'

export const useProjectsStore = defineStore('projects', () => {
  const projects = ref<Project[]>([])
  const activeProjectId = ref<number | null>(null)

  const navigation = useNavigationStore()

  // --- COMPUTED --- //
  const activeProject = computed(() => {
    return projects.value.find(p => p.id === activeProjectId.value) || null
  })

  const activeChapter = computed(() => {
    if (!activeProject.value || navigation.activeChapterId === null) return null
    return activeProject.value.chapters.find(c => c.id === navigation.activeChapterId) || null
  })

  // --- ACTIONS --- //

  function setActiveProject(id: number) {
    activeProjectId.value = id
    navigation.setActiveChapterId(null) // Reset chapter selection when project changes
    navigation.showChapters() // Switch sidebar view to chapters
  }

  // MOCK API CALLS (replace with actual API calls)

  async function createNewProject(prompt: string) {
    const newProject: Project = {
      id: Date.now(),
      prompt,
      chapters: [],
      isLoading: true,
    }
    projects.value.unshift(newProject)
    setActiveProject(newProject.id)

    // --- Mock API Call: Generate Chapters ---
    console.log(`Generating chapters for prompt: "${prompt}"`);
    setTimeout(() => {
        const generatedChapters: Chapter[] = [
            { id: 1, title: 'The Discovery', scenes: [], isLoading: false },
            { id: 2, title: 'The Confrontation', scenes: [], isLoading: false },
            { id: 3, title: 'The Resolution', scenes: [], isLoading: false },
        ];
        const project = projects.value.find(p => p.id === newProject.id);
        if (project) {
            project.chapters = generatedChapters;
            project.isLoading = false;
        }
    }, 2000);
  }

  async function generateScenesForChapter(projectId: number, chapterId: number) {
    const project = projects.value.find(p => p.id === projectId);
    if (!project) return;

    const chapter = project.chapters.find(c => c.id === chapterId);
    if (!chapter) return;

    chapter.isLoading = true;
    console.log(`Generating scenes for Chapter: "${chapter.title}"`);
    
    // --- Mock API Call: Generate Scenes ---
    setTimeout(() => {
        const generatedScenes: Scene[] = [
            { id: 101, title: 'A Strange Signal', frames: [] },
            { id: 102, title: 'Investigating the Source', frames: [] },
        ];
        chapter.scenes = generatedScenes;
        chapter.isLoading = false;
    }, 2000);
  }

  async function generateFramesForScene(projectId: number, chapterId: number, sceneId: number) {
    const project = projects.value.find(p => p.id === projectId);
    if (!project) return;
    const chapter = project.chapters.find(c => c.id === chapterId);
    if (!chapter) return;
    const scene = chapter.scenes.find(s => s.id === sceneId);
    if (!scene) return;

    scene.isLoading = true;
    console.log(`Generating frames for Scene: "${scene.title}"`);

    // --- Mock API Call: Generate Frames ---
    setTimeout(() => {
        const generatedFrames: Frame[] = [
            { frame_id: String(Date.now() + 1), image_url: `https://picsum.photos/seed/${Math.random()}/400/225`, narration: 'A lone astronaut discovers a mysterious signal emanating from a desolate moon.' },
            { frame_id: String(Date.now() + 2), image_url: `https://picsum.photos/seed/${Math.random()}/400/225`, narration: 'The on-board computer flickers, displaying alien-like symbols.' },
        ];
        scene.frames = generatedFrames;
        scene.isLoading = false;
    }, 2000);

  }

  return {
    projects,
    activeProjectId,
    activeProject,
    activeChapter,
    setActiveProject,
    createNewProject,
    generateScenesForChapter,
    generateFramesForScene,
  }
})
