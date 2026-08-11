#!/usr/bin/env python3
"""Generate MiniMax H3 opening frames for commercial video references.

The script is intentionally small and keeps secrets local:
- reads API keys from .env.local or the process environment;
- supports OpenRouter's Image API and direct OpenAI Image API;
- sends product/logo references as actual image inputs;
- writes generated PNGs and redacted metadata only.
"""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import sys
import time
import uuid
from pathlib import Path
from typing import Any
from urllib import error, request


DEFAULT_ENV = ".env.local"
DEFAULT_PROVIDER = "openrouter"
DEFAULT_ENDPOINT = "https://openrouter.ai/api/v1/images"
DEFAULT_OPENAI_ENDPOINT = "https://api.openai.com/v1"
DEFAULT_MODEL = "openai/gpt-image-2"
DEFAULT_OPENAI_MODEL = "gpt-image-2"
DEFAULT_SIZE = "1024x1536"
DEFAULT_FINAL_SIZE = "1080x1920"
DEFAULT_QUALITY = "high"
DEFAULT_ASPECT_RATIO = "9:16"
DEFAULT_RESOLUTION = ""


class Image2Error(RuntimeError):
    pass


def load_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def env_value(key: str, env_file: dict[str, str], default: str = "") -> str:
    return os.environ.get(key) or env_file.get(key) or default


def parse_size(value: str) -> tuple[int, int]:
    try:
        width_raw, height_raw = value.lower().split("x", 1)
        width = int(width_raw)
        height = int(height_raw)
    except ValueError as exc:
        raise SystemExit(f"Invalid size {value!r}; expected WIDTHxHEIGHT") from exc
    if width <= 0 or height <= 0:
        raise SystemExit(f"Invalid size {value!r}; dimensions must be positive")
    return width, height


def data_url(path: Path) -> str:
    if not path.is_file():
        raise SystemExit(f"Missing reference image: {path}")
    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def build_payload(
    *,
    prompt: str,
    references: list[Path],
    model: str,
    size: str,
    quality: str,
) -> dict[str, Any]:
    prompt_with_requirements = (
        prompt.strip()
        + "\n\nOutput requirements: generate exactly one vertical PNG image. "
        + f"Provider request size: {size}. Use {quality} quality. "
        + "Use the supplied image references as visual identity anchors. "
        + "Do not create subtitles, title cards, watermarks, lower-thirds, or floating logos."
    )
    payload: dict[str, Any] = {
        "model": model,
        "prompt": prompt_with_requirements,
        "size": size,
        "quality": quality,
        "output_format": "png",
    }
    if references:
        payload["input_references"] = [
            {"type": "image_url", "image_url": {"url": data_url(path)}}
            for path in references
        ]
    return payload


def openrouter_payload(
    *,
    prompt: str,
    references: list[Path],
    model: str,
    size: str,
    quality: str,
    aspect_ratio: str,
    resolution: str,
) -> dict[str, Any]:
    prompt_with_requirements = (
        prompt.strip()
        + "\n\nOutput requirements: generate exactly one vertical PNG image. "
        + "Use the supplied image references as visual identity anchors. "
        + "Do not create subtitles, title cards, watermarks, lower-thirds, or floating logos."
    )
    payload: dict[str, Any] = {
        "model": model,
        "prompt": prompt_with_requirements,
        "n": 1,
    }

    # OpenRouter's per-endpoint records for GPT Image 2 list aspect_ratio but
    # not explicit size. Other providers such as Seedream prefer resolution.
    if aspect_ratio:
        payload["aspect_ratio"] = aspect_ratio
    if resolution:
        payload["resolution"] = resolution
    elif not model.startswith("openai/gpt-image") and size:
        payload["size"] = size

    if model.startswith("openai/gpt-image"):
        payload["quality"] = quality
        payload["output_format"] = "png"

    if references:
        payload["input_references"] = [
            {"type": "image_url", "image_url": {"url": data_url(path)}}
            for path in references
        ]
    return payload


