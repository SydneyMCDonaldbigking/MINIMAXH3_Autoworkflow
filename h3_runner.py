#!/usr/bin/env python3
"""
Minimal MiniMax H3 runner for a headless ComfyUI server.

This script builds ComfyUI API prompts for:
  - t2v: text to video
  - i2v: first-frame image to video
  - flf2v: first+last-frame image to video
  - r2v: reference image(s) to video

It can submit jobs to a running ComfyUI API, poll the result, and download the
saved video. It uses only the Python standard library so it is easy to copy to a
fresh server.
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import random
import sys
import time
import uuid
from pathlib import Path
from typing import Any
from urllib import error, parse, request


FL2VA_DIFFUSION_MODEL = "minimax_h3_fl2va_pruned_int8_convrot.safetensors"
REF2VA_DIFFUSION_MODEL = "minimax_h3_ref2va_pruned_int8_convrot.safetensors"
TEXT_ENCODER = "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors"
VIDEO_VAE = "minimax_h3_video_vae_fp16.safetensors"
AUDIO_VAE = "minimax_h3_audio_vae_fp32.safetensors"

DEFAULT_SERVER = "http://127.0.0.1:8189"
DEFAULT_PREFIX = "video/MiniMax_H3"
DEFAULT_FPS = 24.0
DEFAULT_WIDTH = 1344
DEFAULT_HEIGHT = 768
DEFAULT_DURATION = 5.0
DEFAULT_STEPS = 20
DEFAULT_TURBO_STEPS = 8
DEFAULT_SAMPLER = "res_multistep"
DEFAULT_SCHEDULER = "simple"
DEFAULT_TURBO_LORA = "minimax_h3_turbo_v4_step600_ema.safetensors"


class ComfyError(RuntimeError):
    pass


def duration_to_h3_frames(seconds: float) -> int:
    """MiniMax H3 wants 24fps lengths where frame_count % 17 == 5."""
    raw = max(5, round(seconds * 24))
    return raw + ((5 - raw % 17) % 17)


def ensure_multiple_of_32(value: int, name: str) -> int:
    if value <= 0 or value % 32 != 0:
        raise SystemExit(f"{name} must be a positive multiple of 32, got {value}")
    return value


def api_url(server: str, path: str, query: dict[str, str] | None = None) -> str:
    server = server.rstrip("/")
    url = f"{server}{path}"
    if query:
        url += "?" + parse.urlencode(query)
    return url


def http_json(
    method: str,
    server: str,
    path: str,
    payload: dict[str, Any] | None = None,
    timeout: int = 60,
) -> dict[str, Any]:
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = request.Request(
        api_url(server, path),
        data=data,
        headers=headers,
        method=method.upper(),
    )
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            body = resp.read()
    except error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        raise ComfyError(f"HTTP {exc.code} from {path}: {details}") from exc
    except error.URLError as exc:
        raise ComfyError(f"Cannot reach ComfyUI at {server}: {exc}") from exc

    if not body:
        return {}
    return json.loads(body.decode("utf-8"))


def upload_image(
    server: str,
    image_path: Path,
    image_type: str = "input",
    overwrite: bool = False,
) -> str:
    if not image_path.exists():
        raise SystemExit(f"Image not found: {image_path}")

    boundary = f"----comfy-h3-{uuid.uuid4().hex}"
    mime = mimetypes.guess_type(str(image_path))[0] or "application/octet-stream"
    file_bytes = image_path.read_bytes()

    parts: list[bytes] = []

    def add_field(name: str, value: str) -> None:
        parts.append(f"--{boundary}\r\n".encode("ascii"))
        parts.append(
            f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("ascii")
        )
        parts.append(value.encode("utf-8"))
        parts.append(b"\r\n")

    def add_file(name: str, filename: str, body: bytes) -> None:
        parts.append(f"--{boundary}\r\n".encode("ascii"))
        disposition = f'Content-Disposition: form-data; name="{name}"; filename="{filename}"'
        parts.append((disposition + "\r\n").encode("utf-8"))
        parts.append(f"Content-Type: {mime}\r\n\r\n".encode("ascii"))
        parts.append(body)
        parts.append(b"\r\n")

    add_file("image", image_path.name, file_bytes)
    add_field("type", image_type)
    add_field("overwrite", "true" if overwrite else "false")
    parts.append(f"--{boundary}--\r\n".encode("ascii"))
    data = b"".join(parts)

    req = request.Request(
        api_url(server, "/upload/image"),
        data=data,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=180) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        raise ComfyError(f"Image upload failed for {image_path}: {details}") from exc
    except error.URLError as exc:
        raise ComfyError(f"Cannot upload to ComfyUI at {server}: {exc}") from exc

    name = result.get("name")
    subfolder = result.get("subfolder")
    if not name:
        raise ComfyError(f"Unexpected upload response: {result}")
    if subfolder:
        return f"{subfolder}/{name}"
    return name


def load_image_node(image_name: str) -> dict[str, Any]:
    return {"class_type": "LoadImage", "inputs": {"image": image_name}}


def common_nodes(
    conditioning_node: str,
    diffusion_model: str,
    seed: int,
    steps: int,
    sampler: str,
    scheduler: str,
    prefix: str,
    turbo_lora: str | None = None,
    turbo_strength: float = 1.0,
    turbo_low_vram: bool = False,
    no_audio: bool = False,
) -> dict[str, Any]:
    model_node = "18" if turbo_lora else "6"
    nodes: dict[str, Any] = {
        "6": {
            "class_type": "UNETLoader",
            "inputs": {
                "unet_name": diffusion_model,
                "weight_dtype": "default",
            },
        },
        "13": {
            "class_type": "CLIPLoader",
            "inputs": {
                "clip_name": TEXT_ENCODER,
                "type": "minimax",
                "device": "default",
            },
        },
        "11": {
            "class_type": "VAELoader",
            "inputs": {"vae_name": VIDEO_VAE},
        },
        "24": {
            "class_type": "VAELoader",
            "inputs": {"vae_name": AUDIO_VAE},
        },
        "15": {
            "class_type": "RandomNoise",
            "inputs": {"noise_seed": seed},
        },
        "17": {
            "class_type": "MiniMaxH3TurboSampler" if turbo_lora else "KSamplerSelect",
            "inputs": {} if turbo_lora else {"sampler_name": sampler},
        },
        "9": {
            "class_type": "BasicScheduler",
            "inputs": {
                "model": [model_node, 0],
                "scheduler": scheduler,
                "steps": steps,
                "denoise": 1.0,
            },
        },
        "16": {
            "class_type": "BasicGuider",
            "inputs": {
                "model": [model_node, 0],
                "conditioning": [conditioning_node, 0],
            },
        },
        "14": {
            "class_type": "SamplerCustomAdvanced",
            "inputs": {
                "noise": ["15", 0],
                "guider": ["16", 0],
                "sampler": ["17", 0],
                "sigmas": ["9", 0],
                "latent_image": [conditioning_node, 1],
            },
        },
        "10": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["14", 0],
                "vae": ["11", 0],
            },
        },
        "23": {
            "class_type": "VAEDecodeAudio",
            "inputs": {
                "samples": ["14", 0],
                "vae": ["24", 0],
            },
        },
        "91": {
            "class_type": "CreateVideo",
            "inputs": {
                "images": ["10", 0],
                "fps": DEFAULT_FPS,
                "bit_depth": 8,
            },
        },
        "92": {
            "class_type": "SaveVideo",
            "inputs": {
                "video": ["91", 0],
                "filename_prefix": prefix,
                "format": "auto",
                "codec": "auto",
            },
        },
    }
    if no_audio:
        nodes.pop("23", None)
    else:
        nodes["91"]["inputs"]["audio"] = ["23", 0]
    if turbo_lora:
        nodes["18"] = {
            "class_type": "MiniMaxH3TurboLoRA",
            "inputs": {
                "model": ["6", 0],
                "lora_name": turbo_lora,
                "strength": turbo_strength,
                "low_vram": turbo_low_vram,
            },
        }
    return nodes


def build_i2v_like_prompt(
    prompt: str,
    width: int,
    height: int,
    frames: int,
    seed: int,
    steps: int,
    sampler: str,
    scheduler: str,
    prefix: str,
    first_frame_name: str | None = None,
    last_frame_name: str | None = None,
    diffusion_model: str = FL2VA_DIFFUSION_MODEL,
    turbo_lora: str | None = None,
    turbo_strength: float = 1.0,
    turbo_low_vram: bool = False,
    no_audio: bool = False,
) -> dict[str, Any]:
    nodes = common_nodes(
        "104",
        diffusion_model,
        seed,
        steps,
        sampler,
        scheduler,
        prefix,
        turbo_lora=turbo_lora,
        turbo_strength=turbo_strength,
        turbo_low_vram=turbo_low_vram,
        no_audio=no_audio,
    )
    h3_inputs: dict[str, Any] = {
        "clip": ["13", 0],
        "vae": ["11", 0],
        "prompt": prompt,
        "width": width,
        "height": height,
        "length": frames,
    }

    next_id = 200
    if first_frame_name:
        node_id = str(next_id)
        next_id += 1
        nodes[node_id] = load_image_node(first_frame_name)
        h3_inputs["first_frame"] = [node_id, 0]
    if last_frame_name:
        node_id = str(next_id)
        nodes[node_id] = load_image_node(last_frame_name)
        h3_inputs["last_frame"] = [node_id, 0]

    nodes["104"] = {
        "class_type": "MiniMaxH3ImageToVideo",
        "inputs": h3_inputs,
    }
    return nodes


def build_r2v_prompt(
    prompt: str,
    width: int,
    height: int,
    frames: int,
    seed: int,
    steps: int,
    sampler: str,
    scheduler: str,
    prefix: str,
    ref_image_names: list[str],
    ref_image_size: str,
    diffusion_model: str = REF2VA_DIFFUSION_MODEL,
    turbo_lora: str | None = None,
    turbo_strength: float = 1.0,
    turbo_low_vram: bool = False,
    no_audio: bool = False,
) -> dict[str, Any]:
    if len(ref_image_names) > 9:
        raise SystemExit("MiniMax H3 reference-image workflow supports up to 9 images")

    nodes = common_nodes(
        "136",
        diffusion_model,
        seed,
        steps,
        sampler,
        scheduler,
        prefix,
        turbo_lora=turbo_lora,
        turbo_strength=turbo_strength,
        turbo_low_vram=turbo_low_vram,
        no_audio=no_audio,
    )
    h3_inputs: dict[str, Any] = {
        "clip": ["13", 0],
        "vae": ["11", 0],
        "audio_vae": ["24", 0],
        "prompt": prompt,
        "width": width,
        "height": height,
        "length": frames,
        "ref_image_size": ref_image_size,
    }

    next_id = 300
    for index, image_name in enumerate(ref_image_names):
        node_id = str(next_id)
        next_id += 1
        nodes[node_id] = load_image_node(image_name)
        h3_inputs[f"ref_images.ref_image_{index}"] = [node_id, 0]

    nodes["136"] = {
        "class_type": "MiniMaxH3ReferenceToVideo",
        "inputs": h3_inputs,
    }
    return nodes


def collect_saved_files(value: Any) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    if isinstance(value, dict):
        if "filename" in value:
            found.append(value)
        for child in value.values():
            found.extend(collect_saved_files(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(collect_saved_files(child))
    return found


def choose_video_file(files: list[dict[str, Any]]) -> dict[str, Any]:
    if not files:
        raise ComfyError("Job finished, but no saved files were found in history")

    video_exts = {".mp4", ".mov", ".webm", ".mkv", ".avi"}
    for item in files:
        suffix = Path(str(item.get("filename", ""))).suffix.lower()
        if suffix in video_exts:
            return item
    return files[0]


def queue_prompt(server: str, prompt: dict[str, Any], client_id: str) -> str:
    result = http_json(
        "POST",
        server,
        "/prompt",
        {"prompt": prompt, "client_id": client_id},
        timeout=120,
    )
    prompt_id = result.get("prompt_id")
    if not prompt_id:
        raise ComfyError(f"Unexpected /prompt response: {result}")
    return str(prompt_id)


def wait_for_history(
    server: str,
    prompt_id: str,
    poll_seconds: float,
    timeout_seconds: float,
) -> dict[str, Any]:
    started = time.time()
    while True:
        history = http_json("GET", server, f"/history/{prompt_id}", timeout=60)
        if prompt_id in history:
            record = history[prompt_id]
            status = record.get("status", {})
            if status.get("status_str") == "error":
                messages = status.get("messages", [])
                raise ComfyError(f"ComfyUI job failed: {messages}")
            return record

        elapsed = time.time() - started
        if elapsed > timeout_seconds:
            raise ComfyError(f"Timed out waiting for prompt {prompt_id}")
        print(f"Waiting for ComfyUI job... {elapsed:.0f}s", flush=True)
        time.sleep(poll_seconds)


def download_saved_file(
    server: str,
    saved_file: dict[str, Any],
    output_dir: Path,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = str(saved_file["filename"])
    subfolder = str(saved_file.get("subfolder") or "")
    file_type = str(saved_file.get("type") or "output")
    target = output_dir / Path(filename).name

    url = api_url(
        server,
        "/view",
        {"filename": filename, "subfolder": subfolder, "type": file_type},
    )
    try:
        with request.urlopen(url, timeout=300) as resp:
            target.write_bytes(resp.read())
    except error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        raise ComfyError(f"Download failed: HTTP {exc.code}: {details}") from exc
    except error.URLError as exc:
        raise ComfyError(f"Download failed: {exc}") from exc
    return target


def maybe_upload_images(args: argparse.Namespace) -> tuple[str | None, str | None, list[str]]:
    if args.save_api_json and args.no_submit:
        first = Path(args.first_frame).name if args.first_frame else None
        last = Path(args.last_frame).name if args.last_frame else None
        refs = [Path(p).name for p in args.ref_image]
        return first, last, refs

    first = (
        upload_image(args.server, Path(args.first_frame), overwrite=args.overwrite_upload)
        if args.first_frame
        else None
    )
    last = (
        upload_image(args.server, Path(args.last_frame), overwrite=args.overwrite_upload)
        if args.last_frame
        else None
    )
    refs = [
        upload_image(args.server, Path(p), overwrite=args.overwrite_upload)
        for p in args.ref_image
    ]
    return first, last, refs


def build_prompt_from_args(args: argparse.Namespace) -> dict[str, Any]:
    width = ensure_multiple_of_32(args.width, "width")
    height = ensure_multiple_of_32(args.height, "height")
    frames = duration_to_h3_frames(args.duration)
    seed = args.seed if args.seed is not None else random.randint(0, 2**63 - 1)
    args.seed = seed
    if args.turbo and args.steps == DEFAULT_STEPS:
        args.steps = DEFAULT_TURBO_STEPS
    turbo_lora = args.turbo_lora if args.turbo else None

    first, last, refs = maybe_upload_images(args)

    if args.mode == "i2v" and not first:
        raise SystemExit("i2v requires --first-frame")
    if args.mode == "flf2v" and (not first or not last):
        raise SystemExit("flf2v requires --first-frame and --last-frame")
    if args.mode == "r2v" and not refs:
        raise SystemExit("r2v requires at least one --ref-image")

    if args.mode in {"t2v", "i2v", "flf2v"}:
        return build_i2v_like_prompt(
            prompt=args.prompt,
            width=width,
            height=height,
            frames=frames,
            seed=seed,
            steps=args.steps,
            sampler=args.sampler,
            scheduler=args.scheduler,
            prefix=args.prefix,
            first_frame_name=first,
            last_frame_name=last,
            diffusion_model=args.diffusion_model or FL2VA_DIFFUSION_MODEL,
            turbo_lora=turbo_lora,
            turbo_strength=args.turbo_strength,
            turbo_low_vram=args.turbo_low_vram,
            no_audio=args.no_audio,
        )

    return build_r2v_prompt(
        prompt=args.prompt,
        width=width,
        height=height,
        frames=frames,
        seed=seed,
        steps=args.steps,
        sampler=args.sampler,
        scheduler=args.scheduler,
        prefix=args.prefix,
        ref_image_names=refs,
        ref_image_size=args.ref_image_size,
        diffusion_model=args.diffusion_model or REF2VA_DIFFUSION_MODEL,
        turbo_lora=turbo_lora,
        turbo_strength=args.turbo_strength,
        turbo_low_vram=args.turbo_low_vram,
        no_audio=args.no_audio,
    )


def add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--server", default=DEFAULT_SERVER, help="ComfyUI API base URL")
    parser.add_argument("--prompt", default=None, help="Generation prompt")
    parser.add_argument("--prompt-file", default=None, help="Read generation prompt from a UTF-8 text file")
    parser.add_argument("--width", type=int, default=DEFAULT_WIDTH)
    parser.add_argument("--height", type=int, default=DEFAULT_HEIGHT)
    parser.add_argument("--duration", type=float, default=DEFAULT_DURATION)
    parser.add_argument("--steps", type=int, default=DEFAULT_STEPS)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--sampler", default=DEFAULT_SAMPLER)
    parser.add_argument("--scheduler", default=DEFAULT_SCHEDULER)
    parser.add_argument("--diffusion-model", default=None)
    parser.add_argument("--prefix", default=DEFAULT_PREFIX)
    parser.add_argument("--output-dir", default="outputs")
    parser.add_argument("--poll", type=float, default=5.0)
    parser.add_argument("--timeout", type=float, default=60 * 60)
    parser.add_argument("--client-id", default=None)
    parser.add_argument("--save-api-json", default=None)
    parser.add_argument("--no-submit", action="store_true")
    parser.add_argument("--overwrite-upload", action="store_true")
    parser.add_argument("--first-frame", default=None)
    parser.add_argument("--last-frame", default=None)
    parser.add_argument("--ref-image", action="append", default=[])
    parser.add_argument("--ref-image-size", choices=["match", "max"], default="match")
    parser.add_argument("--turbo", action="store_true", help="Use MiniMax-H3 Turbo LoRA nodes")
    parser.add_argument("--turbo-lora", default=DEFAULT_TURBO_LORA)
    parser.add_argument("--turbo-strength", type=float, default=1.0)
    parser.add_argument("--turbo-low-vram", action="store_true")
    parser.add_argument("--no-audio", action="store_true", help="Skip H3 audio decode and save a silent video")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Submit MiniMax H3 jobs to a headless ComfyUI server."
    )
    parser.add_argument("mode", choices=["t2v", "i2v", "flf2v", "r2v"])
    add_common_args(parser)
    args = parser.parse_args(argv)
    if args.prompt_file:
        prompt_path = Path(args.prompt_file)
        if not prompt_path.exists():
            raise SystemExit(f"Prompt file not found: {prompt_path}")
        args.prompt = prompt_path.read_text(encoding="utf-8").strip()
    if not args.prompt or not str(args.prompt).strip():
        raise SystemExit("Generation prompt is required. Use --prompt or --prompt-file.")
    args.prompt = str(args.prompt).strip()
    return args


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    prompt = build_prompt_from_args(args)

    print(
        f"MiniMax H3 mode={args.mode} seed={args.seed} "
        f"frames={duration_to_h3_frames(args.duration)} "
        f"size={args.width}x{args.height} steps={args.steps} "
        f"turbo={'on' if args.turbo else 'off'}",
        flush=True,
    )

    if args.save_api_json:
        json_path = Path(args.save_api_json)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(
            json.dumps(prompt, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"Saved ComfyUI API JSON: {json_path}", flush=True)

    if args.no_submit:
        return 0

    client_id = args.client_id or str(uuid.uuid4())
    prompt_id = queue_prompt(args.server, prompt, client_id)
    print(f"Queued prompt_id={prompt_id}", flush=True)

    record = wait_for_history(args.server, prompt_id, args.poll, args.timeout)
    files = collect_saved_files(record.get("outputs", {}))
    saved = choose_video_file(files)
    target = download_saved_file(args.server, saved, Path(args.output_dir))
    print(f"Downloaded: {target.resolve()}", flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except KeyboardInterrupt:
        raise SystemExit(130)
    except ComfyError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
