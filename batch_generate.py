#!/usr/bin/env python3
"""RISE Batch Lesson Generator

Generates all 106 lesson JSON files (53 subtopics x 2 lessons each).
Calls generate_lesson.py for each subtopic sequentially.

Usage:
    python batch_generate.py                      # All tiers
    python batch_generate.py --tier foundation    # Foundation only (72 lessons)
    python batch_generate.py --tier higher        # Higher only (34 lessons)
    python batch_generate.py --resume             # Skip already-generated files
    python batch_generate.py --delay 2.0          # 2 second pause between API calls
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path

from topic_map import FOUNDATION_TOPICS, HIGHER_TOPICS, ALL_TOPICS

OUTPUT_DIR = Path(__file__).parent / "output"


def is_already_generated(subtopic_id: str, tier: str) -> bool:
    """Check if output files already exist for this subtopic."""
    folder = OUTPUT_DIR / tier
    if not folder.exists():
        return False
    prefix = subtopic_id.replace(".", "_") + "_"
    return any(f.name.startswith(prefix) for f in folder.iterdir())


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Batch-generate all RISE lesson pairs via the Anthropic API."
    )
    parser.add_argument(
        "--tier",
        choices=["foundation", "higher"],
        help="Restrict generation to one tier (default: both)",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Skip subtopics that already have output files in /output/",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.5,
        metavar="SECONDS",
        help="Pause between subtopics to avoid rate-limiting (default: 1.5)",
    )
    args = parser.parse_args()

    if args.tier == "foundation":
        topics = FOUNDATION_TOPICS
    elif args.tier == "higher":
        topics = HIGHER_TOPICS
    else:
        topics = ALL_TOPICS

    total = len(topics)
    print(f"Generating {total} lesson pairs ({total * 2} lessons total).")
    if args.resume:
        print("--resume enabled: already-generated subtopics will be skipped.\n")

    succeeded: list[str] = []
    skipped: list[str] = []
    failed: list[str] = []

    for i, (sid, info) in enumerate(topics.items(), start=1):
        label = f"[{i}/{total}] {sid}: {info['subtopic']}"

        if args.resume and is_already_generated(sid, info["tier"]):
            print(f"{label} — skipped (already exists)")
            skipped.append(sid)
            continue

        print(f"\n{label}")
        result = subprocess.run(
            [sys.executable, "generate_lesson.py", "--subtopic-id", sid],
            capture_output=False,
        )

        if result.returncode == 0:
            succeeded.append(sid)
        else:
            print(f"  FAILED — see output above.")
            failed.append(sid)

        if i < total:
            time.sleep(args.delay)

    # Summary
    print("\n" + "=" * 60)
    print(f"Complete.")
    print(f"  Succeeded : {len(succeeded)}")
    print(f"  Skipped   : {len(skipped)}")
    print(f"  Failed    : {len(failed)}")

    if failed:
        print(f"\nFailed subtopic IDs: {', '.join(failed)}")
        print("Re-run with --resume to retry only the failed ones.")

    if succeeded + skipped == total and not failed:
        print("\nAll lessons generated. QA each file before importing to the database.")


if __name__ == "__main__":
    main()