def openai_generation_payload(
    *,
    prompt: str,
    model: str,
    size: str,
    quality: str,
) -> dict[str, Any]:
    return {
        "model": model,
        "prompt": (
            prompt.strip()
            + "\n\nOutput requirements: generate exactly one vertical PNG image. "
            + "Use high-fidelity commercial product photography. "
            + "Do not create subtitles, title cards, watermarks, lower-thirds, or floating logos."
        ),
        "size": size,
        "quality": quality,
        "output_format": "png",
        "n": 1,
    }


def redact_payload(payload: dict[str, Any]) -> dict[str, Any]:
    redacted = json.loads(json.dumps(payload))
    for item in redacted.get("input_references", []):
        image_url = item.get("image_url") if isinstance(item, dict) else None
        if isinstance(image_url, dict) and str(image_url.get("url", "")).startswith("data:"):
            image_url["url"] = "<redacted data URL>"
    return redacted


def provider_terms_hint(body: str) -> str:
    if "provider Terms Of Service" not in body:
        return ""
    return (
        "\nDiagnosis: OpenRouter accepted the API key, but the upstream provider "
        "blocked this model for the account/request under provider terms. This "
        "is not caused by the prompt, logo reference, or image-reference field. "
        "For OpenAI image models, use an OpenRouter account allowed for OpenAI "
        "models, or set VSR_IMAGE_PROVIDER=openai with a direct OPENAI_API_KEY "
        "from a verified OpenAI API organization."
    )


def post_json(payload: dict[str, Any], *, api_key: str, endpoint: str, timeout: int) -> dict[str, Any]:
    req = request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/SydneyMCDonaldbigking/MINIMAXH3_Autoworkflow",
            "X-Title": "MINIMAXH3_Autoworkflow",
        },
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise Image2Error(f"HTTP {exc.code}: {body}{provider_terms_hint(body)}") from exc
    except error.URLError as exc:
        raise Image2Error(f"Request failed: {exc}") from exc


def multipart_body(fields: dict[str, str], files: list[tuple[str, Path]]) -> tuple[bytes, str]:
    boundary = f"----codex-h3-image2-{uuid.uuid4().hex}"
    chunks: list[bytes] = []
    for key, value in fields.items():
        chunks.append(f"--{boundary}\r\n".encode("utf-8"))
        chunks.append(
            f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode("utf-8")
        )
        chunks.append(str(value).encode("utf-8"))
        chunks.append(b"\r\n")
    for key, path in files:
        mime = mimetypes.guess_type(path.name)[0] or "image/png"
        chunks.append(f"--{boundary}\r\n".encode("utf-8"))
        chunks.append(
            (
                f'Content-Disposition: form-data; name="{key}"; '
                f'filename="{path.name}"\r\n'
                f"Content-Type: {mime}\r\n\r\n"
            ).encode("utf-8")
        )
        chunks.append(path.read_bytes())
        chunks.append(b"\r\n")
    chunks.append(f"--{boundary}--\r\n".encode("utf-8"))
    return b"".join(chunks), boundary


