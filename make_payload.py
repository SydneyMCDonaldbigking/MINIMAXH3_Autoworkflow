#!/usr/bin/env python3
"""
Pack everything a fresh render server needs into one archive.

Exists because three hand-made payload tarballs accumulated in the repo root,
nobody could say what was inside them, and they were eventually deleted on that
basis. A payload should be derived, reproducible and self-describing, never
assembled by hand.

What goes in: the runner scripts, the sequence JSONs you name, the prompts they
reference, every reference image they bind, the product images and brand logos,
and the server-side scripts. What stays out: models, outputs, git history, and
anything holding a secret.

Every archive carries a MANIFEST.txt listing its contents, the sequences it was
built for, and the command that produced it, so a stray copy can always explain
itself.

Examples:
  python make_payload.py --all
  python make_payload.py --sequence sequences/shuizhu_beef_roll_3x5_1080.json
  python make_payload.py --all --list
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import sys
import tarfile

ROOT = pathlib.Path(__file__).resolve().parent

# Always shipped: without these the server cannot run a sequence at all.
CORE = [
    "h3_runner.py",
    "h3_sequence_runner.py",
    "h3_accel_runner.py",
    "check_clip_quality.py",
    "prompts/validate_prompt.py",
    "server_scripts/check_bf16_mma.sh",
    "server_scripts/bf16_mma_acceptance.cu",
    "server_scripts/diagnose_h3_black.sh",
    "server_scripts/install_h3_turbo.sh",
    "CURRENT_WORKFLOW.md",
]

# Never shipped, whatever else matches. Secrets and machine-specific config.
NEVER = {".env", ".env.local", "servers.yaml", "jobs.yaml"}


def collect(sequences: list[pathlib.Path]) -> tuple[list[pathlib.Path], list[str]]:
    """Resolve every file the given sequences depend on. Returns (files, warnings)."""
    files: set[pathlib.Path] = set()
    warnings: list[str] = []

    for rel in CORE:
        path = ROOT / rel
        if path.is_file():
            files.add(path)
        else:
            warnings.append(f"core file missing, not packed: {rel}")

    for seq_path in sequences:
        if not seq_path.is_file():
            warnings.append(f"sequence not found: {seq_path}")
            continue
        files.add(seq_path)
        seq = json.loads(seq_path.read_text(encoding="utf-8"))

        for clip in seq.get("clips", []):
            prompt = (seq_path.parent / clip["prompt_file"]).resolve()
            if prompt.is_file():
                files.add(prompt)
            else:
                warnings.append(f"{seq_path.name}: prompt missing {clip['prompt_file']}")

            for ref in clip.get("ref_images", []):
                image = (seq_path.parent / ref).resolve()
                if image.is_file():
                    files.add(image)
                else:
                    warnings.append(f"{seq_path.name}: reference missing {ref}")

    for path in sorted(files):
        if path.name in NEVER:
            raise SystemExit(f"refusing to pack a secret: {path}")

    return sorted(files), warnings


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--sequence", action="append", default=[],
                        help="sequence JSON to include, repeatable")
    parser.add_argument("--all", action="store_true",
                        help="include every sequences/*_3x5_1080.json")
    parser.add_argument("--out", default=None, help="output path for the archive")
    parser.add_argument("--list", action="store_true",
                        help="show what would be packed and exit")
    args = parser.parse_args(argv)

    sequences = [pathlib.Path(s).resolve() for s in args.sequence]
    if args.all:
        sequences += sorted((ROOT / "sequences").glob("*_3x5_1080.json"))
    if not sequences:
        parser.error("give --sequence or --all")
    sequences = sorted(set(sequences))

    files, warnings = collect(sequences)
    total = sum(f.stat().st_size for f in files)

    for w in warnings:
        print(f"  warning: {w}", file=sys.stderr)

    if args.list:
        for f in files:
            print(f"  {f.stat().st_size:>9}  {f.relative_to(ROOT).as_posix()}")
        print(f"\n{len(files)} files, {total / 1048576:.1f} MB")
        return 1 if warnings else 0

    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M")
    names = "_".join(s.stem.replace("_3x5_1080", "") for s in sequences)
    if len(names) > 60:
        names = f"{len(sequences)}_sequences"
    out = pathlib.Path(args.out) if args.out else ROOT / f"payload_{names}_{stamp}.tar.gz"

    manifest = [
        "MiniMax H3 render payload",
        f"built    {dt.datetime.now().isoformat(timespec='seconds')}",
        f"command  python {pathlib.Path(__file__).name} "
        + " ".join(f"--sequence {s.relative_to(ROOT).as_posix()}" for s in sequences),
        "",
        "sequences:",
        *(f"  {s.relative_to(ROOT).as_posix()}" for s in sequences),
        "",
        "unpack on the server with:",
        "  tar xzf <this file> -C /root/ComfyUI",
        "",
        f"contents ({len(files)} files, {total / 1048576:.1f} MB):",
        *(f"  {f.relative_to(ROOT).as_posix()}" for f in files),
        "",
    ]
    if warnings:
        manifest += ["warnings at build time:", *(f"  {w}" for w in warnings), ""]

    manifest_path = ROOT / "MANIFEST.txt"
    manifest_path.write_text("\n".join(manifest), encoding="utf-8", newline="\n")
    try:
        with tarfile.open(out, "w:gz") as tar:
            tar.add(manifest_path, arcname="MANIFEST.txt")
            for f in files:
                tar.add(f, arcname=f.relative_to(ROOT).as_posix())
    finally:
        manifest_path.unlink(missing_ok=True)

    print(f"{out.name}")
    print(f"  {len(files)} files, {total / 1048576:.1f} MB in, "
          f"{out.stat().st_size / 1048576:.1f} MB packed")
    print(f"  sequences: {', '.join(s.stem for s in sequences)}")
    if warnings:
        print(f"  {len(warnings)} warnings, see MANIFEST.txt inside the archive")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
