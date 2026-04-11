export type BlockType = 'arc' | 'chapter' | 'scene';

/**
 * Represents the visual style of a block.
 */
export interface BlockStyle {
  solid: string;  // The primary background color (e.g., in hex).
  shadow: string; // The corresponding shadow color (e.g., in rgba).
}

export interface Block {
  id: string;
  type: BlockType;
  text: string;
  color: BlockStyle; // Color is now a structured and mandatory object.
  children: Block[]; // Correctly typed as an array of Blocks.
}
