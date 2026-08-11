#!/usr/bin/env python3
"""
Experimental MiniMax H3 runner with sigma shift and attention acceleration.

Separate from h3_runner.py on purpose. That one produces the ads and must keep
working; this one exists to answer the questions in
EXPERIMENT_PLAN_ACCELERATION.md and will change shape as they get answered.

Two things this adds to the graph, neither of which the production runner has:

  sigma shift        A sampling-schedule node between the model and the guider.
                     Our own ComfyUI log says the Turbo sampler fell back with
                     "legacy dual-schedule (no native ModelSamplingAV)", so the
                     schedule we have been sampling on is the fallback one.
  acceleration       JR_H3_UnifiedAcceleration from
                     Goldlionren/ComfyUI_JR_MiniMaxH3Node, a MODEL->MODEL patch
                     chaining Sage attention, chunked attention, chunked FFN and
                     Sol-Attn.

Both are opt-in and both are discovered at runtime. The server is asked what it
actually has via /object_info, so a missing node produces a clear message
instead of a graph that fails deep inside execution. --probe reports what is
installed and exits.

Acceleration changes numerics. The same seed will NOT reproduce a pixel-identical
clip, so compare perceptually and with check_clip_quality.py, never by pixel diff.

Examples:
  python h3_accel_runner.py --probe
  python h3_accel_runner.py r2v --prompt-file p.md --ref-image a.png --sigma-shift 3.0
  python h3_accel_runner.py r2v --prompt-file p.md --ref-image a.png --accel
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from typing import Any

import h3_runner as base

# Candidate class names, most specific first. ComfyUI renames things between
# releases and the H3 nodes are young, so ask the server rather than assume.
SIGMA_SHIFT_CANDIDATES = [
    "ModelSamplingAV",
    "MiniMaxH3SigmaShift",
    "ModelSamplingSD3",
    "ModelSamplingAuraFlow",
]
ACCEL_CANDIDATES = ["JR_H3_UnifiedAcceleration"]

# Defaults lifted from the node's own INPUT_TYPES so a bare --accel reproduces
# what its author ships, rather than some combination we invented.
ACCEL_DEFAULTS: dict[str, Any] = {
    "enable": True,
    "sage_attention": "sageattn_qk_int8_pv_fp8_cuda++",
    "allow_compile": False,
    "enable_low_vram_attention": True,
    "head_chunks": 4,
    "enable_low_vram_ffn": True,
    "ffn_chunks": 4,
    "ffn_seq_threshold": 4096,
    "enable_sol_attn": True,
    "tau": 1.3,
    "start_percent": 0.2,
    "end_percent": 0.9,
    "min_tokens": 4096,
    "int8_qk": True,
    "int8_pv": True,
    "sink_conditioning": "exact_kv_and_rows",
    "morton": False,
    "morton_curve": "2d_frame",
    "verbose": True,
    "use_tma": False,
    "dense_blocks": "",
}


def fetch_object_info(server: str) -> dict[str, Any]:
    url = base.api_url(server, "/object_info")
    try:
        with urllib.request.urlopen(url, timeout=120) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        raise base.ComfyError(f"could not read {url}: {exc}") from exc


def pick(available: dict[str, Any], candidates: list[str]) -> str | None:
    for name in candidates:
        if name in available:
            return name
    return None


def describe(available: dict[str, Any], name: str) -> str:
    """One line of a node's required inputs, so a signature change is visible."""
    spec = available.get(name, {})
    required = (spec.get("input", {}) or {}).get("required", {}) or {}
    return ", ".join(required.keys())


def probe(server: str) -> int:
    available = fetch_object_info(server)
    print(f"server: {server}\n")

    for label, candidates in (("sigma shift", SIGMA_SHIFT_CANDIDATES),
                              ("acceleration", ACCEL_CANDIDATES)):
        found = pick(available, candidates)
        if found:
            print(f"  {label:13} OK      {found}")
            print(f"                        inputs: {describe(available, found)}")
        else:
            print(f"  {label:13} MISSING  tried {', '.join(candidates)}")
    print()

    for node in ("MiniMaxH3TurboLoRA", "MiniMaxH3TurboSampler",
                 "MiniMaxH3ReferenceToVideo", "UNETLoader"):
        print(f"  {'baseline':13} {'OK     ' if node in available else 'MISSING'} {node}")
    return 0


