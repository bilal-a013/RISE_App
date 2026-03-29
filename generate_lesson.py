#!/usr/bin/env python3
"""RISE Lesson Generator

Generates a Learn + Practise lesson pair for a given subtopic ID.
Outputs two JSON files to the /output/<tier>/ folder.

Usage:
    python generate_lesson.py --subtopic-id 1.1
    python generate_lesson.py --subtopic-id 2H.3
    python generate_lesson.py --list

Requirements:
    pip install google-genai
    set GEMINI_API_KEY=your_key_here  (Windows)
    export GEMINI_API_KEY=your_key_here  (macOS/Linux)

    Free API key: https://aistudio.google.com/apikey
    Free tier: 15 requests/min, 1,500 requests/day
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("Error: google-genai package not installed. Run: pip install google-genai")
    sys.exit(1)

from topic_map import ALL_TOPICS

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

OUTPUT_DIR = Path(__file__).parent / "output"
MODEL = "gemini-2.0-flash-lite"

# Free tier: 30 requests per minute. One call every 3 seconds = 20 RPM — safely under the limit.
CALL_DELAY_SECONDS = 3

# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
You are a content generator for RISE, a GCSE Maths tutoring app for students aged 14-16.
You create lesson content based strictly on the Edexcel GCSE Maths (1MA1) specification.

Rules — follow without exception:
- Write in plain English. No academic waffle.
- No filler phrases ("Great question!", "In this lesson we will explore...").
- UK English spelling throughout (colour, factorise, recognise, etc.).
- Spell out all operations in step-by-step solutions (e.g. "Divide both sides by 3").
- Do NOT use LaTeX. Write maths in plain text only.
- All content must be original. Do not reference or paraphrase any external source.
- Output valid JSON only. No markdown fences, no preamble, no explanation text.\
"""

LEARN_PROMPT = """\
Generate a Learn lesson for the subtopic below.

Topic: {topic}
Subtopic: {subtopic}
Tier: {tier}

Output ONLY valid JSON with this exact structure — no other text:

{{
  "topic": "{topic}",
  "subtopic": "{subtopic}",
  "lesson_type": "learn",
  "intro": "2-3 sentences. What the topic is and why it matters. No waffle.",
  "explanation": "Full concept explanation for a GCSE student. Plain English. No jargon.",
  "worked_example": {{
    "question": "One realistic exam-style question",
    "steps": [
      "Step 1 — show all working",
      "Step 2",
      "Step 3"
    ],
    "final_answer": "Clearly stated final answer"
  }},
  "common_mistakes": [
    "Specific mistake 1 — not generic",
    "Specific mistake 2",
    "Specific mistake 3"
  ]
}}

Constraints:
- intro: 2-3 sentences only, no filler
- explanation: thorough but written for a 14-16 year old, plain English
- worked_example.steps: minimum 3 steps, show every calculation
- worked_example.question: realistic Edexcel-style wording
- common_mistakes: exactly 3 items, specific to this subtopic\
"""

