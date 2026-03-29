#!/usr/bin/env python3
"""RISE Lesson Generator — GUI
Run with: python gui.py
No extra installs needed beyond google-genai.
"""

import json
import os
import re
import sys
import threading
import time
from pathlib import Path
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

try:
    from google import genai
    from google.genai import types
except ImportError:
    import tkinter as tk
    from tkinter import messagebox
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Missing package", "Run this first:\n\npip install google-genai")
    sys.exit(1)

from topic_map import ALL_TOPICS, FOUNDATION_TOPICS, HIGHER_TOPICS

OUTPUT_DIR = Path(__file__).parent / "output"
MODEL = "gemini-2.0-flash-lite"

# Free tier: 30 requests per minute. One call every 3 seconds = 20 RPM — safely under the limit.
CALL_DELAY_SECONDS = 3

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
    "steps": ["Step 1 — show all working", "Step 2", "Step 3"],
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
    {{"number": 1, "difficulty": "easy", "marks": 1, "question": "Exam-style question", "solution": {{"steps": ["Step 1", "Step 2"], "final_answer": "Answer"}}}},
    {{"number": 2, "difficulty": "easy", "marks": 2, "question": "Exam-style question", "solution": {{"steps": ["Step 1", "Step 2"], "final_answer": "Answer"}}}},
    {{"number": 3, "difficulty": "medium", "marks": 3, "question": "Exam-style question", "solution": {{"steps": ["Step 1", "Step 2", "Step 3"], "final_answer": "Answer"}}}},
    {{"number": 4, "difficulty": "medium", "marks": 3, "question": "Exam-style question", "solution": {{"steps": ["Step 1", "Step 2", "Step 3"], "final_answer": "Answer"}}}},
    {{"number": 5, "difficulty": "hard", "marks": 4, "question": "Exam-style question", "solution": {{"steps": ["Step 1", "Step 2", "Step 3", "Step 4"], "final_answer": "Answer"}}}}
  ],
  "summary": ["Key point 1", "Key point 2", "Key point 3"]
}}

