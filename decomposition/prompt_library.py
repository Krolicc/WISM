# decomposition/prompt_library.py

# --- STREAM 1: STRUCTURAL DECOMPOSITION PROMPTS ---

FIND_CHAPTER_BREAKS_PROMPT = """
As an expert editor, your task is to analyze a chunk of a larger text and identify potential chapter breaks.
A chapter usually begins with a significant shift in topic, time, or narrative focus.

Analyze the provided text chunk. If you identify the beginning of one or more new chapters within this chunk, provide the following for each:
1.  A concise and compelling title for the potential chapter.
2.  The full first sentence of that chapter, which will serve as a unique marker.

The text chunk is delimited by triple backticks.

Text Chunk:
```
{text_chunk}
```

Respond with a JSON object containing a single key "potential_chapters", which is a list of objects.
Each object must have the following structure:
{{
  "title": "A Suggested Chapter Title",
  "first_sentence": "The complete first sentence of the potential chapter..."
}}

If no new chapters appear to begin in this chunk, return an empty list:
{{
  "potential_chapters": []
}}
"""

CONSOLIDATE_CHAPTERS_PROMPT = """
As a lead editor, you are given a list of potential chapter starting points, identified from various overlapping chunks of a single, large story.
Your task is to analyze this list, remove duplicates, discard any false positives, and produce a final, ordered list of definitive chapters.

Potential Chapters List:
```
{potential_chapters_list}
```

Review the list and construct a final, canonical sequence of chapters.
Respond with a JSON object containing a single key "chapters", which is a list of objects.
Each object must have the following structure:
{{
  "title": "The Final Chapter Title",
  "first_sentence": "The complete first sentence of the chapter."
}}
"""

CHAPTER_TO_SCENES_PROMPT = """
As a professional screenwriter, your task is to break down a chapter from a story into a sequence of distinct scenes.
A scene is a continuous block of action that takes place in a single location at a single point in time.
For each scene you identify, provide:
1.  A brief summary.
2.  A list of characters present.
3.  The location.
4.  The full text of the scene.

Chapter Text:
```
{chapter_text}
```

Respond with a JSON object containing a single key "scenes", which is a list of scene objects with keys: "summary", "characters", "location", "text".
"""

SCENE_TO_FRAMES_PROMPT = """
As a film director, break down a scene into a series of visual frames.
For each frame, provide:
1.  A `visual_description` (camera angle, setting details, character expressions).
2.  The key `action_or_dialogue`.
3.  A suggested `shot_type` (e.g., "Close-up", "Wide shot").

Scene Text:
```
{scene_text}
```

Respond with a JSON object containing a single key "frames", which is a list of frame objects with keys: "visual_description", "action_or_dialogue", "shot_type".
"""


# --- STREAM 2: ENTITY & WORLD-BUILDING PROMPTS ---

EXTRACT_ENTITIES_PROMPT = """
As a literary analyst, your task is to read an entire story and identify all key entities.
Your goal is to perform entity resolution, grouping all references to a single entity under one canonical name.

Analyze the full text provided below. Identify all major **characters** and **locations**.

For each entity, you must provide:
1.  `canonical_name`: The most common or official name for the entity.
2.  `aliases`: A list of all other names, nicknames, pronouns, or descriptions used to refer to that entity throughout the text.

The full text is delimited by triple backticks.

Full Text:
```
{full_text}
```

Respond with a JSON object containing two keys: "characters" and "locations".
Each key should hold a list of entity objects, structured as described above.

Example Response:
{{
  "characters": [
    {{
      "canonical_name": "Sherlock Holmes",
      "aliases": ["Holmes", "my companion", "the sleuth", "him"]
    }},
    {{
      "canonical_name": "Dr. John Watson",
      "aliases": ["Watson", "I", "the doctor", "me"]
    }}
  ],
  "locations": [
    {{
      "canonical_name": "221B Baker Street",
      "aliases": ["our flat", "the apartment", "Holmes's residence"]
    }}
  ]
}}
"""

ENRICH_ENTITY_PROMPT = """
As a literary analyst, you are provided with the full text of a story and the canonical name of a specific entity (a character or a location).
Your task is to read the entire text and synthesize all available information about this specific entity into a single, detailed description.

- If it's a **character**, focus on their physical appearance, personality traits, background, skills, habits, and significant actions.
- If it's a **location**, describe its atmosphere, layout, key features, and its role in the story.

Compile all scattered details from the text into a coherent, descriptive paragraph.

The full text is delimited by triple backticks. The name of the entity to focus on is provided separately.

Full Text:
```
{full_text}
```

Entity Name:
`{entity_name}`

Respond with a JSON object containing a single key "description", holding the comprehensive, synthesized paragraph about the specified entity.

Example Response for the entity "Sherlock Holmes":
{{
  "description": "A tall, exceedingly lean man with a sharp, piercing gaze and a thin, hawk-like nose. His chin is prominent and square, indicating a determined nature. An eccentric genius, Holmes is a brilliant consulting detective with profound, albeit specialized, knowledge in fields like chemistry and criminal history, while being astonishingly ignorant in others like literature and astronomy. He is prone to bouts of intense energy and activity, followed by periods of lethargic melancholy. He is a skilled violinist, boxer, and swordsman, and lives at 221B Baker Street."
}}
"""