PRACTISE_PROMPT = """\
Generate a Practise lesson for the subtopic below.

Topic: {topic}
Subtopic: {subtopic}
Tier: {tier}

Output ONLY valid JSON with this exact structure — no other text:

{{
  "topic": "{topic}",
  "subtopic": "{subtopic}",
  "lesson_type": "practise",
  "recap": "One sentence only. Reminds the student what they learned in the Learn lesson.",
  "questions": [
    {{
      "number": 1,
      "difficulty": "easy",
      "marks": 1,
      "question": "Exam-style question",
      "solution": {{
        "steps": ["Step 1", "Step 2"],
        "final_answer": "Answer"
      }}
    }},
    {{
      "number": 2,
      "difficulty": "easy",
      "marks": 2,
      "question": "Exam-style question",
      "solution": {{
        "steps": ["Step 1", "Step 2"],
        "final_answer": "Answer"
      }}
    }},
    {{
      "number": 3,
      "difficulty": "medium",
      "marks": 3,
      "question": "Exam-style question",
      "solution": {{
        "steps": ["Step 1", "Step 2", "Step 3"],
        "final_answer": "Answer"
      }}
    }},
    {{
      "number": 4,
      "difficulty": "medium",
      "marks": 3,
      "question": "Exam-style question",
      "solution": {{
        "steps": ["Step 1", "Step 2", "Step 3"],
        "final_answer": "Answer"
      }}
    }},
    {{
      "number": 5,
      "difficulty": "hard",
      "marks": 4,
      "question": "Exam-style question",
      "solution": {{
        "steps": ["Step 1", "Step 2", "Step 3", "Step 4"],
        "final_answer": "Answer"
      }}
    }}
  ],
  "summary": [
    "Key point 1",
    "Key point 2",
    "Key point 3"
  ]
}}

Constraints:
- recap: exactly one sentence
- questions: exactly 5 in the order shown (easy 1mk, easy 2mk, medium 3mk, medium 3mk, hard 4mk)
- each question must test a different skill — no two questions test the same thing
- Q5 must genuinely stretch a student — multi-step, non-obvious
- all questions must use realistic Edexcel-style wording
- each solution must show at least 2 steps and a clearly stated final answer
- summary: 3-4 bullet points, concise and useful\
"""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def subtopic_to_snake(subtopic_id: str, subtopic_name: str) -> str:
    """Build a snake_case filename prefix: e.g. '1_1_order_of_operations_bidmas'."""
    prefix = subtopic_id.replace(".", "_")
    name = subtopic_name.lower()
    name = re.sub(r"[''']", "", name)
    name = re.sub(r"[^a-z0-9]+", "_", name)
    name = name.strip("_")
    return f"{prefix}_{name}"


