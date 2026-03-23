import { ref, computed } from 'vue';
import { defineStore } from 'pinia';
import { useVerticalNavigationStore } from './vertical_navigation';
import { useContentManageStore } from './content_manage';
import { EnrichedStoryNode } from '../types';
import mockData from '../example_jsons/story-structure.json';

// --- TYPE DEFINITIONS ---

interface BaseMetadata {
  isTerminal?: boolean;
  nextChoiceNode?: string;
  joinNode?: string;
  previous_sequence: string | null;
}

export interface ListMetadata extends BaseMetadata {
  type: 'list';
}

export interface BranchMetadata extends BaseMetadata { }

export interface Branch {
  choice: string;
  metadata: BranchMetadata;
  sequence: string[];
}

export interface BranchContainer {
  metadata: { type: 'branch'; choiceQuestion: string; main_branche: string | null; };
  branches: Record<string, Branch>;
}

export interface ListContainer {
  metadata: ListMetadata;
  sequence: string[];
}

export type SequenceContainer = BranchContainer | ListContainer;
export type HorizontalSequences = Map<string, SequenceContainer>;
export type NodeToPathMap = Map<string, { choiceNodeId: string; pathId: string }>;

// --- UI-Facing Types ---

export type TimelineBranch = {
  type: 'branch';
  choiceNodeId: string;
  choiceQuestion: string;
  choices: { key: string; value: string }[];
  selectedPathId: string;
}

export type TimelineList = {
  type: 'list';
  sequence: EnrichedStoryNode[];
}

type NavigationStep = { choiceNodeId: string; selectedPathId: string };

// --- STORE DEFINITION ---

export const useHorizontalNavigationStore = defineStore('horizontalNavigation', () => {
  // --- STORES ---
  const vertNavStore = useVerticalNavigationStore();
  const contentManageStore = useContentManageStore();

  // --- STATE ---
  const horizontalSequences = ref<HorizontalSequences>(new Map(Object.entries(mockData.horizontalSequences)) as HorizontalSequences);
  const nodeToPathMap = ref<NodeToPathMap>(new Map(Object.entries(mockData.nodeToPathMap)));
  const navigationStack = ref<NavigationStep[]>([]);

  // --- COMPUTED ---

  const currentContext = computed((): (TimelineBranch | TimelineList)[] => {
    const timeline: (TimelineBranch | TimelineList)[] = [];
    let sequenceAccumulator: string[] = [];

    function enrichSequence(sequenceIds: string[]): EnrichedStoryNode[] {
      return sequenceIds
        .map(id => contentManageStore.getNode(id))
        .filter((node): node is EnrichedStoryNode => !!node)
        .map(node => ({
            ...node,
            parent: node.parentId,
        }));
    }

    function flushAccumulator() {
      if (sequenceAccumulator.length > 0) {
        timeline.push({
          type: 'list',
          sequence: enrichSequence(sequenceAccumulator),
        });
        sequenceAccumulator = [];
      }
    }

    for (const step of navigationStack.value) {
      const container = horizontalSequences.value.get(step.choiceNodeId);
      if (!container) continue;

      if (container.metadata.type === 'branch') {
        const branchData = container.branches[step.selectedPathId];
        if (branchData) {
          flushAccumulator();
          
          timeline.push({
            type: 'branch',
            choiceNodeId: step.choiceNodeId,
            choiceQuestion: container.metadata.choiceQuestion,
            choices: Object.entries(container.branches).map(([key, value]) => ({ key, value: value.choice })),
            selectedPathId: step.selectedPathId,
          });

          sequenceAccumulator.push(...branchData.sequence);

        }
      } else { 
        sequenceAccumulator.push(...(container as ListContainer).sequence);
      }
    }

    flushAccumulator();

    return timeline;
  });

  // --- ACTIONS ---

  function getSequenceMetadata(choiceNodeId: string, pathId: string): BaseMetadata | null {
      const container = horizontalSequences.value.get(choiceNodeId);
      if (!container) return null;
      if (container.metadata.type === 'list') {
          return (container as ListContainer).metadata;
      }
      if (container.metadata.type === 'branch') {
          return container.branches[pathId]?.metadata || null;
      }
      return null;
  }

  function buildForward(stack: NavigationStep[]) {
      let latestStep = stack[stack.length - 1];
      while (latestStep) {
          const metadata = getSequenceMetadata(latestStep.choiceNodeId, latestStep.selectedPathId);
          if (!metadata || metadata.isTerminal) break;

          let nextStep: NavigationStep | null = null;
          if (metadata.nextChoiceNode) {
              const branchContainer = horizontalSequences.value.get(metadata.nextChoiceNode) as BranchContainer;
              if (branchContainer && branchContainer.metadata.type === 'branch') {
                  const defaultPathId = branchContainer.metadata.main_branche || Object.keys(branchContainer.branches)[0];
                  if (defaultPathId) {
                      nextStep = { choiceNodeId: metadata.nextChoiceNode, selectedPathId: defaultPathId };
                  }
              }
          } else if (metadata.joinNode) {
              const pathInfo = nodeToPathMap.value.get(metadata.joinNode);
              if (pathInfo) {
                  nextStep = { choiceNodeId: pathInfo.choiceNodeId, selectedPathId: pathInfo.pathId };
              }
          }

          if (nextStep) {
              stack.push(nextStep);
              latestStep = nextStep;
          } else { break; }
      }
  }

  function navigateTo(nodeId: string | null) {
    if (nodeId === null) {
      navigationStack.value = [];
      return;
  }

    const newStack: NavigationStep[] = [];
    const pathInfo = nodeToPathMap.value.get(nodeId);

    if (!pathInfo) {
      navigationStack.value = []; 
      return;
  }

    let currentChoiceId: string | null = pathInfo.choiceNodeId;
    let currentPathId: string = pathInfo.pathId;
    
    while (currentChoiceId) {
        newStack.unshift({ choiceNodeId: currentChoiceId, selectedPathId: currentPathId });
        const metadata = getSequenceMetadata(currentChoiceId, currentPathId);
        const prevSeqId = metadata?.previous_sequence;

        if (prevSeqId) {
            const prevPathInfo = nodeToPathMap.value.get(prevSeqId);
            if (prevPathInfo) {
                currentChoiceId = prevPathInfo.choiceNodeId;
                currentPathId = prevPathInfo.pathId;
            } else {
                console.error(`Could not find path info for previous_sequence: ${prevSeqId}`);
                currentChoiceId = null;
            }
        } else {
            currentChoiceId = null;
        }
    }

    buildForward(newStack);
    navigationStack.value = newStack;
  }

  function makeChoice(choiceNodeId: string, selectedPathId: string) {
    const choiceIndex = navigationStack.value.findIndex(c => c.choiceNodeId === choiceNodeId);
    if (choiceIndex === -1) return;

    navigationStack.value[choiceIndex].selectedPathId = selectedPathId;
    navigationStack.value.splice(choiceIndex + 1);
    buildForward(navigationStack.value);
  }

  return {
    navigationStack,
    currentContext,
    navigateTo,
    makeChoice,
  };
});
