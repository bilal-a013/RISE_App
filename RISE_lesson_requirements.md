# RISE Tutoring — Lesson Constraints & Requirements

## Overview

Every piece of content generated for RISE must follow these rules without exception.
This document is the source of truth for the content generation pipeline.

---

## Exam Board & Subject Scope

| Property | Value |
|---|---|
| Exam Board | Edexcel GCSE Maths (1MA1) |
| Tiers | Foundation (grades 1–5) and Higher (grades 4–9) |
| Tier handling | Separate paths — students pick Foundation or Higher at onboarding |
| Subject (Phase 1) | Maths only |
| Future subjects | Science (Bio, Chem, Physics), English — later phases |

---

## Content Ownership Rules

- All lesson content must be **original and AI-generated**
- Source material is the **Edexcel specification document only** — not BBC Bitesize, Save My Exams, CGP, or any copyrighted site
- No paraphrasing of copyrighted content — everything must be written from scratch
- RISE owns all generated content outright
- A human must **QA every lesson** before it is marked as published in the database

---

## Lesson Structure Per Subtopic

Every subtopic gets exactly **two lessons**:

### Lesson A — Learn

| Block | Requirement |
|---|---|
| `intro` | 2–3 sentences. What the topic is and why it matters. No waffle. |
| `explanation` | Clear concept explanation written for a GCSE student. Plain English. No unnecessary jargon. |
| `worked_example.question` | One clear, realistic exam-style question |
| `worked_example.steps` | Minimum 3 steps. Each step on its own line. Show all working. |
| `worked_example.final_answer` | Clearly stated final answer |
| `common_mistakes` | Exactly 3 common mistakes. Specific, not generic. |

### Lesson B — Practise

| Block | Requirement |
|---|---|
| `recap` | One sentence only. Reminds student what they learned in Lesson A. |
| `questions` | Exactly 5 questions. See question constraints below. |
| `summary` | 3–4 bullet points. Key things to remember. Concise. |

---

## Question Constraints (Practise Lessons)

Every practise lesson must contain exactly 5 questions in this order:

| Question | Difficulty | Marks |
|---|---|---|
| Q1 | Easy | 1 |
| Q2 | Easy | 2 |
| Q3 | Medium | 3 |
| Q4 | Medium | 3 |
| Q5 | Hard | 4 |

### Per Question Requirements

- Questions must be **exam-style** — realistic Edexcel wording and format
- Each question must include a **full worked solution** with steps
- Each solution must include a **clearly stated final answer**
- Questions must increase in difficulty — Q5 should genuinely stretch a student
- No two questions in the same lesson should test the exact same skill
- Do not repeat questions across lessons for the same subtopic

---

## Tone & Language Rules

- Write for a **GCSE student aged 14–16**
- Use **plain English** — no academic waffle
- Be **direct and clear** — explain it like a good teacher, not a textbook
- **No filler phrases** — e.g. "Great question!", "In this lesson we will explore..."
- Use **UK English spelling** throughout (e.g. colour, factorise, recognise)
- Maths notation should be written clearly — spell out operations in steps (e.g. "Divide both sides by 3")
- Do not use LaTeX in generated content unless the app explicitly renders it

---

## JSON Output Requirements

All lessons are output as JSON. The structure must be followed exactly.

### Learn Lesson JSON Structure

```json
{
  "topic": "string — parent topic name",
  "subtopic": "string — subtopic name",
  "lesson_type": "learn",
  "intro": "string",
  "explanation": "string",
  "worked_example": {
    "question": "string",
    "steps": ["string", "string", "string"],
    "final_answer": "string"
  },
  "common_mistakes": ["string", "string", "string"]
}
```

### Practise Lesson JSON Structure

```json
{
  "topic": "string",
  "subtopic": "string",
  "lesson_type": "practise",
  "recap": "string",
  "questions": [
    {
      "number": 1,
      "difficulty": "easy",
      "question": "string",
      "marks": 1,
      "solution": {
        "steps": ["string", "string"],
        "final_answer": "string"
      }
    }
  ],
  "summary": ["string", "string", "string"]
}
```

### JSON Rules

- Output must be **valid JSON only** — no markdown fences, no preamble, no explanation text
- All string fields must be populated — no empty strings or null values
- `steps` arrays must contain at least 2 items in solutions, at least 3 in worked examples
- `common_mistakes` must contain exactly 3 items
- `questions` must contain exactly 5 items
- `summary` must contain 3–4 items

---

## Topic Map Reference

### Foundation Tier

