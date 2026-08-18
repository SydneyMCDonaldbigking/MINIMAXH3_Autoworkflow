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


def _clip_product_picture_index(refs: list[Path], *, carried_frame: bool) -> int:
    return (2 if carried_frame else 1) + len(refs) - 1


def _reference_transfer_scope(ref: Path) -> tuple[str, str]:
    name = ref.stem.lower()
    if any(token in name for token in ("glass", "ice", "pour", "stream", "liquid", "splash", "texture")):
        return (
            "the tumbler or vessel shape, ice placement, liquid stream geometry, splash timing, and glass refraction",
            "the source product identity, brand text, label design, background colour, darker liquid colour, fruit props, and framing crop",
        )
    if any(token in name for token in ("table", "surface", "background", "backdrop", "board", "riser", "scene", "set")):
        return (
            "the tabletop colour, support-surface material, horizon line, light direction, shadow softness, and clean studio spacing",
            "any products, labels, overlay text, fruit props, signage, platform UI, and camera framing that conflicts with the target clip",
        )
    if any(token in name for token in ("hand", "grip", "hold", "person", "character", "model")):
        return (
            "the hand pose, grip height, entry direction, human scale, and the relationship between hand and product",
            "the person's identity, face, clothing, background, product brand, label text, and any unrelated props",
        )
    if any(token in name for token in ("final", "hero", "packshot", "cta", "end")):
        return (
            "the final composition spacing, product-to-prop relationship, stable endpoint pose, and clean negative space",
            "the source brand, source product identity, source flavour story, overlay text, logo card, price, and CTA UI",
        )
    return (
        "the composition geometry, physical action state, scale relationship, light direction, and material surface relationship",
        "the source product identity, brand, label text, overlay text, unrelated props, background colour, and any product-specific claim",
    )


def _ingredient_grounding(plan: RewritePlan, request: RewriteRequest) -> str:
    raw_items = [
        *getattr(plan.prompt_package, "must_keep", []),
        *plan.rewrite_strategy.keep_from_source,
        request.product_context,
    ]
    blocked = ("字幕", "文字", "ui", "price", "tag", "identity", "包装", "label", "shape")
    candidates: list[str] = []
    for item in raw_items:
        text = re.sub(r"\s+", " ", str(item).strip())
        if not text or any(token in text.lower() for token in blocked):
            continue
        candidates.append(text.rstrip("。.;"))
        if len(candidates) >= 3:
            break
    if candidates:
        return (
            "Ground the base with the product's own visible ingredient/material cues from the source image: "
            + "; ".join(candidates)
            + ". These cues sit low on the surface as product grounding, not extra flavours or a new product story."
        )
    return (
        "Ground the base with the product's own visible ingredient or material cue from the source image. "
        "If no separate ingredient is visible, keep the surface bare except for one neutral material cue already implied by the product."
    )


def _frame_inventory(plan: RewritePlan, request: RewriteRequest, product_ref: str) -> str:
    return (
        f"Everything in frame across all three shots: one hero product from {product_ref}, one stable support surface, "
        f"one clean background, one adult hand when needed, one proof vessel/use object when called for, "
        f"and the product's own ingredient/material grounding. The same object positions continue shot to shot; unlisted areas stay bare. "
    )


def _split_action_chunks(items: list[str]) -> list[str]:
    chunks: list[str] = []
    for item in items:
        text = re.sub(r"\s+", " ", item.strip())
        if not text:
            continue
        parts = [part.strip(" ,.;，。；") for part in re.split(r"[。；;，]+", text) if part.strip(" ,.;，。；")]
        chunks.extend(parts or [text])
    return chunks


CAMERA_BEAT_TOKENS = (
    "镜头", "推近", "拉远", "特写", "俯拍", "仰拍", "平视", "近景", "中景", "远景",
    "微距", "构图", "景别", "拍摄", "camera", "push", "pull", "close-up",
    "macro", "tilt", "pan", "dolly", "rack focus", "framing", "composition",
)

