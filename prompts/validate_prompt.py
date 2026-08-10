#!/usr/bin/env python3
"""
Validate Ref2VA clip prompts against the official MiniMax H3 structure.

Checks what a misread spec actually costs: section presence and order, the
350-500 word window, labels used but never declared, shot numbering and cut-time
format, and - the one that silently ruins a clip - whether the highest
<Picture N> matches the number of references the sequence JSON really binds.

That last check needs the sequence, because clips with
use_previous_last_frame_as_ref get the carried frame prepended, so every
reference shifts down one slot.

Usage:
  python prompts/validate_prompt.py sequences/shuizhu_beef_roll_3x5_1080.json
  python prompts/validate_prompt.py --all
  python prompts/validate_prompt.py prompts/h3_3x5_1080/some_clip.md

Exit code 0 when everything passes, 1 on any failure, 2 on a usage error.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SECTIONS = [
    "subject_definitions:",
    "summary:",
    "retention_analysis:",
    "detailed_description:",
    "overall_soundscape:",
    "non_diegetic_music:",
]
MIN_WORDS, MAX_WORDS = 350, 500
VISIBLE_MARKERS = {
    "fully_preserved", "partially_preserved", "attribute_transfer", "weak_reference",
}
AUDIO_MARKERS = {"fully_copy", "partially_copy", "reference", "weak_reference"}


def check(path: Path, expected_refs: int | None = None) -> list[str]:
    text = path.read_text(encoding="utf-8")
    problems: list[str] = []

    found = [line for line in text.splitlines() if re.fullmatch(r"[a-z_]+:", line)]
    if found != SECTIONS:
        problems.append(f"sections are {found or 'none'}, expected {SECTIONS}")
        return problems  # everything below assumes the sections parsed

    body = text.split("detailed_description:")[1].split("overall_soundscape:")[0]
    words = len(body.split())
    if not MIN_WORDS <= words <= MAX_WORDS:
        problems.append(f"detailed_description is {words} words, want {MIN_WORDS}-{MAX_WORDS}")

    declared = set(re.findall(r"^(<Picture \d+>|<Subject \d+>)", text, re.M))
    used = set(re.findall(r"<Picture \d+>|<Subject \d+>", text))
    undeclared = sorted(used - declared)
    if undeclared:
        problems.append(f"used but never declared: {', '.join(undeclared)}")

    pictures = {int(n) for n in re.findall(r"<Picture (\d+)>", text)}
    if pictures and sorted(pictures) != list(range(1, max(pictures) + 1)):
        problems.append(f"<Picture N> numbering has gaps: {sorted(pictures)}")
    if expected_refs is not None and pictures and max(pictures) != expected_refs:
        problems.append(
            f"highest <Picture {max(pictures)}> but the sequence binds {expected_refs} "
            f"references (remember use_previous_last_frame_as_ref prepends one)")

    headings = re.findall(r"\[Shot (\d+)\](?: At (\d\d:\d\d\.\d\d\d),)?", body)
    if len(headings) != 3:
        problems.append(f"{len(headings)} shot headings, expected 3")
    else:
        for i, (num, stamp) in enumerate(headings, start=1):
            if int(num) != i:
                problems.append(f"shot {i} is numbered [Shot {num}]")
            if i == 1 and stamp:
                problems.append("the first shot must not carry a timestamp")
            if i > 1 and not stamp:
                problems.append(f"[Shot {num}] is missing its 'At MM:SS.mmm,' cut time")

    retention = text.split("retention_analysis:")[1].split("detailed_description:")[0]
    for line in retention.strip().splitlines():
        if ":" not in line:
            continue
        marker = line.split(":", 1)[1].strip().split(".")[0].strip()
        if marker and marker not in VISIBLE_MARKERS | AUDIO_MARKERS:
            problems.append(f"unknown retention marker {marker!r}")

    return problems


def refs_for_clip(clip: dict) -> int:
    return len(clip.get("ref_images") or []) + (
        1 if clip.get("use_previous_last_frame_as_ref") else 0)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("targets", nargs="*", help="sequence JSON files or prompt .md files")
    parser.add_argument("--all", action="store_true", help="check every sequences/*_3x5_1080.json")
    args = parser.parse_args(argv)

    targets = [Path(t) for t in args.targets]
    if args.all:
        targets += sorted(Path("sequences").glob("*_3x5_1080.json"))
    if not targets:
        parser.print_usage(sys.stderr)
        return 2

    failed = passed = 0
    for target in targets:
        if not target.is_file():
            print(f"ERROR: not a file: {target}", file=sys.stderr)
            return 2

        if target.suffix == ".json":
            seq = json.loads(target.read_text(encoding="utf-8"))
            print(f"\n{target.name}")
            for clip in seq.get("clips", []):
                prompt = (target.parent / clip["prompt_file"]).resolve()
                if not prompt.is_file():
                    print(f"  MISSING {clip['prompt_file']}")
                    failed += 1
                    continue
                problems = check(prompt, refs_for_clip(clip))
                status = "ok  " if not problems else "FAIL"
                print(f"  {status} {prompt.name}")
                for p in problems:
                    print(f"         ! {p}")
                failed += bool(problems)
                passed += not problems
        else:
            problems = check(target)
            status = "ok  " if not problems else "FAIL"
            print(f"{status} {target.name}  (no sequence given, reference count unchecked)")
            for p in problems:
                print(f"       ! {p}")
            failed += bool(problems)
            passed += not problems

    print(f"\n{passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