def insert_model_patches(
    nodes: dict[str, Any],
    available: dict[str, Any],
    sigma_shift: float | None,
    sigma_shift_audio: float | None,
    accel: bool,
    accel_overrides: dict[str, Any],
) -> list[str]:
    """
    Splice sigma shift and acceleration between the model source and everything
    that consumes a MODEL, then rewire the consumers onto the last patch.

    h3_runner builds node 6 as UNETLoader and node 18 as the Turbo LoRA when
    turbo is on, and both BasicScheduler (9) and BasicGuider (16) read from
    whichever is active. Patches go after that, so acceleration wraps the LoRA
    rather than being overwritten by it.
    """
    applied: list[str] = []
    source = "18" if "18" in nodes else "6"
    next_id = 900

    if sigma_shift is not None:
        name = pick(available, SIGMA_SHIFT_CANDIDATES)
        if not name:
            raise base.ComfyError(
                "no sigma-shift node on this server; tried "
                + ", ".join(SIGMA_SHIFT_CANDIDATES)
                + ". Run --probe to see what is installed.")
        # The shift parameter is neither named nor scaled the same on every
        # candidate node: ModelSamplingSD3 takes one "shift", MiniMaxH3SigmaShift
        # takes "shift_video" (default 12.0) and "shift_audio" (default 3.0).
        # Those defaults differ by 4x, so forcing one number onto both is a guess
        # dressed up as a fix. Read the names AND the declared defaults off the
        # server, and override only what was asked for.
        required = (available[name].get("input", {}) or {}).get("required", {}) or {}
        shift_inputs = [k for k in required if k == "shift" or k.startswith("shift_")]
        if not shift_inputs:
            raise base.ComfyError(
                f"{name} has no shift-like input; its inputs are "
                + ", ".join(required) + ". Run --probe.")
        node_id = str(next_id); next_id += 1
        inputs: dict[str, Any] = {"model": [source, 0]}
        for key in shift_inputs:
            spec = required[key]
            default = spec[1].get("default") if len(spec) > 1 else None
            if key == "shift_audio" and sigma_shift_audio is not None:
                inputs[key] = sigma_shift_audio
            elif key == "shift_audio":
                inputs[key] = default          # leave audio on the node's default
            else:
                inputs[key] = sigma_shift       # "shift" / "shift_video"
        nodes[node_id] = {"class_type": name, "inputs": inputs}
        source = node_id
        applied.append(f"{name}(" + ", ".join(
            f"{k}={v}" for k, v in inputs.items() if k != "model") + ")")

    if accel:
        name = pick(available, ACCEL_CANDIDATES)
        if not name:
            raise base.ComfyError(
                "JR_H3_UnifiedAcceleration is not installed. Clone "
                "Goldlionren/ComfyUI_JR_MiniMaxH3Node into custom_nodes and "
                "install its requirements, then restart ComfyUI.")
        # Only send keys the installed node actually declares: it is young and
        # its signature will move.
        declared = (available[name].get("input", {}) or {}).get("required", {}) or {}
        params = {**ACCEL_DEFAULTS, **accel_overrides}
        inputs = {k: v for k, v in params.items() if k in declared}
        dropped = sorted(set(params) - set(inputs))
        inputs["model"] = [source, 0]

        node_id = str(next_id); next_id += 1
        nodes[node_id] = {"class_type": name, "inputs": inputs}
        source = node_id
        applied.append(f"{name}(sage={inputs.get('sage_attention')}, "
                       f"sol={inputs.get('enable_sol_attn')})")
        if dropped:
            print(f"  note: node does not declare {', '.join(dropped)}; not sent")

    if applied:
        for consumer in ("9", "16"):
            if consumer in nodes and "model" in nodes[consumer]["inputs"]:
                nodes[consumer]["inputs"]["model"] = [source, 0]
    return applied


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="MiniMax H3 runner with sigma shift and attention acceleration.")
    parser.add_argument("mode", nargs="?", choices=["t2v", "i2v", "flf2v", "r2v"])
    parser.add_argument("--probe", action="store_true",
                        help="report which experimental nodes the server has, then exit")
    parser.add_argument("--sigma-shift", type=float, default=None,
                        help="enable the sampling-schedule node with this video shift")
    parser.add_argument("--sigma-shift-audio", type=float, default=None,
                        help="audio shift; omitted means the node's own default")
    parser.add_argument("--accel", action="store_true",
                        help="enable JR_H3_UnifiedAcceleration with its own defaults")
    parser.add_argument("--accel-set", action="append", default=[], metavar="KEY=VALUE",
                        help="override one acceleration parameter, repeatable")
    base.add_common_args(parser)
    args = parser.parse_args(argv)

    if args.probe:
        return probe(args.server)
    if not args.mode:
        parser.error("a mode is required unless --probe is given")
    if args.prompt_file:
        path = base.Path(args.prompt_file)
        if not path.exists():
            raise SystemExit(f"Prompt file not found: {path}")
        args.prompt = path.read_text(encoding="utf-8").strip()
    if not args.prompt or not str(args.prompt).strip():
        raise SystemExit("Generation prompt is required. Use --prompt or --prompt-file.")
    args.prompt = str(args.prompt).strip()

    overrides: dict[str, Any] = {}
    for item in args.accel_set:
        if "=" not in item:
            raise SystemExit(f"--accel-set wants KEY=VALUE, got {item!r}")
        key, _, raw = item.partition("=")
        if raw.lower() in ("true", "false"):
            value: Any = raw.lower() == "true"
        else:
            try:
                value = int(raw)
            except ValueError:
                try:
                    value = float(raw)
                except ValueError:
                    value = raw
        overrides[key.strip()] = value

    prompt = base.build_prompt_from_args(args)

    applied: list[str] = []
    if args.sigma_shift is not None or args.accel:
        applied = insert_model_patches(
            prompt, fetch_object_info(args.server), args.sigma_shift,
            args.sigma_shift_audio,
            args.accel, overrides)

    print(f"MiniMax H3 mode={args.mode} seed={args.seed} "
          f"frames={base.duration_to_h3_frames(args.duration)} "
          f"size={args.width}x{args.height} steps={args.steps} "
          f"turbo={'on' if args.turbo else 'off'}", flush=True)
    print("patches: " + (" -> ".join(applied) if applied
                         else "none (this is the baseline graph)"), flush=True)

    if args.save_api_json:
        path = base.Path(args.save_api_json)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(prompt, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Saved ComfyUI API JSON: {path}", flush=True)
    if args.no_submit:
        return 0

    client_id = args.client_id or base.uuid.uuid4().__str__()
    prompt_id = base.queue_prompt(args.server, prompt, client_id)
    print(f"Queued prompt_id={prompt_id}", flush=True)

    record = base.wait_for_history(args.server, prompt_id, args.poll, args.timeout)
    saved = base.choose_video_file(base.collect_saved_files(record.get("outputs", {})))
    target = base.download_saved_file(args.server, saved, base.Path(args.output_dir))
    print(f"Downloaded: {target.resolve()}", flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except KeyboardInterrupt:
        raise SystemExit(130)
    except base.ComfyError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
