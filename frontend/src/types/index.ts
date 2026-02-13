export interface Frame {
  frame_id: string; // Using string as in the original file
  image_url: string;
  narration: string;
}

export interface Scene {
    id: number;
    title: string;
    frames: Frame[];
    isLoading?: boolean;
}

export interface Chapter {
  id: number;
  title: string;
  scenes: Scene[];
  isLoading?: boolean;
}

export interface Project {
  id: number;
  prompt: string;
  chapters: Chapter[];
  isLoading?: boolean;
}