Constraints:
- recap: exactly one sentence
- questions: exactly 5 in the order shown (easy 1mk, easy 2mk, medium 3mk, medium 3mk, hard 4mk)
- each question must test a different skill
- Q5 must genuinely stretch a student
- each solution must show at least 2 steps and a clearly stated final answer
- summary: 3-4 bullet points, concise and useful\
"""


def subtopic_to_snake(subtopic_id: str, subtopic_name: str) -> str:
    prefix = subtopic_id.replace(".", "_")
    name = subtopic_name.lower()
    name = re.sub(r"[''']", "", name)
    name = re.sub(r"[^a-z0-9]+", "_", name)
    name = name.strip("_")
    return f"{prefix}_{name}"


def strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        inner = lines[1:-1] if lines[-1].strip() == "```" else lines[1:]
        text = "\n".join(inner)
    return text.strip()


def is_already_generated(subtopic_id: str, tier: str) -> bool:
    folder = OUTPUT_DIR / tier
    if not folder.exists():
        return False
    prefix = subtopic_id.replace(".", "_") + "_"
    return any(f.name.startswith(prefix) for f in folder.iterdir())


def call_gemini(client, user_prompt: str, log_fn) -> dict:
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
            time.sleep(CALL_DELAY_SECONDS)
            return result
        except Exception as e:
            msg = str(e)
            if "429" in msg or "RESOURCE_EXHAUSTED" in msg or "quota" in msg.lower():
                wait = 65 * (attempt + 1)
                log_fn(f"  ⏳ Rate limited — waiting {wait}s (attempt {attempt + 1}/3)...")
                time.sleep(wait)
            else:
                raise
    raise RuntimeError("Failed after 3 attempts due to rate limiting.")


# ---------------------------------------------------------------------------
# GUI
# ---------------------------------------------------------------------------

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("RISE Lesson Generator")
        self.resizable(True, True)
        self.minsize(700, 520)
        self._running = False
        self._thread = None
        self._build_ui()

    def _build_ui(self):
        pad = {"padx": 12, "pady": 6}

        # ── API Key ──
        key_frame = ttk.LabelFrame(self, text="Gemini API Key", padding=8)
        key_frame.pack(fill="x", **pad)

        self.key_var = tk.StringVar()
        self.key_entry = ttk.Entry(key_frame, textvariable=self.key_var, show="•", width=60)
        self.key_entry.pack(side="left", fill="x", expand=True)

        self.show_btn = ttk.Button(key_frame, text="Show", width=6, command=self._toggle_key)
        self.show_btn.pack(side="left", padx=(6, 0))

        help_lbl = ttk.Label(key_frame, text="Get free key → aistudio.google.com/apikey",
                             foreground="#0078d4", cursor="hand2")
        help_lbl.pack(side="left", padx=(10, 0))

        # ── Options ──
        opt_frame = ttk.LabelFrame(self, text="Options", padding=8)
        opt_frame.pack(fill="x", **pad)

        ttk.Label(opt_frame, text="Tier:").grid(row=0, column=0, sticky="w")
        self.tier_var = tk.StringVar(value="both")
        for i, (val, lbl) in enumerate([("both", "Both"), ("foundation", "Foundation only"),
                                        ("higher", "Higher only")]):
            ttk.Radiobutton(opt_frame, text=lbl, variable=self.tier_var,
                            value=val).grid(row=0, column=i + 1, padx=8, sticky="w")

        self.resume_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(opt_frame, text="Skip already-generated files (resume)",
                        variable=self.resume_var).grid(row=1, column=0, columnspan=4,
                                                       sticky="w", pady=(4, 0))

        # ── Progress ──
        prog_frame = ttk.LabelFrame(self, text="Progress", padding=8)
        prog_frame.pack(fill="x", **pad)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(prog_frame, variable=self.progress_var,
                                            maximum=100, length=400)
        self.progress_bar.pack(fill="x")

        self.status_var = tk.StringVar(value="Ready.")
        ttk.Label(prog_frame, textvariable=self.status_var).pack(anchor="w", pady=(4, 0))

        # ── File list ──
        files_frame = ttk.LabelFrame(self, text="Generated Files", padding=8)
        files_frame.pack(fill="both", expand=True, **pad)

        cols = ("file", "status")
        self.tree = ttk.Treeview(files_frame, columns=cols, show="headings", height=8)
        self.tree.heading("file", text="File")
        self.tree.heading("status", text="Status")
        self.tree.column("file", width=500)
        self.tree.column("status", width=120, anchor="center")

        sb = ttk.Scrollbar(files_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self.tree.tag_configure("ok", foreground="#107c10")
        self.tree.tag_configure("skip", foreground="#888888")
        self.tree.tag_configure("fail", foreground="#c50f1f")

        # ── Log ──
        log_frame = ttk.LabelFrame(self, text="Log", padding=8)
        log_frame.pack(fill="both", expand=True, **pad)

        self.log = scrolledtext.ScrolledText(log_frame, height=8, state="disabled",
                                             font=("Consolas", 9))
        self.log.pack(fill="both", expand=True)

        # ── Buttons ──
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=12, pady=(0, 12))

        self.run_btn = ttk.Button(btn_frame, text="▶  Generate Lessons",
                                  command=self._start, style="Accent.TButton")
        self.run_btn.pack(side="left")

        self.stop_btn = ttk.Button(btn_frame, text="⏹  Stop", command=self._stop,
                                   state="disabled")
        self.stop_btn.pack(side="left", padx=8)

        ttk.Label(btn_frame, text="Output saved to: output/foundation/ and output/higher/",
                  foreground="#555").pack(side="right")

    def _toggle_key(self):
        if self.key_entry.cget("show") == "•":
            self.key_entry.config(show="")
            self.show_btn.config(text="Hide")
        else:
            self.key_entry.config(show="•")
            self.show_btn.config(text="Show")

    def _log(self, msg: str):
        self.log.config(state="normal")
        self.log.insert("end", msg + "\n")
        self.log.see("end")
        self.log.config(state="disabled")

    def _add_file_row(self, filename: str, status: str, tag: str):
        self.tree.insert("", "end", values=(filename, status), tags=(tag,))
        self.tree.yview_moveto(1)

    def _set_status(self, msg: str):
        self.status_var.set(msg)

    def _start(self):
        api_key = self.key_var.get().strip()
        if not api_key:
            messagebox.showwarning("API Key Missing", "Please enter your Gemini API key.")
            return

        self._running = True
        self.run_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.tree.delete(*self.tree.get_children())

        tier = self.tier_var.get()
        resume = self.resume_var.get()

        self._thread = threading.Thread(
            target=self._run_generation,
            args=(api_key, tier, resume),
            daemon=True,
        )
        self._thread.start()

    def _stop(self):
        self._running = False
        self._log("⏹ Stop requested — will stop after current lesson finishes.")
        self.stop_btn.config(state="disabled")

    def _run_generation(self, api_key: str, tier: str, resume: bool):
        try:
            client = genai.Client(api_key=api_key)
        except Exception as e:
            self.after(0, self._log, f"Error creating client: {e}")
            self.after(0, self._finish)
            return

        if tier == "foundation":
            topics = FOUNDATION_TOPICS
        elif tier == "higher":
            topics = HIGHER_TOPICS
        else:
            topics = ALL_TOPICS

        total = len(topics)
        done = 0

        for sid, info in topics.items():
            if not self._running:
                break

            t = info["tier"]
            topic = info["topic"]
            subtopic = info["subtopic"]
            label = f"[{sid}] {subtopic}"

            if resume and is_already_generated(sid, t):
                self.after(0, self._log, f"⏭  Skipped (exists): {label}")
                self.after(0, self._add_file_row, label, "Skipped", "skip")
                done += 1
                self.after(0, self.progress_var.set, (done / total) * 100)
                continue

            self.after(0, self._set_status, f"Generating: {label}")
            self.after(0, self._log, f"\n⚙  {label}")

            base = subtopic_to_snake(sid, subtopic)

            # --- Learn ---
            try:
                self.after(0, self._log, "  → Learn lesson...")
                learn_data = call_gemini(
                    client,
                    LEARN_PROMPT.format(topic=topic, subtopic=subtopic, tier=t),
                    lambda msg: self.after(0, self._log, msg),
                )
                folder = OUTPUT_DIR / t
                folder.mkdir(parents=True, exist_ok=True)
                path = folder / f"{base}_learn.json"
                path.write_text(json.dumps(learn_data, indent=2, ensure_ascii=False),
                                encoding="utf-8")
                self.after(0, self._log, f"  ✔ Saved: {path.name}")
                self.after(0, self._add_file_row, path.name, "✔ Saved", "ok")
            except Exception as e:
                self.after(0, self._log, f"  ✖ Learn FAILED: {e}")
                self.after(0, self._add_file_row, f"{base}_learn.json", "✖ Failed", "fail")

            if not self._running:
                break

            # --- Practise ---
            try:
                self.after(0, self._log, "  → Practise lesson...")
                practise_data = call_gemini(
                    client,
                    PRACTISE_PROMPT.format(topic=topic, subtopic=subtopic, tier=t),
                    lambda msg: self.after(0, self._log, msg),
                )
                folder = OUTPUT_DIR / t
                folder.mkdir(parents=True, exist_ok=True)
                path = folder / f"{base}_practise.json"
                path.write_text(json.dumps(practise_data, indent=2, ensure_ascii=False),
                                encoding="utf-8")
                self.after(0, self._log, f"  ✔ Saved: {path.name}")
                self.after(0, self._add_file_row, path.name, "✔ Saved", "ok")
            except Exception as e:
                self.after(0, self._log, f"  ✖ Practise FAILED: {e}")
                self.after(0, self._add_file_row, f"{base}_practise.json", "✖ Failed", "fail")

            done += 1
            self.after(0, self.progress_var.set, (done / total) * 100)

        self.after(0, self._finish)

    def _finish(self):
        self._running = False
        self.run_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self._set_status("Done. QA each file before importing to the database.")
        self._log("\n✅ Generation complete.")


if __name__ == "__main__":
    app = App()
    app.mainloop()
