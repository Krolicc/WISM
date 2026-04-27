
from typing import List, Any
from pydantic import BaseModel, Field
from app.enums.generation_task import GenerationTask

class Task(BaseModel):
    task: GenerationTask = Field(..., description="The specific generation task to execute.")
    ids: List[uuid.UUID] = Field(..., description="A list of ids for the task.")

class OrchestrationRequest(BaseModel):
    tasks: List[Task]
