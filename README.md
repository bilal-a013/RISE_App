# RISE Lesson Generator

Automated pipeline for generating RISE GCSE Maths lesson content via the Anthropic API (Claude).

## Structure

```
RISE_App/
├── generate_lesson.py          # Generate one lesson pair (Learn + Practise)
├── batch_generate.py           # Generate all 106 lesson pairs
├── topic_map.py                # All 53 subtopics (Foundation + Higher)
├── requirements.txt
├── RISE_lesson_requirements.md # Source of truth for content rules
└── output/
    ├── foundation/             # 72 Foundation lesson JSON files
    └── higher/                 # 34 Higher lesson JSON files
```

## Setup

**1. Install Python dependencies**
```
pip install -r requirements.txt
```

**2. Get a free Gemini API key**

Go to https://aistudio.google.com/apikey, sign in with a Google account, and create a key.
The free tier gives **1,500 requests/day** — enough to generate all 106 lessons in one run.

**3. Set your API key**

Windows (Command Prompt):
```
set GEMINI_API_KEY=AIza...
```

Windows (PowerShell):
```
$env:GEMINI_API_KEY = "AIza..."
```

macOS / Linux:
```
export GEMINI_API_KEY=AIza...
```

## Generating lessons

**Single lesson pair (recommended for testing and QA):**
```
python generate_lesson.py --subtopic-id 1.1
python generate_lesson.py --subtopic-id 2H.3
```

**List all available subtopic IDs:**
```
python generate_lesson.py --list
```

**All Foundation lessons (72 JSON files):**
```
python batch_generate.py --tier foundation
```

**All Higher lessons (34 JSON files):**
```
python batch_generate.py --tier higher
```

**All 106 lessons:**
```
python batch_generate.py
```

**Resume a batch that was interrupted:**
```
python batch_generate.py --resume
```

## Output file naming

Files are saved to `output/<tier>/` using the pattern:
```
{subtopic_id}_{subtopic_name_snake_case}_{lesson_type}.json
```

Examples:
- `output/foundation/1_1_order_of_operations_bidmas_learn.json`
- `output/foundation/1_1_order_of_operations_bidmas_practise.json`
- `output/higher/1H_3_surds_rationalising_denominators_learn.json`

## Which AI model

The scripts use **Gemini 2.0 Flash** (via Google AI Studio API). This model is the recommended choice for this pipeline because:

- **Free tier**: 1,500 requests/day — enough for all 106 lessons at no cost
- Reliably follows strict JSON structure requirements
- Produces high-quality, spec-aligned educational content
- Handles UK English and Edexcel-style wording well

## QA checklist

Before importing any lesson to the database, verify:

- [ ] Maths in the worked example is correct
- [ ] All 5 practice question answers are correct
- [ ] Difficulty grades are accurate (Q5 genuinely harder than Q1)
- [ ] Language is appropriate for a 14–16 year old
- [ ] UK English spelling throughout
- [ ] No filler phrases or waffle
- [ ] JSON structure is valid and complete
- [ ] Content matches the Edexcel spec for this subtopic

## Cost estimate

**Free.** The Gemini free tier (Google AI Studio) allows 1,500 requests/day.
The full 106-lesson run requires 212 API calls — completable in a single session at no cost.

Sign up at https://aistudio.google.com/apikey (requires a Google account).
