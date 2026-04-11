
export type ViewMode = 'character' | 'location' | 'user';

export interface Entity {
  id: string;
  type: ViewMode;
  group: string;
  canonical_name: string;
  description?: string;
  detailed_prompt: Record<string, any>; 
  is_stale: boolean;
  use_detailed_prompt: boolean;
  aliases: Record<string, any>; 
}