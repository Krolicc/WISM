'''
This script compiles the scattered JSON examples into two training-ready
JSONL files, one for each stage of the image prompt generation process.

Task 1 (scene_to_frames): Converts a full scene text into a list of simple frame descriptions.
  - Input (prompt): The text of the scene.
  - Output (completion): A JSON object containing a list of frames, where each frame has a source_text and a common_description.

Task 2 (frame_to_detailed): Converts a simple frame (source text + common description) into a detailed prompt for an image generator.
  - Input (prompt): A JSON object with common_description and source_text.
  - Output (completion): A JSON object with the original common_description and the highly detailed_prompt structure.
'''

import json
import os

# Define paths
EXAMPLES_DIR = os.path.join("data", "examples", "AStudyInScarlet")
OUTPUT_DIR = os.path.dirname(EXAMPLES_DIR)
SCENES_FILE = os.path.join(EXAMPLES_DIR, "2_chapter_1_scenes.json")

TASK1_OUT_FILE = os.path.join(OUTPUT_DIR, "training_data_task1.jsonl")
TASK2_OUT_FILE = os.path.join(OUTPUT_DIR, "training_data_task2.jsonl")

# --- Task 1: scene_to_simple_frames --- 
def process_task_1():
    print("Processing Task 1: scene_to_simple_frames...")

    with open(SCENES_FILE, 'r', encoding='utf-8') as f:
        all_scenes_data = json.load(f)['scenes']

    # Map scene summaries to their full text for easy lookup
    scene_text_map = {scene['summary']: scene['text'] for scene in all_scenes_data}

    # Associate the simple_frame files with the scene summaries
    scene_to_simple_frames_map = {
        "В баре Уотсон неожиданно встречает своего бывшего коллегу Стэмфорда и приглашает его на завтрак.": "4_scene_criterion_bar_simple_frames.json",
        "Во время завтрака Уотсон рассказывает о своем желании найти недорогую квартиру. Стэмфорд упоминает о Шерлоке Холмсе, который ищет компаньона для совместного съема жилья.": "6_scene_holborn_restaurant_simple_frames.json",
        "По дороге в больницу Стэмфорд предупреждает Уотсона об эксцентричном и \"бездушном\" характере Холмса, который ради науки может ставить опыты на друзьях и колотить трупы палкой.": "8_scene_cab_to_hospital_simple_frames.json",
        "В лаборатории Уотсон знакомится с Шерлоком Холмсом, который демонстрирует свой новый реактив для определения гемоглобина, поражает Уотсона своей наблюдательностью и предлагает вместе снять квартиру на Бейкер-стрит.": "10_scene_laboratory_simple_frames.json",
        "Уходя из больницы, Уотсон спрашивает Стэмфорда, как Холмс догадался о его прошлом. Стэмфорд загадочно отвечает, что в этом и заключается главная особенность Холмса.": "12_scene_farewell_simple_frames.json",
    }

    with open(TASK1_OUT_FILE, 'w', encoding='utf-8') as outfile:
        for summary, filename in scene_to_simple_frames_map.items():
            scene_text = scene_text_map.get(summary)
            if not scene_text:
                print(f"  - WARNING: Could not find scene text for summary: {summary}")
                continue

            try:
                with open(os.path.join(EXAMPLES_DIR, filename), 'r', encoding='utf-8') as f:
                    completion_data = json.load(f)

                # Create the JSONL line
                training_example = {
                    "prompt": scene_text,
                    "completion": completion_data
                }
                outfile.write(json.dumps(training_example, ensure_ascii=False) + '\n')
                print(f"  - Successfully processed {filename}")
            except FileNotFoundError:
                print(f"  - WARNING: File not found: {filename}")
            except json.JSONDecodeError:
                print(f"  - WARNING: Could not decode JSON from {filename}")

    print(f"Task 1 processing complete. Output file: {TASK1_OUT_FILE}\n")


# --- Task 2: simple_frame_to_detailed_frame ---
def process_task_2():
    print("Processing Task 2: simple_frame_to_detailed_frame...")

    # First, build a lookup table from all simple_frames files
    # This maps a common_description to its source_text
    description_to_source_map = {}
    simple_frame_files = [f for f in os.listdir(EXAMPLES_DIR) if 'simple_frames' in f]

    for filename in simple_frame_files:
        try:
            with open(os.path.join(EXAMPLES_DIR, filename), 'r', encoding='utf-8') as f:
                data = json.load(f)
                for frame in data.get('frames', []):
                    if 'common_description' in frame and 'source_text' in frame:
                        description_to_source_map[frame['common_description']] = frame['source_text']
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"  - WARNING: Could not process {filename}. Error: {e}")


    # Now, process the detailed_frame files
    detailed_frame_files = [f for f in os.listdir(EXAMPLES_DIR) if 'detailed' in f]
    with open(TASK2_OUT_FILE, 'w', encoding='utf-8') as outfile:
        for filename in detailed_frame_files:
            try:
                with open(os.path.join(EXAMPLES_DIR, filename), 'r', encoding='utf-8') as f:
                    completion_data = json.load(f)
                
                common_desc = completion_data.get('common_description')
                if not common_desc:
                    print(f"  - WARNING: No common_description in {filename}")
                    continue

                source_text = description_to_source_map.get(common_desc)
                if not source_text:
                    print(f"  - WARNING: Could not find source_text for: {common_desc}")
                    continue
                
                # Create the prompt and completion objects
                prompt_obj = {
                    "common_description": common_desc,
                    "source_text": source_text
                }
                
                training_example = {
                    "prompt": prompt_obj,
                    "completion": completion_data
                }

                outfile.write(json.dumps(training_example, ensure_ascii=False) + '\n')
                print(f"  - Successfully processed {filename}")

            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"  - WARNING: Could not process {filename}. Error: {e}")

    print(f"Task 2 processing complete. Output file: {TASK2_OUT_FILE}\n")

if __name__ == '__main__':
    process_task_1()
    process_task_2()
