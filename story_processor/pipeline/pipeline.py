'''
This module contains the main StoryPipeline class that manages the state
and execution of the story processing workflow.
'''
import asyncio
from collections import deque
from typing import Any, List

from . import mock_tasks
from .data_models import (
    Chapter,
    Scene, 
    Frame, 
    DetailedFramePrompt,
    PipelineData, 
    RawChapterResult,
    RawEntity, 
    EnrichEntity,
    EnrichEntities,
)



class StoryPipeline:
    '''
    A stateful pipeline that processes a story through a series of chained methods.
    '''

    def __init__(self, story_text: str):
        '''Initializes the pipeline with the full story text.'''
        self.data = PipelineData(full_story_text=story_text)
        self._task_map = {
             # Phase 1
            'extract_chapters': self._task_extract_chapters,
            'consolidate_chapters': self._task_consolidate_chapters,

            'extract_entities': self._task_extract_entities,
            'enrich_entities': self._task_enrich_entities,

            # Phase 2
            'process_story': self._task_process_story,
            'process_chapter': self._task_process_chapter,
            'process_scene': self._task_process_scene,
            'process_frame': self._task_process_frame,
        }

    # --- Chaining Methods ---

    def extract_chapters(self):
        '''Queues the raw chapter extraction task.'''
        print("[PIPELINE] Queuing task: Chapter Extraction")
        self.data.task_queue.append(('extract_chapters', {}))
        return self

    def extract_entities(self):
        '''Queues the raw entity extraction task.'''
        print("[PIPELINE] Queuing task: Entity Extraction")
        self.data.task_queue.append(('extract_entities', {}))
        return self

    def process_story(self):
        '''Queues the scene extraction orchestrator task.'''
        print("[PIPELINE] Queuing task: Scene Extraction Orchestrator")
        self.data.task_queue.append(('process_story', {}))
        return self

    # --- Task Execution Logic ---
    async def run(self) -> PipelineData:
        print("\n[PIPELINE] Starting pipeline run...")
        phase = 1
        print(f"[PHASE {phase}] Awaiting Chapter and Entity readiness...")

        while True:
            # --- Условия выхода и ошибки ---
            if self.data.status_flags.error_occurred:
                print(f"[ERROR] Halting pipeline due to error in Phase {phase}.")
                await asyncio.sleep(1)
                break
            
            # Условие выхода из всего конвейера
            if phase == 2 and self.data.status_flags.pending_tasks_count == 0 and not self.data.task_queue:
                print("[PHASE 2] Completed.")
                break

            # --- Логика переключения фаз (Барьер) ---
            if phase == 1 and self.data.status_flags.chapters_ready and self.data.status_flags.entities_ready:
                phase = 2
                print("[PHASE 1] Completed.")
                print(f"\n[PHASE {phase}] Starting asynchronous processing...")
                # Перезапускаем цикл, чтобы он мог обработать задачи Фазы 2, которые уже могут быть в очереди
                continue

            # --- Выполнение задач ---
            try:
                task_name, params = self.data.task_queue.popleft()
                is_phase2_task = task_name in ['process_story', 'process_chapter', 'process_scene', 'process_frame']

                # Если мы в Фазе 1, откладываем задачи Фазы 2
                if phase == 1 and is_phase2_task:
                    self.data.task_queue.append((task_name, params))
                    await asyncio.sleep(0.01)
                    continue
                
                # Запускаем задачу
                handler = self._task_map.get(task_name)
                if handler:
                    print(f"  [TASK] Running: {task_name}")
                    await handler(**params)
                else:
                    print(f"  [WARN] No handler found for task: {task_name}")

            except IndexError:
                await asyncio.sleep(0.1)
        
        print("\n[PIPELINE] Run finished.")
        return self.data

    # --- Private Task Handlers ---
    # Phase 1
    async def _task_extract_chapters(self):
        raw_data = await mock_tasks.extract_chapters(self.data.full_story_text)
        self.data.intermediate_results.raw_chapters = RawChapterResult(**raw_data)
        self.data.task_queue.append(('consolidate_chapters', {}))

        print("    [SUCCESS] Raw chapters extracted.")

    async def _task_consolidate_chapters(self):
        raw_chapters = self.data.intermediate_results.raw_chapters

        self.data.chapters = await mock_tasks.consolidate_chapters(raw_chapters)
        self.data.status_flags.chapters_ready = True
        print("    -> Flag set: chapters_ready = True")

    async def _task_extract_entities(self):
        raw = await mock_tasks.extract_entities(self.data.full_story_text)
        
        self.data.intermediate_results.raw_entities.characters = [RawEntity(**c) for c in raw.get('characters', [])]
        self.data.intermediate_results.raw_entities.locations = [RawEntity(**l) for l in raw.get('locations', [])]
        
        self.data.status_flags.entities_tasks_count = len(raw.get('characters', [])) + len(raw.get('locations', []))

        self.data.task_queue.append(('enrich_entities', {}))
        print("    [SUCCESS] Raw entities extracted.")

    async def _task_enrich_entities(self):
        raw_entities = self.data.intermediate_results.raw_entities

        async def _enrich(entity: RawEntity, result_list: List[EnrichEntity]):
            if self.data.status_flags.error_occurred: return
            try:
                enrich_data = await mock_tasks.enrich_entity(entity)
                enrich_entity = EnrichEntity(**entity.model_dump(), **enrich_data)

                result_list.append(enrich_entity)

            except Exception as e:
                print(f"[ERROR] Could not enrich entity {getattr(entity, 'canonical_name', 'N/A')}: {e}")
                self.data.status_flags.error_occurred = True
            finally:
                self.data.status_flags.entities_tasks_count -= 1
                # print(f"    [Join] Entity enriched. Pending entities: {self.data.status_flags.entities_tasks_count}")
                if self.data.status_flags.entities_tasks_count == 0:
                    self.data.status_flags.entities_ready = True
                    print("    -> Flag set: entities_ready = True")


        for character in raw_entities.characters:
            asyncio.create_task(_enrich(character, self.data.entities.characters))
        
        for location in raw_entities.locations:
            asyncio.create_task(_enrich(location, self.data.entities.locations))

        print("    -> Flag set: entities_ready = True")


    # Phase 2
    async def _task_process_story(self):
        num_chapters = len(self.data.chapters)
        if num_chapters == 0:
            return

        self.data.status_flags.pending_tasks_count = num_chapters
        print(f"  [ORCHESTRATOR] Initializing Phase 2. Pending tasks: {num_chapters}")
        
        full_text = self.data.full_story_text
    
        for i, chapter in enumerate(self.data.chapters):
            start_phrase = chapter.first_sentence
            chapter_text = ""
            start_idx = full_text.find(start_phrase)
            if start_idx == -1:
                self.data.status_flags.pending_tasks_count -= 1
                print(f"    [WARN] Chapter start sentence not found for '{start_phrase[:30]}...'. Skipping. Pending tasks: {self.data.status_flags.pending_tasks_count}")
                continue
            # Find the end of the chapter
            if i + 1 < len(self.data.chapters):
                end_phrase = self.data.chapters[i+1].first_sentence
                end_idx = full_text.find(end_phrase, start_idx)
                if end_idx != -1:
                    chapter_text = full_text[start_idx:end_idx]
                else:
                    chapter_text = full_text[start_idx:]
            else:
                chapter_text = full_text[start_idx:]

            if chapter_text:
                self.data.task_queue.append(('process_chapter', {'chapter_text': chapter_text.strip()}))
            else:
                self.data.status_flags.pending_tasks_count -= 1
                print(f"    [WARN] Chapter text for '{start_phrase[:30]}...' was empty. Skipping. Pending tasks: {self.data.status_flags.pending_tasks_count}")


    async def _task_process_chapter(self, chapter_text: str):
        scenes_raw = await mock_tasks.extract_scenes(chapter_text)
        scenes_data = [Scene(**s) for s in scenes_raw.get('scenes', [])]
        num_scenes = len(scenes_data)

        if num_scenes > 0:
            self.data.status_flags.pending_tasks_count += num_scenes - 1
            print(f"    [Fork] Chapter found {num_scenes} scenes. Pending tasks: {self.data.status_flags.pending_tasks_count}")
            for scene in scenes_data:
                self.data.task_queue.append(('process_scene', {'scene_text': scene.text}))
        else:
            self.data.status_flags.pending_tasks_count -= 1
            print(f"    [Join] Chapter had 0 scenes. Pending tasks: {self.data.status_flags.pending_tasks_count}")


    async def _task_process_scene(self, scene_text: str):
        frames_raw = await mock_tasks.extract_simple_frames(scene_text)
        frames_data = [Frame(**f) for f in frames_raw.get('frames', [])]
        num_frames = len(frames_data)

        if num_frames > 0:
            self.data.status_flags.pending_tasks_count += num_frames - 1
            print(f"    [Fork] Scene found {num_frames} frames. Pending tasks: {self.data.status_flags.pending_tasks_count}")
            for frame in frames_data:
                self.data.task_queue.append(('process_frame', {'frame': frame}))
        else:
            self.data.status_flags.pending_tasks_count -= 1
            print(f"    [Join] Scene had 0 frames. Pending tasks: {self.data.status_flags.pending_tasks_count}")


    async def _task_process_frame(self, frame: Frame):
        entities_in_frame = self._find_entities_in_text(frame.source_text, self.data.entities)
        
        prompt_data = await mock_tasks.enrich_frame(frame.common_description, entities_in_frame)
        frame.detailed_prompt = DetailedFramePrompt(**prompt_data)

        self.data.status_flags.pending_tasks_count -= 1
        
        print(f"    [Join] Frame enriched. Pending tasks: {self.data.status_flags.pending_tasks_count}")


    # --- Extra Private Task Handlers ---
    
    def _find_entities_in_text(self, text: str, all_entities: EnrichEntities) -> list[str]:
        '''Finds which entity canonical names are present in a given text snippet.'''
        present_entities = []

        text_lower = text.lower()
        
        for field_name in all_entities.__fields__:
            list_of_entities = getattr(all_entities, field_name)

            for entity in list_of_entities:
                aliases_to_check = [ entity.canonical_name ] + entity.aliases
                if any(alias.lower() in text_lower for alias in aliases_to_check):
                    present_entities.append(entity.canonical_name)
        return list(set(present_entities))
    
    def _extract_text_between(self, text: str, start_phrase: str, end_phrase: str) -> str:
        '''Extracts text between two phrases.'''
        start_index = text.find(start_phrase)
        if start_index == -1:
            return ""
        start_index += len(start_phrase)
        end_index = text.find(end_phrase, start_index)
        if end_index == -1:
            return ""
        return text[start_index:end_index].strip()