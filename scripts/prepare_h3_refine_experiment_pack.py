#!/usr/bin/env python3
"""
Prepare a MiniMax H3 refine experiment handoff pack.

This tool is intentionally no-submit: it only writes prompts, manifests, and
PowerShell command files for another agent/operator to inspect and run later.
It never queues ComfyUI and never imports the runner modules.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SERVER = "http://127.0.0.1:8189"
DEFAULT_OUTPUT_ROOT = WORKSPACE_ROOT / "local_artifacts" / "h3_refine_experiments"
DEFAULT_TURBO_LORA = "minimax_h3_turbo_v4_step600_ema.safetensors"


@dataclass(frozen=True)
class CommandVariant:
    variant_id: str
    title: str
    runner: str
    width: int | None = None
    height: int | None = None
    steps: int | None = None
    extra_args: tuple[str, ...] = ()
    objective: str = ""
    caveat: str = ""
    submit_ready: bool = True


COMMAND_VARIANTS = [
    CommandVariant(
        variant_id="A_native1080_turbo_single",
        title="Current production baseline: native 1080 vertical, Turbo LoRA, single sampler",
        runner="h3_runner.py",
        objective="Anchor quality, timing, product identity, and food-state behavior against the known stable flow.",
    ),
    CommandVariant(
        variant_id="B_native1080_turbo_sigma_default",
        title="Native 1080 + Turbo LoRA + sigma schedule/refine probe",
        runner="h3_accel_runner.py",
        extra_args=("--sigma-shift", "12.0"),
        objective="Check whether the installed sigma node changes dynamic grain or distant detail without lowering native resolution.",
        caveat=(
            "This is a probe for locally installed sigma nodes. Official MiniMaxH3SigmaShift at its default "
            "may be a no-op; if Claude finds a separate H3 Sigma Refiner node, wire and record that exact class name."
        ),
    ),
    CommandVariant(
        variant_id="C_native1080_turbo_sigma8",
        title="Native 1080 + Turbo LoRA + non-default sigma stress test",
        runner="h3_accel_runner.py",
        extra_args=("--sigma-shift", "8.0", "--sigma-shift-audio", "3.0"),
        objective="Test a visible sigma perturbation after the default/probe run is known to build.",
        caveat="Run only after B builds cleanly; abort this branch if sampler tensor shapes mismatch.",
    ),
    CommandVariant(
        variant_id="D_native1080_turbo_accel_sage_only",
        title="Native 1080 + Turbo LoRA + acceleration chain, SolAttention disabled first",
        runner="h3_accel_runner.py",
        extra_args=("--accel", "--accel-set", "enable_sol_attn=false"),
        objective="Measure speed/VRAM impact separately from quality changes.",
        caveat="This is a performance experiment. It should not be treated as the small-face fix unless quality also improves.",
    ),
]


MANUAL_VARIANTS = [
    {
        "variant_id": "E_halfres_dual_sampler_latent_upscale",
        "title": "Half-resolution latent path: dual sampler + AV split/merge + latent upscale",
        "initial_vertical_size": "544x960",
        "target_vertical_size": "1088x1920, then crop to 1080x1920",
        "why_not_default": (
            "The referenced online workflow starts from a low-resolution latent and refines after upscaling. "
            "That is a different tradeoff from our current native 1080 product/cooking commercial path."
        ),
        "required_node_candidates": {
            "dual_sigma_sampler": ["RHMiniMaxH3DualSigmaSampler"],
            "av_latent_split": ["RHMiniMaxH3SeparateAVLatent"],
            "av_latent_combine": ["RHMiniMaxH3CombineAVLatent"],
            "sigma_refine_or_shift": [
                "MiniMaxH3SigmaShift",
                "ModelSamplingAV",
                "RHMiniMaxH3DualSigmaSampler",
                "JR_H3_UnifiedAcceleration",
            ],
            "latent_upscale": [
                "any installed LATENT upscaler that accepts the video latent only",
                "LTX-style latent upscale node if present",
            ],
        },
        "claude_action": (
            "Do not fake this with pixel upscaling. Build this only after /object_info confirms the actual node classes "
            "and input sockets. Save the ComfyUI API JSON before submitting one 5s clip."
        ),
    },
    {
        "variant_id": "F_lightx2v_compatibility_probe",
        "title": "LIGHTX2V compatibility probe",
        "initial_vertical_size": "1088x1920 first, not half-res",
        "target_vertical_size": "1088x1920, then crop to 1080x1920",
        "why_not_default": (
            "LIGHTX2V may be another LoRA/model patch. Do not stack it with Turbo LoRA until a single-clip compatibility "
            "run proves it does not cause product drift, over-sharpening, or sampler instability."
        ),
        "required_node_candidates": {
            "lightx2v_loader_or_lora": ["the exact LIGHTX2V 0.1 node/model from the shared workflow package"],
        },
        "claude_action": (
            "If LIGHTX2V is only available inside a workflow JSON, inspect the graph and record the loader class, model name, "
            "strength 0.75, and placement relative to Turbo LoRA before running."
        ),
    },
]


class PackError(RuntimeError):
    pass


def now_id() -> str:
    return dt.datetime.now().strftime("%Y%m%d_%H%M%S")


def slug(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9._-]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "h3-refine"


def ps_quote(value: str | Path) -> str:
    text = str(value)
    return "'" + text.replace("'", "''") + "'"


def ps_join(args: list[str | Path]) -> str:
    return " ".join(ps_quote(item) for item in args)


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PackError(f"Invalid JSON: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise PackError(f"Expected a JSON object: {path}")
    return data


def resolve_path(value: str, base_dir: Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return (base_dir / path).resolve()


def merged_clip_defaults(sequence: dict[str, Any], clip: dict[str, Any]) -> dict[str, Any]:
    defaults = sequence.get("defaults") or {}
    if not isinstance(defaults, dict):
        defaults = {}
    merged = dict(defaults)
    merged.update(clip)
    return merged


def read_clip_prompt(clip: dict[str, Any], sequence_dir: Path, target: Path) -> tuple[Path, list[str]]:
    warnings: list[str] = []
    prompt_text = str(clip.get("prompt") or "").strip()
    source = None
    if clip.get("prompt_file"):
        source = resolve_path(str(clip["prompt_file"]), sequence_dir)
        if source.exists():
            prompt_text = source.read_text(encoding="utf-8").strip()
        else:
            warnings.append(f"Missing prompt_file: {source}")
    if not prompt_text:
        prompt_text = "TODO: add the confirmed MiniMax H3 prompt before running this experiment."
        warnings.append(f"Clip {clip.get('id', 'unknown')} has no prompt text.")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(prompt_text + "\n", encoding="utf-8", newline="\n")
    return target, warnings


def bool_enabled(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


def selected_clips(sequence: dict[str, Any], all_clips: bool, clip_count: int) -> list[dict[str, Any]]:
    clips = sequence.get("clips")
    if not isinstance(clips, list) or not clips:
        raise PackError("Sequence JSON must contain a non-empty clips array.")
    if all_clips:
        return [clip for clip in clips if isinstance(clip, dict)]
    return [clip for clip in clips if isinstance(clip, dict)][:clip_count]


def command_for_clip(
    *,
    python_exe: str,
    workspace_root: Path,
    server: str,
    variant: CommandVariant,
    clip: dict[str, Any],
    clip_id: str,
    prompt_path: Path,
    api_json_path: Path,
    output_dir: Path,
    sequence_dir: Path,
    submit: bool,
) -> list[str]:
    width = variant.width or int(clip.get("width", 1088))
    height = variant.height or int(clip.get("height", 1920))
    steps = variant.steps or int(clip.get("steps", 8))
    mode = str(clip.get("mode", "r2v"))
    command: list[str | Path] = [
        python_exe,
        workspace_root / variant.runner,
        mode,
        "--server",
        server,
        "--prompt-file",
        prompt_path,
        "--width",
        str(width),
        "--height",
        str(height),
        "--duration",
        str(float(clip.get("duration", 5.0))),
        "--steps",
        str(steps),
        "--seed",
        str(int(clip.get("seed", 26081801))),
        "--prefix",
        f"experiment/{clip_id}/{variant.variant_id}",
        "--output-dir",
        output_dir,
        "--poll",
        str(float(clip.get("poll", 10))),
        "--timeout",
        str(float(clip.get("timeout", 10800))),
        "--save-api-json",
        api_json_path,
    ]
    if not submit:
        command.append("--no-submit")
    if bool_enabled(clip.get("turbo"), default=True):
        command.append("--turbo")
        command.extend(["--turbo-lora", DEFAULT_TURBO_LORA])
    if bool_enabled(clip.get("turbo_low_vram"), default=True):
        command.append("--turbo-low-vram")
    if bool_enabled(clip.get("no_audio"), default=True):
        command.append("--no-audio")
    command.append("--overwrite-upload")
    if mode == "r2v":
        command.extend(["--ref-image-size", str(clip.get("ref_image_size", "match"))])
        for image in clip.get("ref_images") or []:
            command.extend(["--ref-image", resolve_path(str(image), sequence_dir)])
    elif mode == "i2v":
        if clip.get("first_frame"):
            command.extend(["--first-frame", resolve_path(str(clip["first_frame"]), sequence_dir)])
    elif mode == "flf2v":
        if clip.get("first_frame"):
            command.extend(["--first-frame", resolve_path(str(clip["first_frame"]), sequence_dir)])
        if clip.get("last_frame"):
            command.extend(["--last-frame", resolve_path(str(clip["last_frame"]), sequence_dir)])
    command.extend(variant.extra_args)
    return [str(item) for item in command]


def render_static_plan() -> str:
    manual = json.dumps(MANUAL_VARIANTS, ensure_ascii=False, indent=2)
    return f"""# Claude Handoff: MiniMax H3 Refine Experiments

