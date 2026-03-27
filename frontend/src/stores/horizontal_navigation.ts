
import { ref, computed } from 'vue';
import { defineStore } from 'pinia';
import { useContentManageStore } from './content_manage';
import type { StoryNode } from '../types';

export type PreferredChoices = Record<string, string>;

export const useHorizontalNavigationStore = defineStore('horizontalNavigation', () => {
  const contentStore = useContentManageStore();
  const preferredChoices = ref<PreferredChoices>({});

  const isNodeReachable = (startNodeId: string, targetNodeId: string, choices: PreferredChoices): boolean => {
    const visited = new Set<string>();
    const queue: string[] = [startNodeId];
    while (queue.length > 0) {
      const currentId = queue.shift()!;
      if (currentId === targetNodeId) return true;
      if (visited.has(currentId)) continue;
      visited.add(currentId);
      const currentNode = contentStore.getNode(currentId);
      if (!currentNode) continue;
      let nextIds: string[] = [];
      if (currentNode.type === 'branchSet') {
        const choice = choices[currentNode.id] || (currentNode.next_ids ? currentNode.next_ids[0] : null);
        if (choice) nextIds = [choice];
      } else {
        nextIds = currentNode.next_ids || [];
      }
      for (const nextId of nextIds) {
        if (!visited.has(nextId)) {
          queue.push(nextId);
        }
      }
    }
    return false;
  };

  const makeChoice = (branchSetId: string, chosenPathId: string) => {
    const newChoices = { ...preferredChoices.value, [branchSetId]: chosenPathId };
    const story = contentStore.stories[0];
    if (!story) return;
    const currentActiveId = contentStore.activeNodeId;
    if (!currentActiveId) {
      // If there's no active node, just make the choice and set active node to the choice
      preferredChoices.value = newChoices;
      contentStore.navigateTo(chosenPathId);
      return;
    }
    // Check if the current active node is still reachable with the new choice
    const isReachable = isNodeReachable(story.id, currentActiveId, newChoices);
    if (isReachable) {
      // The path is still valid, just update the choices
      preferredChoices.value = newChoices;
    } else {
      // The active node is now on a dead path. We need to move the camera.
      // We'll set the active node to be the start of the branch the user just chose.
      preferredChoices.value = newChoices;
      contentStore.navigateTo(chosenPathId);
    }
  }

  const buildForward = computed((): StoryNode[] => {
    const path: StoryNode[] = [];
    if (!contentStore.activeNode) return [];
    
    let currentNode: StoryNode | undefined = contentStore.getNode(contentStore.activeNode.id);
    
    console.log(contentStore.activeNode)

    while (currentNode) {
      let nextNodeId: string | null = null;
      if (currentNode.type === 'branchSet') {
        nextNodeId = preferredChoices.value[currentNode.id] || (currentNode.next_ids ? currentNode.next_ids[0] : null);
      } else if (currentNode.next_ids && currentNode.next_ids.length == 1) {
        nextNodeId = currentNode.next_ids[0];
      }

      if (nextNodeId) {
        const nextNode = contentStore.getNode(nextNodeId);
        if (nextNode) {
          path.push(nextNode);
          currentNode = nextNode;
        } else { currentNode = undefined; }
      } else { currentNode = undefined; }
    }
    return path;
  });

  const buildBackward = computed((): StoryNode[] => {
    const path: StoryNode[] = [];
    if (!contentStore.activeNode) return [];

    let currentNode: StoryNode | undefined = contentStore.getNode(contentStore.activeNode.id);

    while (currentNode) {
      let prevNodeId: string | null = null;
      if (currentNode.prev_ids && currentNode.prev_ids.length > 0) {
        prevNodeId = currentNode.prev_ids[0];
      }

      if (prevNodeId) {
        const prevNode = contentStore.getNode(prevNodeId);
        if (prevNode) {
          path.push(prevNode);
          currentNode = prevNode;
        } else { currentNode = undefined; }
      } else { currentNode = undefined; }
    }
    return path.reverse();
  });

  const currentTimeline = computed((): StoryNode[] => {
    const timeline: StoryNode[] = [];
    const backwardPath = buildBackward.value;
    const forwardPath = buildForward.value;

    const fullPath = [...backwardPath];
    if (contentStore.activeNode) {
      fullPath.push(contentStore.activeNode);
    }
    fullPath.push(...forwardPath);

    for (const node of fullPath) {
      if (node.type === 'branchSet') {
        const selectedBranchId = preferredChoices.value[node.id] || (node.next_ids ? node.next_ids[0] : '');

        timeline.push({ ...node, selectedBranchId: selectedBranchId});
      } else {
        timeline.push(node);
      }
    }
    return timeline;
  });

  return {
    preferredChoices,
    currentTimeline,
    buildForward, 
    buildBackward,
    makeChoice,
  };
});