ACTION_BEAT_TOKENS = (
    "手", "倒", "倒入", "倾倒", "注入", "放", "切", "拿", "握", "拧", "打开",
    "开启", "举", "夹", "滴", "淋", "撒", "滚落", "落", "进入", "退出", "摆",
    "旋转", "端", "饮用", "喝", "吞咽", "pour", "place", "drop", "lift",
    "hold", "cut", "grab", "twist", "open", "set", "rotate", "enter", "exit",
)

RESULT_BEAT_TOKENS = (
    "状态", "结果", "呈现", "显示", "保持", "可见", "收尾", "定格", "质感",
    "液体", "水珠", "冰块", "果肉", "冷凝", "通透", "光泽", "成品", "悬浮",
    "完成", "final", "result", "visible", "texture", "state", "finish", "endpoint",
)


def _contains_any(text: str, tokens: tuple[str, ...]) -> bool:
    lower = text.lower()
    return any(token.lower() in lower for token in tokens)


def _clip_shot_beats(group: list[str]) -> dict[str, str]:
    chunks = _split_action_chunks(group)
    action: list[str] = []
    camera: list[str] = []
    result: list[str] = []
    detail: list[str] = []
    for chunk in chunks:
        has_action = _contains_any(chunk, ACTION_BEAT_TOKENS)
        has_result = _contains_any(chunk, RESULT_BEAT_TOKENS)
        has_camera = _contains_any(chunk, CAMERA_BEAT_TOKENS)
        if has_action:
            action.append(chunk)
        elif has_result:
            result.append(chunk)
        elif has_camera:
            camera.append(chunk)
        else:
            detail.append(chunk)
    setup = action[0] if action else (detail[0] if detail else "")
    hand_action = action[1] if len(action) > 1 else ""
    result_beat = result[0] if result else (action[-1] if len(action) > 1 else (detail[-1] if detail else ""))
    return {
        "setup": _condense([setup], limit=260) if setup else "",
        "hand_action": _condense([hand_action], limit=260) if hand_action else "",
        "camera": _condense(camera[:1], limit=260) if camera else "",
        "result": _condense([result_beat], limit=320) if result_beat else "",
    }


def _model_facing_constraints(items: list[str]) -> str:
    blocked = (
        "模板", "viral", "VIRAL", "用户", "agent", "Agent", "自动", "默认",
        "除非", "口播", "字幕逻辑", "总时长", "三段5秒", "product category",
        "main value", "brand", "shopping",
    )
    constraints: list[str] = []
    seen: set[str] = set()
    for item in items:
        for part in re.split(r"[；;]\s*", str(item)):
            text = re.sub(r"\s+", " ", part.strip())
            if not text or any(token in text for token in blocked):
                continue
            key = text.lower()
            if key not in seen:
                seen.add(key)
                constraints.append(text)
            if len(constraints) >= 4:
                return "; ".join(constraints)
    return "; ".join(constraints)


def _model_facing_preserve(items: list[str], fallback: str) -> str:
    blocked = (
        "模板", "viral", "VIRAL", "用户", "agent", "Agent", "字幕", "文字", "UI",
        "ui", "输出", "最终", "总时长", "三段", "source", "不能", "不得", "不要",
        "无人物", "无手部", "口播", "默认", "除非",
    )
    keep: list[str] = []
    seen: set[str] = set()
    for item in items:
        for part in re.split(r"[；;]\s*", str(item)):
            text = re.sub(r"\s+", " ", part.strip())
            if not text or any(token in text for token in blocked):
                continue
            key = text.lower()
            if key not in seen:
                seen.add(key)
                keep.append(text)
            if len(keep) >= 6:
                return "; ".join(keep)
    return "; ".join(keep) or fallback


def _camera_sentence(camera_beat: str, fallback: str) -> str:
    if not camera_beat:
        return fallback
    return (
        f"Camera/framing follows this beat: {camera_beat}. "
        "Treat it as the only camera or framing instruction for this shot; add no extra pan, tilt, rack focus, or drift."
    )


