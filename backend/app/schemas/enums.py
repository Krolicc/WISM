
from enum import Enum

class EntityType(str, enum.Enum):
    CHARACTER = "character"
    LOCATION = "location"

class GenerationStage(str, Enum):
    """Defines the current generation stage of a story."""
    INITIAL = "INITIAL"
    ARCS_GENERATED = "ARCS_GENERATED"
    CHAPTERS_OUTLINED = "CHAPTERS_OUTLINED"
    CHAPTERS_WRITTEN = "CHAPTERS_WRITTEN"
    COMPLETE = "COMPLETE"

class OrchestrationTask(str, Enum):
    """Defines the specific long-running task to be executed by a worker."""
    
    # --- Common Level --- #
    PROCESS_GENERATION_CHAIN = "process_generation_chain"

    # --- Story Level --- #
    DECOMPOSE_TEXT_TO_SKELETON = "decompose_text_to_skeleton"
    
    # --- Arc Level --- #
    GENERATE_ARCS_SKELETON = "generate_arcs_skeleton"
    REWRITE_ARC_CONTENT = "rewrite_arc_content"
    REGENERATE_ARC_SKELETON = "regenerate_arc_skeleton"
    INSERT_NEW_ARC_AND_GENERATE_SKELETON = "insert_new_arc_and_generate_skeleton"

    # --- Chapter Level --- #
    GENERATE_CHAPTERS_SKELETON = "generate_chapters_skeleton"
    REWRITE_CHAPTER_CONTENT = "rewrite_chapter_content"
    REGENERATE_CHAPTER_SKELETON = "regenerate_chapter_skeleton"
    INSERT_NEW_CHAPTER_AND_GENERATE_SKELETON = "insert_new_chapter_and_generate_skeleton"

    # --- Scene Level --- #
    GENERATE_SCENES_SKELETON = "generate_scenes_skeleton"
    REWRITE_SCENE_CONTENT = "rewrite_scene_content"
    REGENERATE_SCENE_SKELETON = "regenerate_scene_skeleton"
    INSERT_NEW_SCENE_AND_GENERATE_SKELETON = "insert_new_scene_and_generate_skeleton"

    # --- Frame Level --- #
    GENERATE_FRAMES_SKELETON = "generate_frames_skeleton"
    GENERATE_FRAMES_CONTENT = "generate_frames_content"
    GENERATE_FRAME_IMAGE = "generate_frame_image"

    # --- Utility Tasks --- #
    EXTRACT_ENTITIES = "extract_entities"
