import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useStoryStructuringStore, findBlock, findBlockPath, HIERARCHY } from './story-structuring';
import type { Block, BlockType } from '@/types/preprocessing';
import { cloneDeep } from 'lodash-es';

// --- Recursive helper to flatten blocks to a single text string --- //
function flattenBlocksToText(blocks: Block[]): string {
  return blocks.map(block => {
    const childText = block.children ? flattenBlocksToText(block.children) : '';
    const currentText = (block.text || '').trim();
    return (currentText + (childText ? '\n\n' + childText : '')).trim();
  }).join('\n\n');
}

function flattenBlock(block: Block): Block {
  const combinedText = flattenBlocksToText([block]);

  return {
    id: block.id,
    type: 'Scene',
    text: combinedText.trim(),
    color: block.color,
    children: [],
  }
}

function degradeBlock(block: Block): Block {
  const newBlock = cloneDeep(block);

  if (newBlock.type === 'Arc') {
      newBlock.type = 'Chapter';
  } else if (newBlock.type === 'Chapter') {
      newBlock.type = 'Scene';
  }
  
  if (newBlock.children?.length) {
      newBlock.children = newBlock.children.map(degradeBlock);
  }

  return newBlock;
}

export const useSelectionStore = defineStore('selection', () => {
  const storyStore = useStoryStructuringStore();

  const selectedBlockIds = ref(new Set<string>());

  // ... selectedBlocks and selectionMetadata computed properties remain unchanged ...
  const selectedBlocks = computed(() => {
    const selected: Block[] = [];
    selectedBlockIds.value.forEach(id => {
        const block = findBlock(storyStore.blocks, id);
        if (block) { selected.push(block); }
    });
    return selected;
  });

  const selectionMetadata = computed(() => {
    const ids = Array.from(selectedBlockIds.value);
    if (ids.length === 0) {
        return { isValidForMove: false };
    }

    const paths = ids.map(id => findBlockPath(storyStore.blocks, id)).filter(Boolean) as Block[][];

    // If any ID didn't resolve to a path, something is wrong.
    if (paths.length !== ids.length) {
        return { isValidForMove: false };
    }

    // An action is valid if no selected block is an ancestor of another selected block.
    // This prevents trying to move a folder into one of its own sub-folders.
    let isValid = true;
    for (let i = 0; i < paths.length; i++) {
        for (let j = 0; j < paths.length; j++) {
            if (i === j) continue;
            const pathI = paths[i]; // Potential ancestor
            const pathJ = paths[j]; // Potential descendant
            
            // Check if pathI is a prefix for pathJ (i.e., ancestor)
            if (pathJ.length > pathI.length && pathJ[pathI.length - 1].id === pathI[pathI.length - 1].id) {
                 const isAncestor = pathI.every((node, index) => node.id === pathJ[index].id);
                 if (isAncestor) {
                    isValid = false;
                    break;
                 }
            }
        }
        if (!isValid) break;
    }

    return { isValidForMove: isValid };
  });

  function clearSelection() {
    selectedBlockIds.value.clear();
  }

function toggleSelection({ blockId, isMultiSelect }: { blockId: string; isMultiSelect: boolean; }) {
    const currentSelection = selectedBlockIds.value;

    if (!isMultiSelect) {
      if (currentSelection.has(blockId) && currentSelection.size === 1) {
        // If the only selected item is clicked again, deselect it.
        currentSelection.clear();
      } else {
        // Otherwise, clear the old selection and start a new one.
        currentSelection.clear();
        currentSelection.add(blockId);
      }
      return;
    }

    // For multi-select, just toggle the item's presence in the set.
    if (currentSelection.has(blockId)) {
      currentSelection.delete(blockId);
    } else {
      currentSelection.add(blockId);
    }
  }
  // --- ACTION HANDLERS ---

  function transformBlocksForMove(sourceBlocks: Block[], targetId: string, position: 'before' | 'after' | 'prepend' | 'append'): Block[] {
    const targetPath = findBlockPath(storyStore.blocks, targetId);
    if (!targetPath) return sourceBlocks;

    const immediateTarget = targetPath[targetPath.length - 1];
    const sourceBlock = sourceBlocks[0]; 
    if (!sourceBlock) return []; // No source blocks

    let targetLevel: number;

    if (position === 'prepend' || position === 'append') {
        targetLevel = HIERARCHY[immediateTarget.type] - 1;
    } else {
        targetLevel = HIERARCHY[immediateTarget.type];
    }
    
    if (targetLevel < HIERARCHY.Scene) {
      targetLevel = HIERARCHY.Scene;
    }

    const sourceLevel = HIERARCHY[sourceBlock.type];

    if (sourceLevel <= targetLevel) {
        return sourceBlocks;
    }

    let transformed = cloneDeep(sourceBlocks);
    let levelsToDrop = sourceLevel - targetLevel;

    for (let i = 0; i < levelsToDrop; i++) {
        const currentTransformedType = transformed[0].type;
        
        if (HIERARCHY[currentTransformedType] <= HIERARCHY.Chapter) {
             transformed = transformed.map(flattenBlock);
             break;
        } else {
             transformed = transformed.map(degradeBlock);
        }
    }

    return transformed;
  }

  function handleMove(sourceBlocks: Block[], targetId: string, position: 'before' | 'after' | 'prepend' | 'append') {
    const transformedBlocks = transformBlocksForMove(sourceBlocks, targetId, position);

    const success = storyStore.insertBlocks(transformedBlocks, targetId, position);
    if (!success) {
      console.error("Move failed. A rollback mechanism should be implemented.");
    }
  }

  function handleMerge(sourceBlocks: Block[], targetId: string, position: 'prepend' | 'append') {
    const textToMerge = flattenBlocksToText(sourceBlocks);
    if (!textToMerge) return;

    const success = storyStore.appendTextToBlock(targetId, textToMerge, position === 'prepend' ? 'start' : 'end');
    if (!success) {
       console.error("Merge failed. Text could not be appended.");
    }
  }


  function executeMoveOrMerge(payload: {
    targetId: string;
    action: 'move' | 'merge';
    position: 'before' | 'after' | 'prepend' | 'append';
  }) {
    const { targetId, action, position } = payload;
    const sourceIds = new Set(selectedBlockIds.value);

    if (!sourceIds.size || sourceIds.has(targetId)) return;

    const sourceBlocks = storyStore.removeBlocks(sourceIds);
    if (sourceBlocks.length !== sourceIds.size) {
      console.error("Couldn't find all source blocks. Aborting.");
      return;
    }

    if (action === 'move') {
      handleMove(sourceBlocks, targetId, position);
    } else if (action === 'merge') {
      if (position !== 'prepend' && position !== 'append') {
        console.error("Merge action only supports 'prepend' or 'append'.");
        return;
      }
      handleMerge(sourceBlocks, targetId, position);
    }

    clearSelection();
  }

  return {
    selectedBlockIds,
    selectedBlocks,
    selectionMetadata,
    clearSelection,
    toggleSelection,
    executeMoveOrMerge,
  };
});