def _h3_shots_for_clip(
    *,
    clip_index: int,
    product_ref: str,
    product: str,
    role: str,
    shot_beats: dict[str, str],
) -> tuple[str, str, str]:
    setup_beat = shot_beats.get("setup", "")
    hand_beat = shot_beats.get("hand_action", "")
    camera_beat = shot_beats.get("camera", "")
    result_beat = shot_beats.get("result", "")
    if clip_index == 1:
        setup_sentence = f"The action translates this template beat into one physical movement: {setup_beat}. " if setup_beat else ""
        shot_1 = (
            f"[Shot 1] Medium vertical commercial shot, 50mm feel. Establish {product} through the {role} beat. "
            f"The single hero product from {product_ref} begins just outside the left edge in one adult hand, held upright around its lower third or label side. "
            "The hand carries that same product into the centre of the stable support surface, sets it down squarely on the landing spot, and withdraws to the left out of frame. "
            f"{setup_sentence}"
            + _camera_sentence(camera_beat, "The camera performs one continuous slow push-in of about 4 cm across the whole shot, never pausing and never reversing.")
            + " "
            "The shot ends with the product standing alone, front-readable, on the surface."
        )
        detail_sentence = f"The concrete product-detail result for this shot is: {result_beat}. " if result_beat else ""
        shot_2 = (
            "[Shot 2] At 00:01.600, cut to a medium close-up product angle. "
            f"The same product remains on the same landing spot from shot 1, and the same hand re-enters from the lower right only to rotate the product a few degrees toward camera. "
            f"{detail_sentence}"
            "The support surface, background, and any low ingredient/material grounding do not move. "
            "The hand exits along the same lower-right path after the front face is readable, leaving the product upright and centred. "
            "The camera is locked-off with shallow focus; the proof action is the controlled reveal of the exact source-product identity, not a new object or a second SKU. "
            "The shot ends with the hand gone and the product still in the same physical place."
        )
        shot_3 = (
            "[Shot 3] At 00:03.400, cut to the endpoint composition for this five-second clip. "
            f"The same product from {product_ref} has not changed identity or position; it stands on the support surface as the packshot anchor. "
            "One proof vessel or small material cue sits low and secondary beside it only if it was already introduced in shot 2. "
            f"{detail_sentence}"
            "The upper frame stays clean for later editing, while the product front, silhouette, colour, and material remain readable. "
            "The camera does not move and the focus does not rack. "
            "The shot ends in a stable product-visible handoff frame for clip 02."
        )
        return shot_1, shot_2, shot_3

    if clip_index == 2:
        setup_sentence = f"The concrete setup beat is: {setup_beat}. " if setup_beat else ""
        shot_1 = (
            f"[Shot 1] Medium-close vertical product-proof setup, 50mm to 70mm feel. The single product from {product_ref} starts standing on the support surface behind the proof vessel and stays there for this whole shot. "
            "One adult hand or tool enters from the upper right and performs the setup movement at the vessel. "
            f"{setup_sentence}"
            "The product remains visible as the background anchor, the surface grounding remains low and still, and no second product appears in the foreground. "
            "Camera locked-off, no pan. The shot ends with the product still standing behind the vessel and the proof vessel ready for action."
        )
        hand_sentence = (
            f"The hand performs exactly this proof action, start to finish: {hand_beat}. "
            if hand_beat
            else "The hand performs one simple product-proof action that completes the setup, start to finish. "
        )
        shot_2 = (
            "[Shot 2] At 00:01.600, cut to a tight close-up action insert. "
            f"That same product has now been lifted off the support surface by one adult hand and enters from the upper right, so the surface behind the vessel is physically empty where it stood in shot 1. "
            f"{hand_sentence}"
            "The motion is directed down toward the vessel or use object. "
            "The product label or defining front area flashes briefly so the viewer knows this is the same source product. "
            + _camera_sentence(camera_beat, "Camera locked, shallow focus, no drift.")
            + " The shot ends with the action completed and the product still in that same hand."
        )
        result_sentence = f"The vessel now shows this completed material result: {result_beat}. " if result_beat else "The vessel now shows the completed material result from shot 2. "
        shot_3 = (
            "[Shot 3] At 00:03.400, cut to the result state. "
            f"The one product from {product_ref} has been set back down on the same support surface behind or beside the proof vessel, restoring the single-product layout from shot 1. "
            f"{result_sentence}"
            "The grounding ingredient/material cue stays low around the base and does not become a new flavour, label, or product. "
            "The camera does not move and the focus settles on the result plus product. "
            "The shot ends with a clean product-visible handoff frame for clip 03."
        )
        return shot_1, shot_2, shot_3

    setup_sentence = f"The concrete preparation beat is: {setup_beat}. " if setup_beat else ""
    shot_1 = (
        f"[Shot 1] Tight vertical close-up, 70mm product-detail feel. The single hero product from {product_ref} begins in one adult hand near the centre-right of frame, already lifted from the support surface. "
        "The hand grips the product at a natural use point, performs the final-use preparation, and keeps the front identity partly readable. "
        f"{setup_sentence}"
        "The support surface below remains clean, with only the product's own grounding cue and the proof vessel waiting in its fixed position. "
        "Camera locked-off, shallow focus. The shot ends with the product still in hand, ready to create the final result."
    )
    hand_sentence = (
        f"One continuous physical action completes this final material action: {hand_beat}. "
        if hand_beat
        else "One continuous physical action completes the final material result. "
    )
    shot_2 = (
        "[Shot 2] At 00:01.600, cut to a low close-up action insert. "
        f"The same product moves from the hand position in shot 1 into the upper-right action angle, aimed toward the same proof vessel or use object already waiting on the surface. "
        f"{hand_sentence}"
        "There is no extra handoff and no second product. "
        "The surface point where the product will later stand is visible and empty during the action, making the single-object movement clear. "
        + _camera_sentence(camera_beat, "Camera locked, one action only.")
        + " The shot ends with the final result visible in the vessel or use area."
    )
    result_sentence = f"The concrete final memory beat is: {result_beat}. " if result_beat else ""
    shot_3 = (
        "[Shot 3] At 00:03.400, cut to the final hero packshot. "
        f"The same product from {product_ref} has been placed back onto the support surface next to the completed proof result. "
        "Its front identity faces camera, the result object sits beside it, and the grounding ingredient/material cue remains low at the base. "
        f"{result_sentence}"
        "The upper frame stays clean for later editing text, but no text is generated. "
        "The camera does not move, the focus does not rack, and the product remains visible until the final frame. "
        "The shot ends as a stable product-memory frame, not a fade or empty scene."
    )
    return shot_1, shot_2, shot_3


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
            transfers, rejects = _reference_transfer_scope(ref)
            declarations.append(
                f"<Picture {idx}> is a supporting H3 reference image: {ref.name}. "
                f"Transfer only {transfers}. Do not transfer {rejects}."
            )
            retention.append(
                f"<Picture {idx}>: attribute_transfer. Transfer only {transfers}. Do not transfer {rejects}."
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
    product = request.product_context or "the source product"
    must_keep = _model_facing_preserve(plan.rewrite_strategy.keep_from_source, product)
    borrow = "; ".join(item for item in plan.rewrite_strategy.borrow_from_viral if item.strip()) or "the template's hook, pacing, camera rhythm, and satisfaction structure"
    model_constraints = _model_facing_constraints(plan.rewrite_strategy.risk_controls)
    shot_beats = _clip_shot_beats(group)
    product_ref = f"<Picture {_clip_product_picture_index(refs, carried_frame=carried)}>"
    shot_1, shot_2, shot_3 = _h3_shots_for_clip(
        clip_index=clip_index,
        product_ref=product_ref,
        product=product,
        role=role,
        shot_beats=shot_beats,
    )
    frame_inventory = _frame_inventory(plan, request, product_ref)
    ingredient_grounding = _ingredient_grounding(plan, request)
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

{frame_inventory}

{ingredient_grounding}

Preserve across all shots: {must_keep}. Avoid template product leakage, fake labels, invented text, subtitles, price tags, shopping UI, watermarks, extra fingers, warped hands, camera shake, scene jumps, and product identity drift. {model_constraints}

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
