
import { defineStore } from 'pinia';
import type { ActionType } from '../lib/action-meta';
import type { StoryNode, BranchSet, BaseNode } from '../types';
import { v4 as uuidv4 } from 'uuid';
import { useContentManageStore } from './content_manage'
// import { yjsServiceContent.ydoc, nodes as yjsServiceContent.collections.nodes } from '../services/yjs_service';
import { yjsServiceContent } from '../services/content_yjs_service';

// --- TYPE DEFINITIONS ---

// This is the structure that will be written directly onto the node object.
export interface ActionState {
  type: 'modify' | 'delete';
  modifyType?: ActionType; // e.g., 'rewrite', 'regenerate'
  flag?: string;
  parameters?: Record<string, any>;
}

/**
 * useOrchestrationManageStore
 *
 * This store is a thin, stateless helper for performing immediate,
 * transactional changes to a node's `actionState` property within the Yjs document.
 */
export const useOrchestrationManageStore = defineStore('orchestrationManage', () => {

  const contentManageStore = useContentManageStore();

  /**
   * Sets or updates the action state for a given node.
   * This action is immediate and transactional.
   */
  function setAction(nodeId: string, action: ActionState) {
    yjsServiceContent.ydoc.transact(() => {
      const node = yjsServiceContent.collections.nodes.get(nodeId);
      if (node) {
        // Create a new object to ensure reactivity if needed, though Yjs handles this.
        const updatedNode = { ...node, actionState: action };
        yjsServiceContent.collections.nodes.set(nodeId, updatedNode);
      }
    });
  }

  /**
   * Clears the action state from a node, effectively cancelling any pending action.
   * This action is immediate and transactional.
   */
  function clearAction(nodeId: string) {
    yjsServiceContent.ydoc.transact(() => {
      const node = yjsServiceContent.collections.nodes.get(nodeId);
      if (node && node.actionState) {
        const { actionState, ...rest } = node; // Create a new object without the actionState
        yjsServiceContent.collections.nodes.set(nodeId, rest);
      }
    });
  }

  function createManualNode(type: string, id: string, isParent: boolean = false) {
    yjsServiceContent.ydoc.transact(() => {
      let afterId = null;
      let beforeId = null;
      let parentId = null;
      
      if (isParent) {
        parentId = id;
        const parentNode = contentManageStore.getNode(parentId, type == "arc");

        if (parentNode) {
          beforeId = parentNode.children_ids[0]?.id || null;
        }
      } else {
        afterId = id;
        const afterNode = contentManageStore.getNode(afterId)
        
        if (afterNode) {
          parentId = afterNode.parent_id;
          beforeId = afterNode.next_ids[0] || null;
        }
      }

      const newNodeId = uuidv4();
      const newNode: StoryNode = {
        id: newNodeId,
        content: { title: 'No title' },
        type: type,
        parent_id: parentId,
        children_ids: [],
        prev_ids: afterId ? [afterId] : [],
        next_ids: beforeId ? [beforeId] : [],
      };
      // Add the new node to the store
      yjsServiceContent.collections.nodes.set(newNodeId, newNode);

      // --- Link surrounding nodes ---
      if (afterId) {
        const afterNode = contentManageStore.getNode(afterId) as StoryNode;
        if (afterNode) {
          const oldNextIds = afterNode.next_ids || [];
          const newNextIds = [...oldNextIds.filter(id => id !== beforeId), newNodeId];
          yjsServiceContent.collections.nodes.set(afterId, { ...afterNode, next_ids: newNextIds });
        }
      }
      if (beforeId) {
        const beforeNode = contentManageStore.getNode(beforeId) as StoryNode;
        if (beforeNode) {
          const oldPrevIds = beforeNode.prev_ids || [];
          const newPrevIds = [...oldPrevIds.filter(id => id !== afterId), newNodeId];
          yjsServiceContent.collections.nodes.set(beforeId, { ...beforeNode, prev_ids: newPrevIds });
        }
      }
    });
  }

  function createBranchFromNode(sourceNodeId: string) {
    yjsServiceContent.ydoc.transact(() => {
      const sourceNode = contentManageStore.getNode(sourceNodeId) as StoryNode;
      if (!sourceNode) {
        console.error(`createBranchFromNode: Source node with ID ${sourceNodeId} not found.`);
        return;
      }
      const parentId = sourceNode.parent_id;
      if (!parentId) {
          console.error(`Cannot create a branch from a node with no parent.`);
          return;
      }
      // 1. Identify the original successor
      const originalNextId = sourceNode.next_ids?.[0]; // Assuming one main successor

      const branchSetId = uuidv4();
      const branchSetNode: BranchSet = {
          id: branchSetId,
          type: 'branchSet',
          title: 'Branch', 
          question: 'No quiestion',
          parent_id: parentId, 
          prev_ids: [sourceNodeId],
          next_ids: [],
          branches: {}
      };

      const newBranchNodeId = uuidv4();
      const newBranchNode: StoryNode = {
        id: newBranchNodeId,
        type: sourceNode.type, // Inherit type from the source
        content: { title: 'New Branch' },
        parent_id: branchSetId, // Belongs to the same parent
        prev_ids: [branchSetId], // Will be linked to the BranchSet
        next_ids: [],
        children_ids: []
      };

      if (originalNextId) {
          const originalNextNode = contentManageStore.getNode(originalNextId) as StoryNode;
          if (originalNextNode) {
            yjsServiceContent.collections.nodes.set(originalNextId, { ...originalNextNode, prev_ids: [branchSetId] });
          }
          // BranchSet points to the original successor
          branchSetNode.next_ids.push(originalNextId);
          branchSetNode.branches[originalNextId] = { label: 'Continue' }; 
      }
      // Link the new branch
      branchSetNode.next_ids.push(newBranchNodeId);
      branchSetNode.branches[newBranchNodeId] = { label: 'New Path' };
      // Add the BranchSet to the store

      yjsServiceContent.collections.nodes.set(newBranchNodeId, newBranchNode);
      yjsServiceContent.collections.nodes.set(branchSetId, branchSetNode);
        
      yjsServiceContent.collections.nodes.set(sourceNodeId, { ...sourceNode, next_ids: [branchSetId] });
      
      console.log(`Branch created. Source: ${sourceNodeId}, BranchSet: ${branchSetId}, New Node: ${newBranchNodeId}`);
    });
  }

  return {
    setAction,
    clearAction,
    createManualNode,
    createBranchFromNode,
    // createGenerationRequest,
  };
});