def strip_fences(text: str) -> str:
    """Remove accidental markdown code fences from API output."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        # Drop first line (``` or ```json) and last line (```)
        inner = lines[1:-1] if lines[-1].strip() == "```" else lines[1:]
        text = "\n".join(inner)
    return text.strip()


def call_gemini(client: "genai.Client", user_prompt: str) -> dict:
    """Call Gemini and return parsed JSON. Retries once on 429 rate-limit."""
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.7,
                    max_output_tokens=4096,
                ),
            )
            raw = strip_fences(response.text)
            result = json.loads(raw)
            # Pause after every successful call to stay under the 15 RPM free-tier limit.
            time.sleep(CALL_DELAY_SECONDS)
            return result
        except Exception as e:
            msg = str(e)
            if "429" in msg or "RESOURCE_EXHAUSTED" in msg or "quota" in msg.lower():
                wait = 65 * (attempt + 1)
                print(f"  Rate limited — waiting {wait}s before retry (attempt {attempt + 1}/3)...")
                time.sleep(wait)
            else:
                raise
    raise RuntimeError("Gemini call failed after 3 attempts due to rate limiting.")


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate_learn(data: dict) -> list[str]:
    errors: list[str] = []
    for field in ("topic", "subtopic", "lesson_type", "intro", "explanation",
                  "worked_example", "common_mistakes"):
        if not data.get(field):
            errors.append(f"Missing or empty field: {field}")
    if data.get("lesson_type") != "learn":
        errors.append("lesson_type must be 'learn'")
    steps = data.get("worked_example", {}).get("steps", [])
    if len(steps) < 3:
        errors.append(f"worked_example.steps needs >= 3 items (got {len(steps)})")
    mistakes = data.get("common_mistakes", [])
    if len(mistakes) != 3:
        errors.append(f"common_mistakes must have exactly 3 items (got {len(mistakes)})")
    return errors


def validate_practise(data: dict) -> list[str]:
    errors: list[str] = []
    for field in ("topic", "subtopic", "lesson_type", "recap", "questions", "summary"):
        if not data.get(field):
            errors.append(f"Missing or empty field: {field}")
    if data.get("lesson_type") != "practise":
        errors.append("lesson_type must be 'practise'")
    questions = data.get("questions", [])
    if len(questions) != 5:
        errors.append(f"questions must have exactly 5 items (got {len(questions)})")
    spec = [(1, "easy", 1), (2, "easy", 2), (3, "medium", 3), (4, "medium", 3), (5, "hard", 4)]
    for q, (num, diff, marks) in zip(questions, spec):
        if q.get("number") != num:
            errors.append(f"Q{num}: wrong number value")
        if q.get("difficulty") != diff:
            errors.append(f"Q{num}: difficulty should be '{diff}', got '{q.get('difficulty')}'")
        if q.get("marks") != marks:
            errors.append(f"Q{num}: marks should be {marks}, got {q.get('marks')}")
        sol_steps = q.get("solution", {}).get("steps", [])
        if len(sol_steps) < 2:
            errors.append(f"Q{num}: solution.steps needs >= 2 items")
    summary = data.get("summary", [])
    if not (3 <= len(summary) <= 4):
        errors.append(f"summary must have 3-4 items (got {len(summary)})")
    return errors


# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------


def save_lesson(data: dict, tier: str, filename: str) -> Path:
    folder = OUTPUT_DIR / tier
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / filename
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def list_subtopics() -> None:
    from topic_map import FOUNDATION_TOPICS, HIGHER_TOPICS
    print("\nFoundation subtopics:")
    for sid, info in FOUNDATION_TOPICS.items():
        print(f"  {sid:6s}  {info['subtopic']}  ({info['topic']})")
    print("\nHigher subtopics:")
    for sid, info in HIGHER_TOPICS.items():
        print(f"  {sid:6s}  {info['subtopic']}  ({info['topic']})")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a RISE Learn + Practise lesson pair for a given subtopic."
    )
    parser.add_argument(
        "--subtopic-id",
        metavar="ID",
        help="Subtopic ID from the topic map, e.g. 1.1 or 2H.3",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Print all available subtopic IDs and exit",
    )
    args = parser.parse_args()

    if args.list:
        list_subtopics()
        return

    if not args.subtopic_id:
        parser.print_help()
        sys.exit(1)

    info = ALL_TOPICS.get(args.subtopic_id)
    if not info:
        print(f"Error: subtopic ID '{args.subtopic_id}' not found. Run --list to see all IDs.")
        sys.exit(1)

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable is not set.")
        print("Get a free key at: https://aistudio.google.com/apikey")
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    tier = info["tier"]
    topic = info["topic"]
    subtopic = info["subtopic"]
    base = subtopic_to_snake(args.subtopic_id, subtopic)

    print(f"\nGenerating lesson pair: [{args.subtopic_id}] {subtopic} ({tier})")

    # --- Learn ---
    print("\n[1/2] Learn lesson...")
    learn_data = call_gemini(
        client,
        LEARN_PROMPT.format(topic=topic, subtopic=subtopic, tier=tier),
    )
    errors = validate_learn(learn_data)
    if errors:
        print("  Validation issues (check before importing):")
        for e in errors:
            print(f"    - {e}")
    path = save_lesson(learn_data, tier, f"{base}_learn.json")
    print(f"  Saved: {path}")

    # --- Practise ---
    print("\n[2/2] Practise lesson...")
    practise_data = call_gemini(
        client,
        PRACTISE_PROMPT.format(topic=topic, subtopic=subtopic, tier=tier),
    )
    errors = validate_practise(practise_data)
    if errors:
        print("  Validation issues (check before importing):")
        for e in errors:
            print(f"    - {e}")
    path = save_lesson(practise_data, tier, f"{base}_practise.json")
    print(f"  Saved: {path}")

    print("\nDone. QA both files before importing to the database.")


if __name__ == "__main__":
    main()