def post_openai_images(
    *,
    prompt: str,
    references: list[Path],
    api_key: str,
    endpoint: str,
    model: str,
    size: str,
    quality: str,
    timeout: int,
) -> dict[str, Any]:
    base = endpoint.rstrip("/")
    if references:
        fields = {
            "model": model,
            "prompt": (
                prompt.strip()
                + "\n\nOutput requirements: generate exactly one vertical PNG image. "
                + "Use the supplied images as high-fidelity visual identity anchors. "
                + "Do not create subtitles, title cards, watermarks, lower-thirds, or floating logos."
            ),
            "size": size,
            "quality": quality,
            "output_format": "png",
        }
        files = [("image[]", path) for path in references]
        body, boundary = multipart_body(fields, files)
        req = request.Request(
            f"{base}/images/edits",
            data=body,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": f"multipart/form-data; boundary={boundary}",
            },
            method="POST",
        )
    else:
        payload = openai_generation_payload(
            prompt=prompt,
            model=model,
            size=size,
            quality=quality,
        )
        req = request.Request(
            f"{base}/images/generations",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
    try:
        with request.urlopen(req, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise Image2Error(f"OpenAI HTTP {exc.code}: {body}") from exc
    except error.URLError as exc:
        raise Image2Error(f"OpenAI request failed: {exc}") from exc


def image_candidates(response: dict[str, Any]) -> list[tuple[str, str]]:
    candidates: list[tuple[str, str]] = []
    for item in response.get("data", []) or []:
        if not isinstance(item, dict):
            continue
        if item.get("b64_json"):
            candidates.append(("b64", str(item["b64_json"])))
        elif item.get("url"):
            candidates.append(("url", str(item["url"])))

    for choice in response.get("choices", []) or []:
        if not isinstance(choice, dict):
            continue
        message = choice.get("message", {})
        if not isinstance(message, dict):
            continue
        for item in message.get("images", []) or []:
            if isinstance(item, dict):
                url = item.get("image_url", item)
                if isinstance(url, dict):
                    url = url.get("url")
                if url:
                    candidates.append(("url", str(url)))
    return candidates


def save_candidate(kind: str, value: str, out_path: Path, timeout: int) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if kind == "b64":
        out_path.write_bytes(base64.b64decode(value))
        return
    if value.startswith("data:image"):
        _, encoded = value.split(",", 1)
        out_path.write_bytes(base64.b64decode(encoded))
        return
    with request.urlopen(value, timeout=timeout) as response_obj:
        out_path.write_bytes(response_obj.read())


def reframe_cover(input_path: Path, output_path: Path, final_size: str) -> bool:
    try:
        from PIL import Image
    except Exception:
        return False

    target_w, target_h = parse_size(final_size)
    with Image.open(input_path) as image:
        rgb = image.convert("RGB")
        src_w, src_h = rgb.size
        scale = max(target_w / src_w, target_h / src_h)
        resized_w = round(src_w * scale)
        resized_h = round(src_h * scale)
        resized = rgb.resize((resized_w, resized_h), Image.Resampling.LANCZOS)
        left = max(0, (resized_w - target_w) // 2)
        top = max(0, (resized_h - target_h) // 2)
        cropped = resized.crop((left, top, left + target_w, top + target_h))
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cropped.save(output_path)
    return True


def generate(args: argparse.Namespace) -> dict[str, Any]:
    env_file = load_env(Path(args.env_file))
    provider = (args.provider or env_value("VSR_IMAGE_PROVIDER", env_file, DEFAULT_PROVIDER)).lower()
    if provider in {"direct_openai", "openai_direct"}:
        provider = "openai"
    if provider not in {"openrouter", "openai"}:
        raise SystemExit("--provider must be openrouter or openai")

    api_key = (
        env_value("OPENAI_API_KEY", env_file)
        if provider == "openai"
        else env_value("OPENROUTER_API_KEY", env_file)
    )
    model = args.model or (
        env_value("OPENAI_IMAGE_MODEL", env_file, DEFAULT_OPENAI_MODEL)
        if provider == "openai"
        else env_value("VSR_IMAGE_API_MODEL", env_file, DEFAULT_MODEL)
    )
    endpoint = args.endpoint or (
        env_value("OPENAI_BASE_URL", env_file, DEFAULT_OPENAI_ENDPOINT)
        if provider == "openai"
        else env_value("VSR_IMAGE_ENDPOINT", env_file, DEFAULT_ENDPOINT)
    )
    quality = args.quality or env_value("VSR_IMAGE_QUALITY", env_file, DEFAULT_QUALITY)
    size = args.size or env_value("H3_FIRST_FRAME_PROVIDER_SIZE", env_file, DEFAULT_SIZE)
    final_size = args.final_size or env_value("H3_FIRST_FRAME_FINAL_SIZE", env_file, DEFAULT_FINAL_SIZE)
    timeout = int(env_value("VSR_OPENROUTER_TIMEOUT_SECONDS", env_file, "420"))
    aspect_ratio = args.aspect_ratio or env_value("H3_OPENROUTER_ASPECT_RATIO", env_file, DEFAULT_ASPECT_RATIO)
    resolution = args.resolution or env_value("H3_OPENROUTER_RESOLUTION", env_file, DEFAULT_RESOLUTION)

    prompt_path = Path(args.prompt_file)
    if not prompt_path.is_file():
        raise SystemExit(f"Missing prompt file: {prompt_path}")
    prompt = prompt_path.read_text(encoding="utf-8")
    references = [Path(path) for path in args.reference]
    out_dir = Path(args.out_dir)
    original_dir = out_dir / "generated-original-size"
    generated_dir = out_dir / "generated"
    meta_dir = out_dir / "metadata"
    stem = args.stem or prompt_path.stem

    payload = (
        openrouter_payload(
            prompt=prompt,
            references=references,
            model=model,
            size=size,
            quality=quality,
            aspect_ratio=aspect_ratio,
            resolution=resolution,
        )
        if provider == "openrouter"
        else openai_generation_payload(
            prompt=prompt,
            model=model,
            size=size,
            quality=quality,
        )
    )
    metadata = {
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "provider": provider,
        "endpoint": endpoint,
        "model": model,
        "quality": quality,
        "provider_size": size,
        "aspect_ratio": aspect_ratio if provider == "openrouter" else None,
        "resolution": resolution if provider == "openrouter" else None,
        "final_size": final_size,
        "prompt_file": str(prompt_path),
        "references": [str(path) for path in references],
        "payload": redact_payload(payload),
    }
    if args.dry_run:
        print(json.dumps({**metadata, "api_key_set": bool(api_key)}, ensure_ascii=False, indent=2))
        return metadata
    if not api_key:
        key_name = "OPENAI_API_KEY" if provider == "openai" else "OPENROUTER_API_KEY"
        raise SystemExit(f"{key_name} is not set. Put it in .env.local.")

    if provider == "openai":
        response = post_openai_images(
            prompt=prompt,
            references=references,
            api_key=api_key,
            endpoint=endpoint,
            model=model,
            size=size,
            quality=quality,
            timeout=timeout,
        )
    else:
        response = post_json(payload, api_key=api_key, endpoint=endpoint, timeout=timeout)
    candidates = image_candidates(response)
    if not candidates:
        meta_dir.mkdir(parents=True, exist_ok=True)
        (meta_dir / f"{stem}-response-no-image.json").write_text(
            json.dumps(response, ensure_ascii=False, indent=2)[:20000],
            encoding="utf-8",
        )
        raise Image2Error("OpenRouter response did not contain an image")

    saved: list[str] = []
    reframed: list[str] = []
    for index, (kind, value) in enumerate(candidates, start=1):
        original_path = original_dir / f"{stem}-{index}.png"
        save_candidate(kind, value, original_path, timeout)
        saved.append(str(original_path.resolve()))
        final_path = generated_dir / f"{stem}-{index}.png"
        if reframe_cover(original_path, final_path, final_size):
            reframed.append(str(final_path.resolve()))

    metadata["saved_originals"] = saved
    metadata["saved_reframed"] = reframed
    metadata["response_id"] = response.get("id")
    metadata["usage"] = response.get("usage")
    meta_dir.mkdir(parents=True, exist_ok=True)
    meta_path = meta_dir / f"{stem}-metadata.json"
    meta_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"saved_originals": saved, "saved_reframed": reframed, "metadata": str(meta_path.resolve())}, ensure_ascii=False, indent=2))
    return metadata


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate GPT Image 2 first frames for MiniMax H3.")
    parser.add_argument("--env-file", default=DEFAULT_ENV)
    parser.add_argument("--provider", choices=["openrouter", "openai", "direct_openai", "openai_direct"])
    parser.add_argument("--prompt-file", required=True)
    parser.add_argument("--out-dir", default="outputs/image2_first_frames")
    parser.add_argument("--stem")
    parser.add_argument("--reference", action="append", default=[])
    parser.add_argument("--model")
    parser.add_argument("--endpoint")
    parser.add_argument("--quality")
    parser.add_argument("--size")
    parser.add_argument("--aspect-ratio")
    parser.add_argument("--resolution")
    parser.add_argument("--final-size")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    try:
        generate(parse_args(argv))
        return 0
    except KeyboardInterrupt:
        return 130
    except Image2Error as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
