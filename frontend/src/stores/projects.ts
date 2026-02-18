import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Project, Chapter, Scene, Frame } from '../types/index'
import { useNavigationStore } from './navigation'

// Define the base URL for the API. 
// This is the public URL of your backend, which is forwarded by Cloud Workstation.
const API_BASE_URL = 'https://9000-firebase-wism-1770010266998.cluster-4cmpbiopffe5oqk7tloeb2ltrk.cloudworkstations.dev';

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

  async function createNewProject(prompt: string) {
    const response = await fetch(`${API_BASE_URL}/api/v1/stories`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'accept': 'application/json',
        },
        body: JSON.stringify({ title: prompt, description: prompt }),
    });
    const newProject = await response.json();
    projects.value.unshift(newProject);
    setActiveProject(newProject.id);

    const contentResponse = await fetch(`${API_BASE_URL}/api/v1/stories/${newProject.id}/generate_content`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        },
        body: JSON.stringify({ idea: prompt }),
    });
    const fullStory = await contentResponse.json();

    const project = projects.value.find(p => p.id === newProject.id);
    if (project) {
        project.chapters = fullStory.scenes.map((scene: any) => ({
            id: scene.id,
            title: scene.title,
            scenes: [], // Scenes will be fetched later
            isLoading: false,
        }));
        project.isLoading = false;
    }
  }

  async function generateScenesForChapter(projectId: number, chapterId: number) {
    const project = projects.value.find(p => p.id === projectId);
    if (!project) return;

    const chapter = project.chapters.find(c => c.id === chapterId);
    if (!chapter) return;

    chapter.isLoading = true;
    
    const response = await fetch(`${API_BASE_URL}/api/v1/scenes/${chapterId}/generate_panels`, {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
        },
    });
    const scenes = await response.json();

    chapter.scenes = scenes.map((scene: any) => ({
        id: scene.id,
        title: scene.description,
        frames: scene.panels.map((panel: any) => ({
            frame_id: panel.id,
            image_url: panel.image_url,
            narration: panel.narration,
        })),
    }));

    chapter.isLoading = false;
  }

  async function generateFramesForScene(projectId: number, chapterId: number, sceneId: number) {
    const project = projects.value.find(p => p.id === projectId);
    if (!project) return;
    const chapter = project.chapters.find(c => c.id === chapterId);
    if (!chapter) return;
    const scene = chapter.scenes.find(s => s.id === sceneId);
    if (!scene) return;

    scene.isLoading = true;

    const response = await fetch(`${API_BASE_URL}/api/v1/panels/${sceneId}/generate_image`, {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
        },
    });
    const frame = await response.json();

    scene.frames.push({
        frame_id: frame.id,
        image_url: frame.image_url,
        narration: frame.narration,
    });

    scene.isLoading = false;

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
