
export interface PromptField {
  id: string;
  value: string;
  placeholder: string;
}

// Defines the structure for a section containing multiple fields
export interface PromptSection {
  id: string;
  fields: { [key: string]: PromptField | PromptSection }; // Can be nested
}

// Defines a generic object containing either fields or sections
export type PromptObject = { [key: string]: PromptField | PromptSection };

export type UpdateObject = { 
  key: string; 
  value: UpdateObject | string;
  isDeleted?: boolean;
}