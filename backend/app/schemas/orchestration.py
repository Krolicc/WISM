
from pydantic import BaseModel, Field
from typing import List, Optional, Union, Literal
from typing_extensions import Annotated
import uuid

from .enums import OrchestrationTask

# ===================================================================
# 1. PARAMETER MODELS FOR EACH TASK
# NOTE: story_id is no longer needed here, it's in the main request
# ===================================================================

# --- Story Level ---
class DecomposeTextToSkeletonParams(BaseModel):
    full_text: str

# --- Arc Level ---
class GenerateArcsSkeletonParams(BaseModel):
    story_ids: List[uuid.UUID]
    num_arcs: int = Field(default=5, gt=0, le=10)

class RewriteArcContentParams(BaseModel):
    arc_ids: List[uuid.UUID]
    writing_prompt: Optional[str] = None

class RegenerateArcSkeletonParams(BaseModel):
    arc_ids: List[uuid.UUID]
    prompt: Optional[str] = None
    num_chapters: int = Field(default=3, gt=0, le=20)

class InsertNewArcAndGenerateSkeletonParams(BaseModel):
    parent_id: uuid.UUID
    insert_after_ids: Optional[List[uuid.UUID]] = None
    count: int = Field(default=1, gt=0, le=5)
    prompt: str

# --- Chapter Level ---
class GenerateChaptersSkeletonParams(BaseModel):
    arc_ids: List[uuid.UUID]
    num_chapters: int = Field(default=3, gt=0, le=20)

class RewriteChapterContentParams(BaseModel):
    chapter_ids: List[uuid.UUID]
    writing_prompt: Optional[str] = None

class RegenerateChapterSkeletonParams(BaseModel):
    chapter_id: List[uuid.UUID]
    prompt: Optional[str] = None
    num_scenes: int = Field(default=5, gt=0, le=20)

class InsertNewChapterAndGenerateSkeletonParams(BaseModel):
    parent_id: uuid.UUID
    insert_after_id: Optional[List[uuid.UUID]] = None
    count: int = Field(default=1, gt=0, le=5)
    prompt: str

# --- Scene Level ---
class GenerateScenesSkeletonParams(BaseModel):
    chapter_ids: List[uuid.UUID]
    num_scenes: int = Field(default=5, gt=0, le=20)

class RewriteSceneContentParams(BaseModel):
    scene_ids: List[uuid.UUID]
    writing_prompt: Optional[str] = None

class RegenerateSceneSkeletonParams(BaseModel):
    scene_id: List[uuid.UUID]
    prompt: Optional[str] = None
    num_frames: int = Field(default=3, gt=0, le=10)

class InsertNewSceneAndGenerateSkeletonParams(BaseModel):
    parent_id: uuid.UUID
    insert_after_id: Optional[List[uuid.UUID]] = None
    count: int = Field(default=1, gt=0, le=5)
    prompt: str

# --- Frame Level ---
class GenerateFramesSkeletonParams(BaseModel):
    scene_ids: List[uuid.UUID]
    num_frames: int = Field(default=3, gt=0, le=10)

class GenerateFramesContentParams(BaseModel):
    frame_ids: List[uuid.UUID]
    writing_prompt: Optional[str] = None

class GenerateFrameImageParams(BaseModel):
    frame_id: uuid.UUID
    style_prompt: Optional[str] = None

# --- Utility Tasks ---
class ExtractEntitiesParams(BaseModel):
    # Limit extraction to specific items to avoid re-processing the whole story
    arc_ids: Optional[List[uuid.UUID]] = None
    chapter_ids: Optional[List[uuid.UUID]] = None
    scene_ids: Optional[List[uuid.UUID]] = None

# ===================================================================
# 2. DISCRIMINATED UNION FOR TASK VALIDATION
# ===================================================================

class BaseTask(BaseModel):
    task: OrchestrationTask

class DecomposeTextToSkeletonTask(BaseTask):
    task: Literal[OrchestrationTask.DECOMPOSE_TEXT_TO_SKELETON]
    params: DecomposeTextToSkeletonParams

class GenerateArcsSkeletonTask(BaseTask):
    task: Literal[OrchestrationTask.GENERATE_ARCS_SKELETON]
    params: GenerateArcsSkeletonParams

class RewriteArcContentTask(BaseTask):
    task: Literal[OrchestrationTask.REWRITE_ARC_CONTENT]
    params: RewriteArcContentParams

class RegenerateArcSkeletonTask(BaseTask):
    task: Literal[OrchestrationTask.REGENERATE_ARC_SKELETON]
    params: RegenerateArcSkeletonParams