This pack is no-submit by design. The generated `commands.build_api_json.ps1`
only builds/saves API JSON with `--no-submit`. `commands.submit_real_runs.ps1.disabled`
is intentionally disabled and must not be renamed or edited until the user gives
explicit approval to burn GPU time.

## Goal

Test whether the online "dual sampler + sigma refine + latent upscale" idea has
anything worth borrowing for our MiniMax H3 workflow, without replacing the
current production path.

Current production baseline:

- MiniMax H3 Ref2VA
- Native vertical `1088x1920`, crop to `1080x1920`
- `8` steps
- `minimax_h3_turbo_v4_step600_ema.safetensors`
- `--turbo-low-vram`
- `--no-audio`
- Separate 5s clips, no concat unless explicitly requested

## Key Hypothesis

The referenced online workflow appears to start at a low-resolution latent
(`960x544` in the horizontal example), then split A/V latent, upscale only the
video latent, merge A/V back together, and run a second sampler. That is not the
same as our native 1080 workflow.

For our vertical workflow, the fair half-resolution analogue is `544x960` ->
latent upscale -> `1088x1920` -> crop to `1080x1920`.

## Command Variants

{json.dumps([variant.__dict__ for variant in COMMAND_VARIANTS], ensure_ascii=False, indent=2)}

