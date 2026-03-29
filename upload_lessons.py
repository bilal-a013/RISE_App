import os
import json
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# Maps JSON filename prefixes to subtopic codes in the database
SUBTOPIC_CODE_MAP = {
    # Foundation Number
    "1_1": "1.1", "1_2": "1.2", "1_3": "1.3", "1_4": "1.4",
    "1_5": "1.5", "1_6": "1.6", "1_7": "1.7", "1_8": "1.8", "1_9": "1.9",
    # Foundation Algebra
    "2_1": "2.1", "2_2": "2.2", "2_3": "2.3", "2_4": "2.4", "2_5": "2.5",
    "2_6": "2.6", "2_7": "2.7", "2_8": "2.8", "2_9": "2.9", "2_10": "2.10",
    # Foundation Ratio
    "3_1": "3.1", "3_2": "3.2", "3_3": "3.3", "3_4": "3.4", "3_5": "3.5",
    # Foundation Geometry
    "4_1": "4.1", "4_2": "4.2", "4_3": "4.3", "4_4": "4.4",
    "4_5": "4.5", "4_6": "4.6", "4_7": "4.7",
    # Foundation Probability
    "5_1": "5.1", "5_2": "5.2", "5_3": "5.3", "5_4": "5.4",
    # Foundation Statistics
    "6_1": "6.1", "6_2": "6.2",
    # Higher Number
    "1H_1": "1H.1", "1H_2": "1H.2", "1H_3": "1H.3", "1H_4": "1H.4",
    # Higher Algebra
    "2H_1": "2H.1", "2H_2": "2H.2", "2H_3": "2H.3", "2H_4": "2H.4", "2H_5": "2H.5",
    # Higher Ratio
    "3H_1": "3H.1", "3H_2": "3H.2",
    # Higher Geometry
    "4H_1": "4H.1", "4H_2": "4H.2", "4H_3": "4H.3",
    # Higher Stats & Probability
    "5H_1": "5H.1", "5H_2": "5H.2", "5H_3": "5H.3",
}


def get_subtopic_id(code: str) -> str | None:
    result = supabase.table("subtopics").select("id").eq("code", code).execute()
    if result.data:
        return result.data[0]["id"]
    print(f"  WARNING: No subtopic found for code {code}")
    return None


def extract_prefix(filename: str) -> str:
    # e.g. "1_1_order_of_operations_bidmas_learn.json" -> "1_1"
    # e.g. "2H_3_perpendicular_lines_learn.json" -> "2H_3"
    parts = filename.replace(".json", "").split("_")
    if parts[1].upper() == "H" or (len(parts) > 1 and parts[0][0].isdigit() and parts[1] == "H"):
        return f"{parts[0]}H_{parts[2]}"
    if "H" in parts[0]:
        return f"{parts[0]}_{parts[1]}"
    return f"{parts[0]}_{parts[1]}"


def lesson_already_exists(subtopic_id: str, lesson_type: str) -> bool:
    result = supabase.table("lessons").select("id").eq("subtopic_id", subtopic_id).eq("lesson_type", lesson_type).execute()
    return bool(result.data)


def upload_learn_lesson(data: dict, subtopic_id: str, order_index: int):
    learn = data.get("learn") or data  # handle both wrapped and flat formats

    lesson = supabase.table("lessons").insert({
        "subtopic_id": subtopic_id,
        "lesson_type": "learn",
        "intro": learn.get("intro"),
        "explanation": learn.get("explanation"),
        "order_index": order_index
    }).execute()

    lesson_id = lesson.data[0]["id"]

    # Worked example
    we = learn.get("worked_example")
    if we:
        supabase.table("worked_examples").insert({
            "lesson_id": lesson_id,
            "question": we.get("question"),
            "steps": we.get("steps"),
            "final_answer": we.get("final_answer")
        }).execute()

    # Common mistakes — handle list of strings or list of dicts
    mistakes = learn.get("common_mistakes", [])
    for i, mistake in enumerate(mistakes):
        if isinstance(mistake, dict):
            mistake = mistake.get("mistake") or mistake.get("text") or str(mistake)
        supabase.table("common_mistakes").insert({
            "lesson_id": lesson_id,
            "mistake": mistake,
            "order_index": i + 1
        }).execute()

    return lesson_id


def upload_practise_lesson(data: dict, subtopic_id: str, order_index: int):
    practise = data.get("practise") or data

    lesson = supabase.table("lessons").insert({
        "subtopic_id": subtopic_id,
        "lesson_type": "practise",
        "recap": practise.get("recap"),
        "summary": practise.get("summary"),
        "order_index": order_index
    }).execute()

    lesson_id = lesson.data[0]["id"]

    # Questions — handle array format (foundation) and dict format (higher: {Q1: {...}, Q2: {...}})
    questions_raw = practise.get("questions", [])
    if isinstance(questions_raw, dict):
        questions = [{"number": int(k[1:]), **v} for k, v in questions_raw.items()]
    else:
        questions = questions_raw

    for q in questions:
        solution = q.get("solution", {})
        if isinstance(solution, str):
            solution = {"steps": [solution], "final_answer": solution}
        supabase.table("questions").insert({
            "lesson_id": lesson_id,
            "number": q.get("number"),
            "difficulty": q.get("difficulty"),
            "question": q.get("question"),
            "marks": q.get("marks"),
            "solution_steps": solution.get("steps", []),
            "final_answer": solution.get("final_answer")
        }).execute()

    return lesson_id


def process_folder(folder_path: str):
    files = [f for f in os.listdir(folder_path) if f.endswith(".json")]
    print(f"\nProcessing {len(files)} files in {folder_path}...")

    for filename in sorted(files):
        filepath = os.path.join(folder_path, filename)

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Get prefix and map to subtopic code
        prefix = extract_prefix(filename)
        code = SUBTOPIC_CODE_MAP.get(prefix)

        if not code:
            print(f"  SKIP: Could not map prefix '{prefix}' from {filename}")
            continue

        subtopic_id = get_subtopic_id(code)
        if not subtopic_id:
            continue

        lesson_type = "learn" if filename.endswith("_learn.json") else "practise"
        order_index = 1 if lesson_type == "learn" else 2

        if lesson_already_exists(subtopic_id, lesson_type):
            print(f"  SKIP (already uploaded): {filename}")
            continue

        print(f"  Uploading {lesson_type}: {filename}...")

        try:
            if lesson_type == "learn":
                upload_learn_lesson(data, subtopic_id, order_index)
            else:
                upload_practise_lesson(data, subtopic_id, order_index)
            print(f"  ✓ Done")
        except Exception as e:
            print(f"  ✗ Error on {filename}: {e}")


if __name__ == "__main__":
    print("Starting RISE lesson upload...")
    process_folder("output/foundation")
    process_folder("output/higher")
    print("\nUpload complete.")