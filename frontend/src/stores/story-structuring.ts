import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { v4 as uuidv4 } from 'uuid';
import type { Block, BlockType, BlockStyle } from '@/types/preprocessing';
import { ARC_COLORS, generateShades, createBlockStyle } from '/src/utils/colors';
import { cloneDeep } from 'lodash-es';

const initialText = `Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non risus. Suspendisse lectus tortor, dignissim sit amet, adipiscing nec, ultricies sed, dolor. Cras elementum ultrices diam. Maecenas ligula massa, varius a, semper congue, euismod non, mi. Proin porttitor, orci nec nonummy molestie, enim est eleifend mi, non fermentum diam nisl sit amet erat. Duis semper. Duis arcu massa, scelerisque vitae, consequat in, pretium a, enim. Pellentesque congue. Ut in risus volutpat libero pharetra tempor. Cras vestibulum bibendum augue. Praesent egestas leo in pede. Praesent blandit odio eu enim. Pellentesque sed dui ut augue blandit sodales. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Aliquam nibh. Mauris ac mauris sed pede pellentesque fermentum. Maecenas adipiscing ante non diam.`

export const HIERARCHY: Record<BlockType, number> = {
  Arc: 3,
  Chapter: 2,
  Scene: 1,
};

function escapeRegExp(string: string) {
  return string.replace(/[.*+?^${}()|[\\]\\]/g, '\\$&');
}

// --- EXPORTED HELPERS --- //
export function findBlock(nodes: Block[], id: string): Block | null {
    for (const node of nodes) {
        if (node.id === id) return node;
        if (node.children) {
            const found = findBlock(node.children, id);
            if (found) return found;
        }
    }
    return null;
}

export function removeBlocksRecursive(nodes: Block[], idsToRemove: Set<string>): Block[] {
  const removed: Block[] = [];

  // Iterate backwards to safely splice while looping
  for (let i = nodes.length - 1; i >= 0; i--) {
    const node = nodes[i];
    if (idsToRemove.has(node.id)) {
      // Using cloneDeep to ensure the moved block is a new object
      removed.unshift(cloneDeep(node)); // unshift to preserve original order
      nodes.splice(i, 1);
    } else if (node.children?.length) {
      // Recursively search in children
      const nestedRemoved = removeBlocksRecursive(node.children, idsToRemove);
      removed.unshift(...nestedRemoved);
    }
  }
  return removed;
}

export function findBlockPath(nodes: Block[], id: string, path: Block[] = []): Block[] | null {
  for (const node of nodes) {
    const currentPath = [...path, node];
    if (node.id === id) return currentPath;
    if (node.children) {
      const foundPath = findBlockPath(node.children, id, currentPath);
      if (foundPath) return foundPath;
    }
  }
  return null;
}

function buildPartialTree(
  path: Block[],
  ancestorIndex: number,
  sourceBlock: Block,
  leafText: string,
  part: 'before' | 'after'
): Block | null {
  if (!leafText.trim()) return null;

  let lastNode: Block = {
      id: uuidv4(),
      type: sourceBlock.type,
      text: leafText,
      color: sourceBlock.color,
      children: []
  };

  for (let i = path.length - 2; i >= ancestorIndex; i--) {
    const parent = path[i];
    const child = path[i + 1];
    const childIndex = parent.children.findIndex(c => c.id === child.id);

    const newParent: Block = {
      id: uuidv4(),
      type: parent.type,
      text: parent.text,
      color: parent.color,
      children: []
    };

    if (part === 'before') {
      const siblingsBefore = parent.children.slice(0, childIndex);
      newParent.children.push(...cloneDeep(siblingsBefore), lastNode);
    } else { 
      const siblingsAfter = parent.children.slice(childIndex + 1);
      newParent.children.push(lastNode, ...cloneDeep(siblingsAfter));
    }
    lastNode = newParent;
  }
  return lastNode;
}