## Manual Graph Variants

These are not generated as runnable commands because the exact local ComfyUI
node class names and socket signatures must be confirmed from `/object_info`
first.

```json
{manual}
```

## Claude Rules

1. Probe nodes before any experimental run:
   `python h3_accel_runner.py --probe --server http://127.0.0.1:8189`
2. Build and save API JSON first. Do not submit blind workflow JSON.
3. Run only one 5s clip first, ideally clip 01 from the video-rewrite package.
4. Keep the current Turbo LoRA enabled for baseline/sigma tests.
5. Do not stack LIGHTX2V with Turbo until the LIGHTX2V loader/model placement is known.
6. Treat low-res latent upscale as a separate experiment, not a replacement for native 1080.
7. Record the exact node class names, model filenames, LoRA strengths, seeds, run seconds, and output paths.

## Scoring Sheet

Use 1-5 for each output:

- Product identity / dish identity consistency
- Small face integrity if people appear
- Dynamic grain / pixel breakup
- Food or product texture truth
- Camera stability
- Hands and object interaction
- Text/UI hallucination control
- End frame usefulness for clip handoff

Promotion rule:

- Native 1080 stays production unless a variant improves quality without product drift.
- Half-res latent upscale can become an optional people/high-motion branch only if it beats native 1080 on the same seed and prompt.
- Speed-only acceleration is useful only after output quality is acceptable.
"""


def write_lines(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8", newline="\n")


def build_pack(args: argparse.Namespace) -> Path:
    sequence_path = Path(args.sequence).expanduser().resolve()
    if not sequence_path.exists():
        raise PackError(f"Sequence JSON not found: {sequence_path}")
    sequence = load_json(sequence_path)
    sequence_dir = sequence_path.parent
    sequence_id = slug(str(sequence.get("sequence_id") or sequence_path.stem))
    pack_id = slug(args.experiment_id or f"{sequence_id}-{now_id()}")
    pack_dir = Path(args.output_root).expanduser().resolve() / pack_id

    clips = selected_clips(sequence, args.all_clips, args.clip_count)
    server = args.server or str(sequence.get("server") or DEFAULT_SERVER)
    build_commands: list[str] = [
        "# Generated by scripts/prepare_h3_refine_experiment_pack.py",
        "# Safe file: every command includes --no-submit.",
        "$ErrorActionPreference = \"Stop\"",
        "",
        f"# Source sequence: {sequence_path}",
        "",
    ]
    submit_commands: list[str] = [
        "# Generated by scripts/prepare_h3_refine_experiment_pack.py",
        "# Disabled by default. Remove this throw only after explicit user approval.",
        "throw 'GPU submission commands are disabled by default. Read README_CLAUDE_HANDOFF.md first.'",
        "",
        "$ErrorActionPreference = \"Stop\"",
        "",
        f"# Source sequence: {sequence_path}",
        "",
    ]
    manifest: dict[str, Any] = {
        "pack_id": pack_id,
        "created_at": dt.datetime.now().isoformat(timespec="seconds"),
        "source_sequence": str(sequence_path),
        "server": server,
        "turbo_lora": DEFAULT_TURBO_LORA,
        "policy": {
            "no_submit_by_default": True,
            "baseline_resolution": "1088x1920",
            "delivery_crop": "1080x1920",
            "first_pass_clip_count": len(clips),
        },
        "variants": [],
        "manual_variants": MANUAL_VARIANTS,
        "warnings": [],
    }

    defaults = sequence.get("defaults") if isinstance(sequence.get("defaults"), dict) else {}
    for clip_index, raw_clip in enumerate(clips, start=1):
        clip = merged_clip_defaults(sequence, raw_clip)
        clip_id = slug(str(clip.get("id") or f"clip-{clip_index:02d}"))
        prompt_path = pack_dir / "prompts" / f"{clip_id}.md"
        prompt_path, warnings = read_clip_prompt(clip, sequence_dir, prompt_path)
        manifest["warnings"].extend(warnings)
        if clip.get("use_previous_last_frame_as_ref"):
            manifest["warnings"].append(
                f"{clip_id} uses previous last frame in production; this pack keeps the listed refs only. "
                "Run clip 01 first before doing continuity-chain tests."
            )

        ref_images = [resolve_path(str(item), sequence_dir) for item in (clip.get("ref_images") or [])]
        missing_refs = [str(path) for path in ref_images if not path.exists()]
        if missing_refs:
            manifest["warnings"].append(f"{clip_id} missing ref image(s): " + "; ".join(missing_refs))

        for variant in COMMAND_VARIANTS:
            variant_dir = pack_dir / "runs" / variant.variant_id / clip_id
            api_json = variant_dir / "api_graph.json"
            output_dir = variant_dir / "outputs"
            build_cmd = command_for_clip(
                python_exe=args.python,
                workspace_root=WORKSPACE_ROOT,
                server=server,
                variant=variant,
                clip=clip,
                clip_id=clip_id,
                prompt_path=prompt_path,
                api_json_path=api_json,
                output_dir=output_dir,
                sequence_dir=sequence_dir,
                submit=False,
            )
            submit_cmd = command_for_clip(
                python_exe=args.python,
                workspace_root=WORKSPACE_ROOT,
                server=server,
                variant=variant,
                clip=clip,
                clip_id=clip_id,
                prompt_path=prompt_path,
                api_json_path=api_json,
                output_dir=output_dir,
                sequence_dir=sequence_dir,
                submit=True,
            )
            build_commands.append(ps_join(build_cmd))
            build_commands.append("")
            submit_commands.append(ps_join(submit_cmd))
            submit_commands.append("")
            manifest["variants"].append(
                {
                    "variant_id": variant.variant_id,
                    "title": variant.title,
                    "clip_id": clip_id,
                    "runner": variant.runner,
                    "prompt_file": str(prompt_path),
                    "api_json": str(api_json),
                    "output_dir": str(output_dir),
                    "build_command": build_cmd,
                    "submit_command_disabled": submit_cmd,
                    "objective": variant.objective,
                    "caveat": variant.caveat,
                    "inherits_defaults": defaults,
                    "clip": {
                        "mode": clip.get("mode", "r2v"),
                        "width": clip.get("width", 1088),
                        "height": clip.get("height", 1920),
                        "duration": clip.get("duration", 5.0),
                        "steps": clip.get("steps", 8),
                        "seed": clip.get("seed"),
                        "ref_images": [str(path) for path in ref_images],
                    },
                }
            )

    pack_dir.mkdir(parents=True, exist_ok=True)
    (pack_dir / "experiment_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    write_lines(pack_dir / "commands.build_api_json.ps1", build_commands)
    write_lines(pack_dir / "commands.submit_real_runs.ps1.disabled", submit_commands)
    (pack_dir / "README_CLAUDE_HANDOFF.md").write_text(render_static_plan(), encoding="utf-8", newline="\n")
    return pack_dir


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare a no-submit H3 refine experiment handoff pack.")
    parser.add_argument("--sequence", required=True, help="Existing H3 sequence JSON or viral-rewrite h3-package/sequence.json")
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT), help="Directory for the generated handoff pack")
    parser.add_argument("--experiment-id", default=None, help="Stable pack folder name; defaults to sequence id + timestamp")
    parser.add_argument("--server", default=None, help="Override the sequence server URL")
    parser.add_argument("--python", default="python", help="Python executable written into generated command files")
    parser.add_argument("--clip-count", type=int, default=1, help="Number of clips to include when --all-clips is not used")
    parser.add_argument("--all-clips", action="store_true", help="Include every clip from the sequence")
    args = parser.parse_args()

    if args.clip_count < 1:
        raise SystemExit("--clip-count must be at least 1")
    try:
        pack_dir = build_pack(args)
    except PackError as exc:
        raise SystemExit(f"ERROR: {exc}") from exc
    print(f"H3 refine experiment handoff pack written: {pack_dir}")
    print("No ComfyUI job was submitted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