| ID | Topic | Subtopic |
|---|---|---|
| 1.1 | Number | Order of Operations (BIDMAS) |
| 1.2 | Number | Place Value & Integers |
| 1.3 | Number | The Four Operations |
| 1.4 | Number | Prime Factorisation, HCF & LCM |
| 1.5 | Number | Fractions |
| 1.6 | Number | Decimals |
| 1.7 | Number | Percentages |
| 1.8 | Number | Rounding (d.p. and s.f.) |
| 1.9 | Number | Error Intervals & Bounds (Foundation) |
| 2.1 | Algebra | Algebraic Notation & Vocabulary |
| 2.2 | Algebra | Substitution |
| 2.3 | Algebra | Simplifying & Collecting Like Terms |
| 2.4 | Algebra | Expanding Brackets |
| 2.5 | Algebra | Factorising (including x²+bx+c) |
| 2.6 | Algebra | Solving Linear Equations |
| 2.7 | Algebra | Linear Simultaneous Equations |
| 2.8 | Algebra | Linear Inequalities |
| 2.9 | Algebra | Straight Line Graphs (y=mx+c) |
| 2.10 | Algebra | Quadratic, Cubic & Reciprocal Graphs |
| 3.1 | Ratio, Proportion & Rates of Change | Ratio & Dividing into a Ratio |
| 3.2 | Ratio, Proportion & Rates of Change | Scale Factors & Maps |
| 3.3 | Ratio, Proportion & Rates of Change | Direct Proportion |
| 3.4 | Ratio, Proportion & Rates of Change | Inverse Proportion |
| 3.5 | Ratio, Proportion & Rates of Change | Compound Units (Speed, Density, Pressure) |
| 4.1 | Geometry & Measures | Angle Facts & Parallel Lines |
| 4.2 | Geometry & Measures | Properties of 2D Shapes |
| 4.3 | Geometry & Measures | Perimeter, Area & Volume |
| 4.4 | Geometry & Measures | Ruler & Compass Constructions |
| 4.5 | Geometry & Measures | Transformations |
| 4.6 | Geometry & Measures | Pythagoras' Theorem |
| 4.7 | Geometry & Measures | Trigonometry (sin, cos, tan) |
| 5.1 | Probability | Basic Probability |
| 5.2 | Probability | Combined Events |
| 5.3 | Probability | Venn Diagrams |
| 5.4 | Probability | Tree Diagrams |
| 6.1 | Statistics | Charts & Diagrams |
| 6.2 | Statistics | Averages & Range |

**Total Foundation subtopics: 36 → 72 lessons (36 Learn + 36 Practise)**

---

### Higher Tier (Additional — builds on Foundation)

| ID | Topic | Subtopic |
|---|---|---|
| 1H.1 | Number | Product Rule for Counting |
| 1H.2 | Number | Estimating Powers & Roots |
| 1H.3 | Number | Surds & Rationalising Denominators |
| 1H.4 | Number | Upper & Lower Bounds |
| 2H.1 | Algebra | Factorising ax²+bx+c |
| 2H.2 | Algebra | Composite & Inverse Functions |
| 2H.3 | Algebra | Perpendicular Lines |
| 2H.4 | Algebra | Linear & Quadratic Simultaneous Equations |
| 2H.5 | Algebra | Iteration |
| 3H.1 | Ratio, Proportion & Rates of Change | Gradient as Rate of Change |
| 3H.2 | Ratio, Proportion & Rates of Change | Growth & Decay |
| 4H.1 | Geometry & Measures | Circle Theorems |
| 4H.2 | Geometry & Measures | Sine & Cosine Rules |
| 4H.3 | Geometry & Measures | Vectors |
| 5H.1 | Statistics & Probability | Conditional Probability |
| 5H.2 | Statistics & Probability | Histograms |
| 5H.3 | Statistics & Probability | Cumulative Frequency |

**Total Higher-only subtopics: 17 → 34 lessons (17 Learn + 17 Practise)**

---

## Total Lesson Count (Edexcel Maths)

| Tier | Subtopics | Lessons |
|---|---|---|
| Foundation | 36 | 72 |
| Higher (additional) | 17 | 34 |
| **Total** | **53** | **106** |

---

## Content Pipeline Rules

- Generate one lesson pair at a time (one Learn + one Practise per script run)
- Save each output as a `.json` file named after the subtopic (snake_case)
- All files saved to the `/output` folder before database import
- Do not import any lesson to the database until it has been manually QA'd
- Flag any lesson where the AI output is clearly wrong, vague, or off-spec — regenerate it

---

## QA Checklist (Per Lesson Pair)

Before marking a lesson as approved:

- [ ] Maths in the worked example is correct
- [ ] All 5 practice question answers are correct
- [ ] Difficulty grades are accurate (Q5 genuinely harder than Q1)
- [ ] Language is appropriate for a 14–16 year old
- [ ] UK English spelling throughout
- [ ] No filler, no waffle, no generic phrases
- [ ] JSON structure is valid and complete
- [ ] Content matches the Edexcel spec for this subtopic
- [ ] No content copied or paraphrased from copyrighted sources