export const useStoryStructuringStore = defineStore('story-structuring', () => {
  const blocks = ref<Block[]>([
    {
      id: uuidv4(),
      type: 'Arc',
      text: initialText,
      color: createBlockStyle(ARC_COLORS[0]),
      children: [],
    },
  ]);

  const arcCount = computed(() => blocks.value.filter(b => b.type === 'Arc').length);

  function appendTextToBlock(blockId: string, textToAppend: string, at: 'start' | 'end'): boolean {
    const block = findBlock(blocks.value, blockId);
    if (!block) {
      console.error("Target block for merge not found:", blockId);
      return false;
    }

    if (at === 'start') {
      block.text = textToAppend + (block.text ? '\\n\\n' + block.text : '');
    } else {
      block.text = (block.text ? block.text + '\\n\\n' : '') + textToAppend;
    }
    return true;
  }

  function removeBlocksRecursive(nodes: Block[], idsToRemove: Set<string>): Block[] {
    const removed: Block[] = [];

    // Iterate backwards to safely splice while looping
    for (let i = nodes.length - 1; i >= 0; i--) {
      const node = nodes[i];
      if (idsToRemove.has(node.id)) {
        // Using cloneDeep to ensure the moved block is a new object
        removed.unshift(cloneDeep(node)); // unshift to preserve original order
        nodes.splice(i, 1);
      } else if (node.children?.length) {
        // Recursively search in children
        const nestedRemoved = removeBlocksRecursive(node.children, idsToRemove);
        removed.unshift(...nestedRemoved);
      }
    }
    return removed;
  }
  
  function insertBlocks(sourceBlocks: Block[], targetId: string, position: 'before' | 'after' | 'prepend' | 'append'): boolean {
      const targetPath = findBlockPath(blocks.value, targetId);
      if (!targetPath) {
        console.error("Target block not found for insertion.");
        return false;
      }

      const targetNode = targetPath[targetPath.length - 1];

      // Case 1: Inserting into a parent (prepend/append)
      if (position === 'prepend' || position === 'append') {
          targetNode.children = position === 'prepend' 
              ? [...sourceBlocks, ...targetNode.children]
              : [...targetNode.children, ...sourceBlocks];
          return true;
      }

      // Case 2: Inserting next to a sibling (before/after)
      const targetParent = targetPath.length > 1 ? targetPath[targetPath.length - 2] : null;
      const targetCollection = targetParent ? targetParent.children : blocks.value;
      const targetIndex = targetCollection.findIndex(b => b.id === targetId);

      if (targetIndex === -1) {
        console.error("Target block not found in its collection.");
        return false;
      }

      const insertionIndex = position === 'before' ? targetIndex : targetIndex + 1;
      targetCollection.splice(insertionIndex, 0, ...sourceBlocks);
      return true;
  }

  function getNewBlockStyle(newBlockType: BlockType, parent: Block | null, index?: number): BlockStyle {
    let hexColor: string;

    const arcIndex = (parent?.type === 'Arc') 
        ? blocks.value.findIndex(b => b.id === parent.id)
        : arcCount.value;

    if (!parent) { // New top-level Arc
      hexColor = ARC_COLORS[arcCount.value % ARC_COLORS.length];
    } else {
      const parentArc = (parent.type === 'Arc') 
          ? parent 
          : findBlockPath(blocks.value, parent.id)?.find(p => p.type === 'Arc');

      switch (newBlockType) {
          case 'Arc':
              hexColor = ARC_COLORS[index !== undefined ? index % ARC_COLORS.length : arcCount.value % ARC_COLORS.length];
              break;
          case 'Chapter': {
              const arcColor = parentArc?.color.solid || ARC_COLORS[0];
              const palette = generateShades(arcColor, 5);
              const chapterIndex = index !== undefined ? index : parentArc?.children?.length || 0;
              hexColor = palette[chapterIndex % palette.length];
              break;
          }
          case 'Scene':
              hexColor = parent.color.solid;
              break;
      }
    }
    return createBlockStyle(hexColor);
  }

  function createBlock(sourceBlockId: string, selectedText: string, newBlockType: BlockType) {
    const path = findBlockPath(blocks.value, sourceBlockId);
    if (!path) return;

    const sourceBlockLevel = HIERARCHY[path[path.length - 1].type];
    const newBlockLevel = HIERARCHY[newBlockType];

    if (newBlockLevel < sourceBlockLevel) {
      handleNesting(path, selectedText, newBlockType);
    } else if (newBlockLevel === sourceBlockLevel) {
      handleSameLevelSplitting(path, selectedText, newBlockType);
    } else {
      handleElevation(path, selectedText, newBlockType);
    }
  }

  function handleNesting(path: Block[], selectedText: string, newBlockType: BlockType) {
    const sourceBlock = path[path.length - 1];
    const escapedSelectedText = escapeRegExp(selectedText);
    const [beforeText, afterText] = sourceBlock.text.split(escapedSelectedText).map(t => t.trim());

    const finalChildren: Block[] = [];
    const residualBlockType = sourceBlock.type === 'Arc' ? 'Chapter' : 'Scene';

    if (beforeText) finalChildren.push({ id: uuidv4(), type: residualBlockType, text: beforeText, children: [], color: getNewBlockStyle(residualBlockType, sourceBlock, 0) });

    let childCount = beforeText ? 1 : 0;

    if (sourceBlock.type === 'Arc' && newBlockType === 'Scene') {
      const newChapterStyle = getNewBlockStyle('Chapter', sourceBlock, childCount);
      const sceneBlock: Block = { id: uuidv4(), type: 'Scene', text: selectedText, children: [], color: newChapterStyle };
      finalChildren.push({ id: uuidv4(), type: 'Chapter', text: 'New Chapter', children: [sceneBlock], color: newChapterStyle });
    } else {
      finalChildren.push({ id: uuidv4(), type: newBlockType, text: selectedText, children: [], color: getNewBlockStyle(newBlockType, sourceBlock, childCount) });
    }
    childCount++;

    if (afterText) finalChildren.push({ id: uuidv4(), type: residualBlockType, text: afterText, children: [], color: getNewBlockStyle(residualBlockType, sourceBlock, childCount) });
    
    sourceBlock.children = finalChildren;
    sourceBlock.text = sourceBlock.type === 'Arc' ? 'New Arc Title' : 'New Chapter Title';
  }

  function handleSameLevelSplitting(path: Block[], selectedText: string, newBlockType: BlockType) {
    const sourceBlock = path[path.length - 1];
    const parent = path.length > 1 ? path[path.length - 2] : null;
    const targetArray = parent ? parent.children : blocks.value;

    const escapedSelectedText = escapeRegExp(selectedText);
    const [beforeText, afterText] = sourceBlock.text.split(escapedSelectedText).map(t => t.trim());

    const sourceIndex = targetArray.findIndex(b => b.id === sourceBlock.id);
    if (sourceIndex === -1) return;

    const newSequence: Block[] = [];

    if (beforeText) newSequence.push({ id: uuidv4(), type: sourceBlock.type, text: beforeText, children: [], color: sourceBlock.color });
    newSequence.push({ id: uuidv4(), type: newBlockType, text: selectedText, children: [], color: getNewBlockStyle(newBlockType, parent) });
    if (afterText) newSequence.push({ id: uuidv4(), type: sourceBlock.type, text: afterText, children: [], color: sourceBlock.color });
    
    targetArray.splice(sourceIndex, 1, ...newSequence);

    if (newBlockType === 'Arc') {
      let arcIndex = 0;
      blocks.value.forEach(block => {
        if (block.type === 'Arc') {
          block.color = getNewBlockStyle('Arc', null, arcIndex);
          arcIndex++;
        }
      });
    } else if (newBlockType === 'Chapter' && parent) {
      let chapterIndex = 0;
      parent.children.forEach(child => {
        if (child.type === 'Chapter') {
          child.color = getNewBlockStyle('Chapter', parent, chapterIndex);
          chapterIndex++;
        }
      });
    }
  }

  function handleElevation(path: Block[], selectedText: string, newBlockType: BlockType) {
    const sourceBlock = path[path.length - 1];
    const escapedSelectedText = escapeRegExp(selectedText);
    const [beforeText, afterText] = sourceBlock.text.split(escapedSelectedText).map(t => t.trim());

    const ancestorIndex = path.findIndex(p => p.type === newBlockType);
    if (ancestorIndex === -1) return;

    const targetAncestor = path[ancestorIndex];
    const parentOfAncestor = ancestorIndex > 0 ? path[ancestorIndex - 1] : null;

    const beforeBlock = buildPartialTree(path, ancestorIndex, sourceBlock, beforeText, 'before');
    const requestedBlock: Block = { id: uuidv4(), type: newBlockType, text: selectedText, children: [], color: getNewBlockStyle(newBlockType, parentOfAncestor) };
    const afterBlock = buildPartialTree(path, ancestorIndex, sourceBlock, afterText, 'after');

    const newSequence = [beforeBlock, requestedBlock, afterBlock].filter(Boolean) as Block[];
    const targetArray = parentOfAncestor ? parentOfAncestor.children : blocks.value;
    const replaceIndex = targetArray.findIndex(b => b.id === targetAncestor.id);
    
    if (replaceIndex !== -1) {
      targetArray.splice(replaceIndex, 1, ...newSequence);
    }
  }

  function updateBlockText(blockId: string, newText: string) {
    const path = findBlockPath(blocks.value, blockId);
    if (!path) return;
    const block = path[path.length - 1];
    if (newText.trim() === '' && !block.children.length) return;
    block.text = newText;
  }

  return { 
    blocks, 
    createBlock, 
    updateBlockText,
    removeBlocks: (ids: Set<string>) => removeBlocksRecursive(blocks.value, ids),
    insertBlocks,
    appendTextToBlock,
  };
});
