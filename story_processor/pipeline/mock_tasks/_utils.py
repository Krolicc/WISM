'''
This utility module provides shared functions for all mock task modules.
'''

import json
import os

# The "root" for file paths is the directory TWO levels up from this file
# (up from /mock_tasks, up from /pipeline to /story_processor)
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EXAMPLES_DIR = os.path.join(SCRIPT_DIR, "..", "model_training", "data", "examples", "AStudyInScarlet")
PROMPTS_DIR = os.path.join(SCRIPT_DIR, "..", "prompts")

def load_example(task_name: str, prompt_file: str, example_file: str):
    '''
    Prints a standard message and loads a predefined JSON example.
    '''
    print(f"\n--- [MOCK AI CALL] Task: {task_name} ---")
    prompt_path = os.path.join(PROMPTS_DIR, prompt_file)
    # We are getting the absolute path to make sure the file is found
    # since we are now in a different folder structure
    prompt_path = os.path.abspath(prompt_path)

    print(f"SIMULATING model call with prompt from: {prompt_path}")
    
    example_path = os.path.join(EXAMPLES_DIR, example_file)
    example_path = os.path.abspath(example_path)

    print(f"LOADING predefined answer from: {example_path}")
    with open(example_path, 'r', encoding='utf-8') as f:
        result = json.load(f)
    
    print("--- [END MOCK AI CALL] ---")
    return result