class InsertNewArcAndGenerateSkeletonTask(BaseTask):
    task: Literal[OrchestrationTask.INSERT_NEW_ARC_AND_GENERATE_SKELETON]
    params: InsertNewArcAndGenerateSkeletonParams

class GenerateChaptersSkeletonTask(BaseTask):
    task: Literal[OrchestrationTask.GENERATE_CHAPTERS_SKELETON]
    params: GenerateChaptersSkeletonParams

class RewriteChapterContentTask(BaseTask):
    task: Literal[OrchestrationTask.REWRITE_CHAPTER_CONTENT]
    params: RewriteChapterContentParams

class RegenerateChapterSkeletonTask(BaseTask):
    task: Literal[OrchestrationTask.REGENERATE_CHAPTER_SKELETON]
    params: RegenerateChapterSkeletonParams
class InsertNewChapterAndGenerateSkeletonTask(BaseTask):
    task: Literal[OrchestrationTask.INSERT_NEW_CHAPTER_AND_GENERATE_SKELETON]
    params: InsertNewChapterAndGenerateSkeletonParams

class GenerateScenesSkeletonTask(BaseTask):
    task: Literal[OrchestrationTask.GENERATE_SCENES_SKELETON]
    params: GenerateScenesSkeletonParams

class RewriteSceneContentTask(BaseTask):
    task: Literal[OrchestrationTask.REWRITE_SCENE_CONTENT]
    params: RewriteSceneContentParams

class RegenerateSceneSkeletonTask(BaseTask):
    task: Literal[OrchestrationTask.REGENERATE_SCENE_SKELETON]
    params: RegenerateSceneSkeletonParams
class InsertNewSceneAndGenerateSkeletonTask(BaseTask):
    task: Literal[OrchestrationTask.INSERT_NEW_SCENE_AND_GENERATE_SKELETON]
    params: InsertNewSceneAndGenerateSkeletonParams

class GenerateFramesSkeletonTask(BaseTask):
    task: Literal[OrchestrationTask.GENERATE_FRAMES_SKELETON]
    params: GenerateFramesSkeletonParams

class GenerateFramesContentTask(BaseTask):
    task: Literal[OrchestrationTask.GENERATE_FRAMES_CONTENT]
    params: GenerateFramesContentParams

class GenerateFrameImageTask(BaseTask):
    task: Literal[OrchestrationTask.GENERATE_FRAME_IMAGE]
    params: GenerateFrameImageParams

class ExtractEntitiesTask(BaseTask):
    task: Literal[OrchestrationTask.EXTRACT_ENTITIES]
    params: ExtractEntitiesParams

# --- Common Level ---

ChainableTasks = Union[
    'GenerateArcsSkeletonTask',
    'RewriteArcContentTask',
    'GenerateChaptersSkeletonTask',
    'RewriteChapterContentTask',
    'GenerateScenesSkeletonTask',
    'RewriteSceneContentTask',
    'GenerateFramesSkeletonTask',
    'GenerateFramesContentTask'
]

class ProcessGenerationChainParams(BaseModel):
    service_name: str
    actions: List[ChainableTasks]


class ProcessGeneratioChainTask(BaseTask):
    task: Literal[OrchestrationTask.PROCESS_GENERATION_CHAIN]
    params: ProcessGenerationChainParams

AllTasks = Annotated[
    Union[
        DecomposeTextToSkeletonTask,

        GenerateArcsSkeletonTask,
        RewriteArcContentTask,
        RegenerateArcSkeletonTask,
        InsertNewArcAndGenerateSkeletonTask,

        GenerateChaptersSkeletonTask,
        RewriteChapterContentTask,
        RegenerateChapterSkeletonTask,
        InsertNewChapterAndGenerateSkeletonTask,

        GenerateScenesSkeletonTask,
        RewriteSceneContentTask,
        RegenerateSceneSkeletonTask,
        InsertNewSceneAndGenerateSkeletonTask,

        GenerateFramesSkeletonTask,
        GenerateFramesContentTask,
        GenerateFrameImageTask,
        ExtractEntitiesTask,
        
        ProcessGeneratioChainTask,
    ],
    Field(discriminator="task"),
]

# ===================================================================
# 3. THE MAIN REQUEST BODY FOR THE ORCHESTRATION API
# ===================================================================

class OrchestrationRequest(BaseModel):
    tasks: List[AllTasks] = Field(..., min_items=1)

# ===================================================================
# 4. ERROR AND STATUS MODELS
# ===================================================================

class OrchestrationError(Exception):
    """Custom exception for orchestration errors."""
    pass

class TaskStatus(BaseModel):
    task_id: str
    status: str # e.g., PENDING, STARTED, SUCCESS, FAILURE
    task_type: OrchestrationTask
    message: Optional[str] = None
