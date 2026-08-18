#!/usr/bin/env python3
"""MiniMax H3 runtime bridge for the creative rewrite skill."""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any
from urllib import error, request as urlrequest

from schemas import RewritePlan, RewriteRequest


DEFAULT_SERVER = "http://127.0.0.1:8189"
DEFAULT_WIDTH = 1088
DEFAULT_HEIGHT = 1920
DEFAULT_DURATION = 5.0
DEFAULT_STEPS = 8
MAX_REF_IMAGES_WITH_CARRY = 8


class H3RuntimeError(RuntimeError):
    pass


def _slug(value: str, fallback: str = "viral-rewrite") -> str:
    text = value.strip().lower()
    text = re.sub(r"[^a-z0-9._-]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text[:80] or fallback


def _is_url(value: str) -> bool:
    return value.startswith("http://") or value.startswith("https://")


def workflow_root() -> Path:
    configured = os.getenv("H3_WORKFLOW_ROOT", "").strip()
    if configured:
        return Path(configured).expanduser().resolve()
    skill_root = Path(__file__).resolve().parent.parent
    for candidate in [skill_root, *skill_root.parents]:
        if (candidate / "h3_sequence_runner.py").exists() and (candidate / "h3_runner.py").exists():
            return candidate.resolve()
    return skill_root.parent.parent.resolve()


def h3_output_root(root: Path | None = None) -> Path:
    root = root or workflow_root()
    configured = os.getenv("H3_OUTPUT_ROOT", "").strip()
    if configured:
        path = Path(configured).expanduser()
        return path.resolve() if path.is_absolute() else (root / path).resolve()
    return (root / "sequence_outputs").resolve()


def h3_server(request: RewriteRequest | None = None) -> str:
    value = ""
    if request is not None:
        value = getattr(request, "h3_server", "") or ""
    return value.strip() or os.getenv("H3_COMFYUI_SERVER", "").strip() or DEFAULT_SERVER


def h3_dry_run_enabled(request: RewriteRequest | None = None) -> bool:
    value = os.getenv("H3_DRY_RUN", "").strip().lower()
    if value in {"1", "true", "yes", "y", "on"}:
        return True
    return bool(getattr(request, "h3_dry_run", False)) if request is not None else False


def _resolve_local_path(value: str, *, base_dirs: list[Path]) -> Path:
    if not value:
        raise H3RuntimeError("empty media path")
    if _is_url(value):
        raise H3RuntimeError(f"MiniMax H3 local ComfyUI generation needs a local image file, not a URL: {value}")
    raw = Path(value).expanduser()
    candidates = [raw] if raw.is_absolute() else [base / raw for base in base_dirs]
    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()
    raise H3RuntimeError(f"local media file not found: {value}")


def _reference_images(request: RewriteRequest, root: Path) -> list[Path]:
    skill_root = Path(__file__).resolve().parent.parent
    base_dirs = [Path.cwd(), root, skill_root]
    refs: list[Path] = []
    for item in getattr(request, "h3_reference_images", []) or []:
        refs.append(_resolve_local_path(str(item), base_dirs=base_dirs))
    if not request.source_image:
        raise H3RuntimeError("source_image is required for MiniMax H3 generation")
    refs.append(_resolve_local_path(str(request.source_image), base_dirs=base_dirs))
    deduped: list[Path] = []
    seen: set[str] = set()
    for ref in refs:
        key = str(ref).lower()
        if key not in seen:
            seen.add(key)
            deduped.append(ref)
    if len(deduped) > MAX_REF_IMAGES_WITH_CARRY:
        raise H3RuntimeError(
            f"MiniMax H3 uses the previous clip last frame as a continuity reference, so this skill allows at most "
            f"{MAX_REF_IMAGES_WITH_CARRY} local reference images including the product image. Got {len(deduped)}."
        )
    return deduped


def _server_reachable(server: str, timeout: float = 3.0) -> bool:
    try:
        with urlrequest.urlopen(server.rstrip("/") + "/queue", timeout=timeout) as response:
            return 200 <= response.status < 500
    except (error.URLError, TimeoutError, OSError):
        return False


def h3_preflight_issues(request: RewriteRequest, plan: RewritePlan | None = None, *, check_server: bool = True) -> list[str]:
    issues: list[str] = []
    root = workflow_root()
    if not (root / "h3_sequence_runner.py").exists():
        issues.append(f"h3_sequence_runner.py not found under H3_WORKFLOW_ROOT/workflow root: {root}")
    if not (root / "h3_runner.py").exists():
        issues.append(f"h3_runner.py not found under H3_WORKFLOW_ROOT/workflow root: {root}")
    try:
        _reference_images(request, root)
    except H3RuntimeError as exc:
        issues.append(str(exc))
    if check_server and not h3_dry_run_enabled(request):
        server = h3_server(request)
        if not _server_reachable(server):
            issues.append(
                f"ComfyUI MiniMax H3 server is not reachable at {server}. Start ComfyUI or open the SSH tunnel before confirmed generation."
            )
    return issues


def h3_preflight_blocking_message(request: RewriteRequest, plan: RewritePlan | None = None, *, language: str = "zh") -> str:
    issues = h3_preflight_issues(request, plan, check_server=True)
    if not issues:
        return ""
    if language == "en":
        lines = ["Generation is blocked before MiniMax H3 submission:"]
        lines.extend(f"- {issue}" for issue in issues)
        lines.append("The prepared brief is reusable; fix the H3 runtime/server issue and confirm generation again.")
        return "\n".join(lines)
    lines = ["已在提交 MiniMax H3 前阻断："]
    lines.extend(f"- {issue}" for issue in issues)
    lines.append("当前 prepared brief 可以复用；修好 H3 运行环境或 ComfyUI server 后再确认生成。")
    return "\n".join(lines)


def _storyboard_groups(plan: RewritePlan) -> list[list[str]]:
    shots = [shot.visual_instruction.strip() for shot in plan.rewritten_storyboard.shots if shot.visual_instruction.strip()]
    if not shots:
        shots = [
            "Establish the source product in the template's opening hook structure.",
            "Show one close product proof or texture action.",
            "End on a product-visible use or CTA moment.",
        ]
    groups: list[list[str]] = []
    total = len(shots)
    for index in range(3):
        start = round(index * total / 3)
        end = round((index + 1) * total / 3)
        group = shots[start:end] or [shots[min(index, total - 1)]]
        groups.append(group)
    return groups


def _clip_role(index: int) -> str:
    return ["opening hook and product identity", "proof, texture, or usage transformation", "satisfaction close and visual CTA"][index - 1]


def _condense(items: list[str], limit: int = 560) -> str:
    text = " ".join(item.replace("\n", " ").strip() for item in items if item.strip())
    text = re.sub(r"\s+", " ", text)
    if len(text) > limit:
        return text[: limit - 1].rstrip() + "."
    return text


def _reference_declarations(refs: list[Path], *, carried_frame: bool) -> tuple[str, str]:
    declarations: list[str] = []
    retention: list[str] = []
    offset = 1
    if carried_frame:
        declarations.append("<Picture 1> is the final frame of the previous MiniMax H3 clip, used as the continuity anchor.")
        retention.append("<Picture 1>: fully_preserved. Continue the same product, scene, lighting, and physical state without a jump.")
        offset = 2
    for idx, ref in enumerate(refs, start=offset):
        if idx == offset + len(refs) - 1:
            declarations.append(f"<Picture {idx}> is the source product image and product identity truth: {ref.name}.")
            retention.append(
                f"<Picture {idx}>: fully_preserved. Preserve the product type, shape, packaging, color, label placement, material, and visible design details."
            )
        else:
            declarations.append(f"<Picture {idx}> is a supporting H3 reference image for scene, character, hand, action, or product-state continuity: {ref.name}.")
            retention.append(
                f"<Picture {idx}>: attribute_transfer. Use only the relevant scene, character, action-state, lighting, or material attributes; do not invent text."
            )
    return "\n".join(declarations), "\n".join(retention)


def _h3_prompt_for_clip(
    *,
    clip_index: int,
    plan: RewritePlan,
    request: RewriteRequest,
    refs: list[Path],
) -> str:
    carried = clip_index > 1
    declarations, retention = _reference_declarations(refs, carried_frame=carried)
    groups = _storyboard_groups(plan)
    group = groups[clip_index - 1]
    role = _clip_role(clip_index)
    strategy = plan.rewrite_strategy.strategy_summary
    must_keep = "; ".join(item for item in plan.rewrite_strategy.keep_from_source if item.strip()) or request.product_context or "the source product identity"
    borrow = "; ".join(item for item in plan.rewrite_strategy.borrow_from_viral if item.strip()) or "the template's hook, pacing, camera rhythm, and satisfaction structure"
    risks = "; ".join(item for item in plan.rewrite_strategy.risk_controls if item.strip())
    base_action = _condense(group)
    product = request.product_context or "the source product"
    shot_1 = (
        f"[Shot 1] Medium vertical commercial shot, 50mm feel. Establish {product} through the {role} beat. "
        f"Start with the reference product readable, the scene stable, and the template function visible. {base_action} "
        "The camera is locked-off or performs one slow push-in of about 4 cm, never both."
    )
    shot_2 = (
        "[Shot 2] At 00:01.600, cut to a medium close-up or close food/product angle. "
        "Show one physical proof action only: a pour, lift, texture reveal, hand placement, use motion, or product-state change that completes inside this shot. "
        "Keep the product identity from the source image sharp and consistent. The camera does not drift."
    )
    shot_3 = (
        "[Shot 3] At 00:03.400, cut to the endpoint composition for this five-second clip. "
        "Finish with a clean product-visible handoff: the product, its result, or its use state lands in a readable final composition. "
        "The camera does not move and the focus does not rack."
    )
    return f"""subject_definitions:
{declarations}

summary:
reference generation. A five-second vertical MiniMax H3 commercial clip, clip {clip_index:02d} of a three-clip sequence. This clip handles {role}. Keep the source product identity from the product image, while borrowing only the template's creative structure: {borrow}. The confirmed rewrite strategy is: {strategy}

retention_analysis:
{retention}

detailed_description:
{shot_1}

{shot_2}

{shot_3}

Preserve across all shots: {must_keep}. Avoid template product leakage, fake labels, invented text, subtitles, price tags, shopping UI, watermarks, extra fingers, warped hands, camera shake, scene jumps, and product identity drift. {risks}

overall_soundscape:
Silent delivery is expected, but describe physical commercial sound for motion guidance: clean product handling, soft ambience, texture sounds, and a clear impact at the endpoint of each action.

non_diegetic_music:
No exported music by default. Use the imagined score only to guide pacing: original, non-identifiable, no vocals, no lyrics, no recognizable melody, lifting gently across the action and resolving at the final clip.
"""


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def prepare_h3_sequence_package(request: RewriteRequest, plan: RewritePlan) -> dict[str, Any]:
    root = workflow_root()
    refs = _reference_images(request, root)
    sequence_id = _slug(getattr(request, "h3_sequence_id", "") or request.product_context or "viral-rewrite-h3")
    run_id = _slug(getattr(request, "h3_run_id", "") or dt.datetime.now().strftime("%Y%m%d_%H%M%S"), fallback="run")
    package_dir = h3_output_root(root) / sequence_id / run_id / "h3-package"
    prompt_dir = package_dir / "prompts"
    prompt_dir.mkdir(parents=True, exist_ok=True)
    prompt_files: list[Path] = []
    for clip_index in range(1, 4):
        path = prompt_dir / f"clip-{clip_index:02d}_ref2va.md"
        path.write_text(
            _h3_prompt_for_clip(clip_index=clip_index, plan=plan, request=request, refs=refs),
            encoding="utf-8",
            newline="\n",
        )
        prompt_files.append(path)

    clip_specs = []
    for clip_index, prompt_file in enumerate(prompt_files, start=1):
        spec: dict[str, Any] = {
            "id": f"clip-{clip_index:02d}-{_slug(_clip_role(clip_index), fallback='clip')}",
            "prompt_file": str(prompt_file),
            "ref_images": [str(ref) for ref in refs],
            "seed": int(getattr(request, "h3_seed_base", 26081800)) + clip_index,
            "prefix": f"sequence/{sequence_id}/{run_id}/clip-{clip_index:02d}",
        }
        if clip_index > 1:
            spec["use_previous_last_frame_as_ref"] = True
        clip_specs.append(spec)

    sequence = {
        "sequence_id": sequence_id,
        "server": h3_server(request),
        "defaults": {
            "mode": "r2v",
            "width": DEFAULT_WIDTH,
            "height": DEFAULT_HEIGHT,
            "duration": DEFAULT_DURATION,
            "steps": DEFAULT_STEPS,
            "turbo": True,
            "turbo_low_vram": True,
            "no_audio": True,
            "ref_image_size": "match",
            "poll": 10,
            "timeout": 10800,
        },
        "clips": clip_specs,
        "final": {
            "filename": f"{sequence_id}_{run_id}_1080x1920.mp4",
            "concat_mode": "both",
            "crop": {"width": 1080, "height": 1920, "x": 4, "y": 0},
            "crf": 16,
            "preset": "medium",
            "keep_audio": False,
        },
    }
    sequence_path = package_dir / "sequence.json"
    _write_json(sequence_path, sequence)
    return {
        "workflow_root": str(root),
        "sequence_id": sequence_id,
        "run_id": run_id,
        "package_dir": str(package_dir),
        "sequence_path": str(sequence_path),
        "prompt_files": [str(path) for path in prompt_files],
        "ref_images": [str(path) for path in refs],
    }


def _run_streamed(command: list[str], *, cwd: Path, log_path: Path) -> tuple[int, str]:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    output_lines: list[str] = []
    with subprocess.Popen(
        command,
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    ) as process:
        assert process.stdout is not None
        with log_path.open("w", encoding="utf-8", newline="\n") as log:
            for line in process.stdout:
                print(line, end="", flush=True)
                log.write(line)
                output_lines.append(line)
            return process.wait(), "".join(output_lines)


def run_h3_sequence(request: RewriteRequest, plan: RewritePlan) -> dict[str, Any]:
    issues = h3_preflight_issues(request, plan, check_server=not h3_dry_run_enabled(request))
    if issues:
        raise H3RuntimeError("\n".join(issues))

    package = prepare_h3_sequence_package(request, plan)
    root = Path(package["workflow_root"])
    output_root = h3_output_root(root)
    command = [
        sys.executable,
        str(root / "h3_sequence_runner.py"),
        "run",
        "--sequence",
        package["sequence_path"],
        "--server",
        h3_server(request),
        "--output-root",
        str(output_root),
        "--run-id",
        package["run_id"],
    ]
    if getattr(request, "h3_no_concat", True):
        command.append("--no-concat")
    if h3_dry_run_enabled(request):
        command.append("--dry-run")

    started = time.time()
    log_path = Path(package["package_dir"]) / "h3_sequence_runner.log"
    code, output = _run_streamed(command, cwd=root, log_path=log_path)
    if code != 0:
        raise H3RuntimeError(f"h3_sequence_runner.py failed with exit code {code}. See {log_path}")

    manifest_path = output_root / package["sequence_id"] / package["run_id"] / "sequence-manifest.json"
    manifest: dict[str, Any] = {}
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    clip_paths = [
        str(Path(item["video"]).resolve())
        for item in manifest.get("clips", [])
        if isinstance(item, dict) and item.get("video") and Path(str(item["video"])).exists()
    ]
    final_video = manifest.get("final_video")
    local_video = str(Path(final_video).resolve()) if final_video and Path(str(final_video)).exists() else (clip_paths[0] if clip_paths else "")
    return {
        **package,
        "server": h3_server(request),
        "dry_run": h3_dry_run_enabled(request),
        "seconds": round(time.time() - started, 2),
        "command": command,
        "runner_log_path": str(log_path),
        "manifest_path": str(manifest_path),
        "manifest": manifest,
        "clip_paths": clip_paths,
        "final_video_path": str(Path(final_video).resolve()) if final_video else "",
        "local_video_path": local_video,
        "stdout_tail": output[-4000:],
    }
