#!/usr/bin/env python3
"""Repository-level validation for the MiniMax H3 workflow."""

from __future__ import annotations

import json
import py_compile
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent

PYTHON_FILES = [
    "check_clip_quality.py",
    "cluster_runner.py",
    "generate_clip_prompts.py",
    "generate_dish_assets.py",
    "h3_accel_runner.py",
    "h3_runner.py",
    "h3_sequence_runner.py",
    "h3_server_setup.py",
    "image2_first_frame.py",
    "make_payload.py",
    "prompts/validate_prompt.py",
]

JSON_ROOTS = [
    "workflows",
    "sequences",
    "prompts/dish_configs",
    "prompts/templates",
]

PRODUCTION_DEFAULT_TARGETS = [
    "README.md",
    "CURRENT_WORKFLOW.md",
    "h3_runner.py",
    "h3_sequence_runner.py",
    "h3_server_setup.py",
    "cluster_runner.py",
    "jobs.example.yaml",
    "servers.example.yaml",
    "server_scripts/install_h3_turbo.sh",
    "server_scripts/run_h3_turbo_probe.sh",
    "docs/runbooks",
    "docs/reference",
]

FORBIDDEN_PRODUCTION_PATTERNS = [
    re.compile(r"h3_i2v_turbo_4step_api"),
    re.compile(r"DEFAULT_TORCH_INDEX\s*=\s*[\"']https://download\.pytorch\.org/whl/cu124[\"']"),
    re.compile(r"DEFAULT_SERVER\s*=\s*[\"']http://127\.0\.0\.1:8188[\"']"),
    re.compile(r"DEFAULT_STEPS\s*=\s*4\b"),
    re.compile(r"DEFAULT_TURBO_STEPS\s*=\s*6\b"),
]


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def run_step(name: str, command: list[str]) -> None:
    print(f"\n== {name}", flush=True)
    result = subprocess.run(command, cwd=ROOT)
    if result.returncode:
        raise SystemExit(result.returncode)


def compile_python() -> None:
    print("\n== Python compile", flush=True)
    for name in PYTHON_FILES:
        path = ROOT / name
        if not path.is_file():
            raise SystemExit(f"missing python file: {name}")
        py_compile.compile(str(path), doraise=True)
    print(f"compiled {len(PYTHON_FILES)} files")


def check_json() -> None:
    print("\n== JSON parse", flush=True)
    files: list[Path] = []
    for root_name in JSON_ROOTS:
        root = ROOT / root_name
        if root.exists():
            files.extend(sorted(root.rglob("*.json")))
    files.extend(sorted((ROOT / "sequence_outputs").glob("*/preproduction/**/*.json")))
    for path in files:
        json.loads(path.read_text(encoding="utf-8"))
    print(f"json ok {len(files)}")


def check_sequence_refs() -> None:
    print("\n== Sequence references", flush=True)
    missing: list[str] = []
    count = 0
    for seq_path in sorted((ROOT / "sequences").glob("*_3x5_1080.json")):
        seq = json.loads(seq_path.read_text(encoding="utf-8"))
        for clip in seq.get("clips") or []:
            for ref in clip.get("ref_images") or []:
                count += 1
                path = (seq_path.parent / ref).resolve()
                if not path.is_file():
                    missing.append(f"{rel(seq_path)}: {ref}")
    if missing:
        raise SystemExit("missing sequence refs:\n" + "\n".join(missing))
    print(f"sequence refs ok {count}")


def collect_steps(value: object, output: list[int]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "steps":
                output.append(child)
            collect_steps(child, output)
    elif isinstance(value, list):
        for child in value:
            collect_steps(child, output)


def check_turbo_workflows() -> None:
    print("\n== Turbo workflow defaults", flush=True)
    bad: list[str] = []
    for path in sorted((ROOT / "workflows").glob("*turbo*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        steps: list[int] = []
        collect_steps(data, steps)
        print(f"{rel(path)} {steps}")
        if steps != [8]:
            bad.append(f"{rel(path)} has steps {steps}, want [8]")
    if bad:
        raise SystemExit("\n".join(bad))


def production_default_files() -> list[Path]:
    files: list[Path] = []
    for target in PRODUCTION_DEFAULT_TARGETS:
        path = ROOT / target
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            files.extend(sorted(path.rglob("*")))
    return [p for p in files if p.is_file()]


def check_old_production_defaults() -> None:
    print("\n== Old production-default scan", flush=True)
    hits: list[str] = []
    for path in production_default_files():
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            for pattern in FORBIDDEN_PRODUCTION_PATTERNS:
                if pattern.search(line):
                    hits.append(f"{rel(path)}:{lineno}: {line}")
    if hits:
        raise SystemExit("old production defaults remain:\n" + "\n".join(hits))
    print("old production defaults ok")


def main() -> int:
    run_step("Generated config dry-run", [sys.executable, "generate_clip_prompts.py", "--all", "--check"])
    run_step("Prompt validator", [sys.executable, "prompts/validate_prompt.py", "--all"])
    compile_python()
    check_json()
    check_sequence_refs()
    check_turbo_workflows()
    check_old_production_defaults()
    print("\nrepo check ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
