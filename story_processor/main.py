'''
Main entry point for the Story Processor application.

This script initializes and runs the story processing pipeline.
'''

import os
import json
import asyncio
from pipeline.pipeline import StoryPipeline

# The "root" for our file paths is the directory this script is in.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

async def main():
    '''
    Main function to set up and run the pipeline.
    '''
    # 1. Load the story
    story_path = os.path.join(SCRIPT_DIR, 'model_training', 'data', 'raw_stories', 'AStudyInScarlet.txt')
    print(f"[MAIN] Loading story from: {story_path}")
    with open(story_path, 'r', encoding='utf-8') as f:
        full_story_text = f.read()
    print("[MAIN] Story loaded successfully.")

    # 2. Configure and run the pipeline
    pipeline = StoryPipeline(full_story_text)

    # Chain the methods to define the flow.
    # The new architecture ensures each step can rely on data from the previous one.
    final_data = await (
        pipeline
        .extract_chapters()      
        .extract_entities()      
        .process_story()        
        .run()
    )

    # print("\n[MAIN] Final pipeline data:")
    # final_data_dict = final_data.model_dump()
    # print(json.dumps(final_data_dict, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())
