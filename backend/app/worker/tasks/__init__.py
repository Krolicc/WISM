
# This file makes the 'tasks' directory a Python package.
# It also ensures that Celery can auto-discover tasks defined in the submodules.

from .base import process_generation_chain

from .generate import (
    decompose_text_to_skeleton,
    generate_arcs_skeleton,
    generate_chapters_skeleton,
    generate_scenes_skeleton,
    generate_frames_skeleton
)

from .write import (
    write_arc_content,
    write_chapter_content,
    write_scene_content,
    write_frame_content,
    generate_frame_image
)

from .refine import (
    refine_arcs,
    refine_chapters,
    refine_scenes,
    refine_frames
)

# You can optionally define __all__ to control what `from .tasks import *` imports
__all__ = [
    # Chain
    "process_generation_chain",
    
    # Generate
    "decompose_text_to_skeleton",

    "generate_arcs_skeleton",
    "generate_chapters_skeleton",
    "generate_scenes_skeleton",
    "generate_frames_skeleton",
    
    # Write
    "rewrite_arc_content",
    "rewrite_chapter_content",
    "rewrite_scene_content",
    "write_frame_content",
    "generate_frame_image",
]