#!/usr/bin/env python3
"""
Run a MiniMax H3 commercial as several short clips, then stitch them.

The stable A100-40G production path is:
  1. generate three native 1088x1920 clips of about five seconds each;
  2. optionally prepend the previous clip's extracted last frame as the next
     clip's first reference;
  3. concatenate without scaling;
  4. optionally crop 1088x1920 to exact 1080x1920 for delivery.

The script calls h3_runner.py for each clip, so it works against a local ComfyUI
API, an SSH tunnel, or directly on the server.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


DEFAULT_SERVER = "http://127.0.0.1:8188"
DEFAULT_OUTPUT_ROOT = "sequence_outputs"
DEFAULT_WIDTH = 1088
DEFAULT_HEIGHT = 1920
DEFAULT_DURATION = 5.0
DEFAULT_STEPS = 4
DEFAULT_TIMEOUT = 21600.0


class SequenceError(RuntimeError):
    pass


def now_id() -> str:
    return dt.datetime.now().strftime("%Y%m%d_%H%M%S")


def slug(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9._-]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "item"


def as_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


def load_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SequenceError(f"Sequence config not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SequenceError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise SequenceError("Sequence config must be a JSON object")
    return data


def rel_path(value: str | os.PathLike[str], base_dir: Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return (base_dir / path).resolve()


def merge_dict(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    merged.update(override)
    return merged


def read_prompt(clip: dict[str, Any], base_dir: Path) -> str:
    if clip.get("prompt_file"):
        path = rel_path(str(clip["prompt_file"]), base_dir)
        if not path.exists():
            raise SequenceError(f"Prompt file not found: {path}")
        return path.read_text(encoding="utf-8").strip()
    if str(clip.get("prompt") or "").strip():
        return str(clip["prompt"]).strip()
    raise SequenceError(f"Clip {clip.get('id') or clip.get('name') or '?'} needs prompt or prompt_file")


def require_files(paths: list[Path]) -> None:
    missing = [path for path in paths if not path.exists()]
    if missing:
        formatted = "\n".join(f"  - {path}" for path in missing)
        raise SequenceError(f"Missing input file(s):\n{formatted}")


def find_existing_video(path: Path) -> Path | None:
    if not path.exists():
        return None
    candidates: list[Path] = []
    for suffix in ("*.mp4", "*.mov", "*.webm", "*.mkv", "*.avi"):
        candidates.extend(path.glob(suffix))
    if not candidates:
        return None
    return max(candidates, key=lambda item: item.stat().st_mtime)


def parse_downloaded_path(output: str) -> Path | None:
    matches = re.findall(r"Downloaded:\s*(.+)", output)
    if not matches:
        return None
    return Path(matches[-1].strip())


def run_streamed(command: list[str], log_path: Path, timeout: float | None = None) -> tuple[int, str, float]:
    started = time.perf_counter()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    with subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    ) as process:
        assert process.stdout is not None
        with log_path.open("w", encoding="utf-8", newline="\n") as log:
            while True:
                if timeout is not None and time.perf_counter() - started > timeout:
                    process.kill()
                    raise SequenceError(f"Command timed out after {timeout:.0f}s: {' '.join(command)}")
                line = process.stdout.readline()
                if not line:
                    if process.poll() is not None:
                        break
                    time.sleep(0.2)
                    continue
                print(line, end="", flush=True)
                log.write(line)
                log.flush()
                lines.append(line)
            return_code = process.wait()
    return return_code, "".join(lines), time.perf_counter() - started


def ffmpeg_bin(preferred: str | None = None) -> str:
    if preferred:
        found = shutil.which(preferred) or preferred
    else:
        found = shutil.which("ffmpeg")
    if not found:
        raise SequenceError("ffmpeg not found. Install ffmpeg or pass --ffmpeg /path/to/ffmpeg.")
    return found


def concat_line(path: Path) -> str:
    text = path.resolve().as_posix()
    return "file '" + text.replace("'", "'\\''") + "'"


def run_ffmpeg(command: list[str], log_path: Path) -> None:
    code, output, _seconds = run_streamed(command, log_path)
    if code != 0:
        raise SequenceError(f"ffmpeg failed with exit code {code}. See {log_path}\n{output[-1000:]}")


def extract_last_frame(ffmpeg: str, video: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    run_ffmpeg(
        [
            ffmpeg,
            "-y",
            "-sseof",
            "-0.5",
            "-i",
            str(video),
            "-frames:v",
            "1",
            str(target),
        ],
        target.with_suffix(".ffmpeg.log"),
    )


def concat_videos(
    ffmpeg: str,
    videos: list[Path],
    run_dir: Path,
    final_path: Path,
    final_options: dict[str, Any],
    concat_mode: str,
) -> Path:
    concat_file = run_dir / "concat-list.txt"
    concat_file.write_text("\n".join(concat_line(video) for video in videos) + "\n", encoding="utf-8")

    crop = final_options.get("crop") or {}
    crf = str(final_options.get("crf", 16))
    preset = str(final_options.get("preset", "medium"))
    raw_concat = run_dir / (final_path.stem + ".raw-concat.mp4")

    if crop:
        copy_target = raw_concat
    else:
        copy_target = final_path

    if concat_mode in {"copy", "both"}:
        try:
            run_ffmpeg(
                [
                    ffmpeg,
                    "-y",
                    "-f",
                    "concat",
                    "-safe",
                    "0",
                    "-i",
                    str(concat_file),
                    "-c",
                    "copy",
                    str(copy_target),
                ],
                run_dir / "ffmpeg-concat-copy.log",
            )
            if not crop:
                return copy_target
        except SequenceError:
            if concat_mode == "copy":
                raise
            print("Concat copy failed; falling back to high-quality re-encode.", flush=True)

    vf_args: list[str] = []
    input_path: Path | None = None
    if crop and raw_concat.exists():
        input_path = raw_concat
        crop_expr = (
            f"crop={int(crop['width'])}:{int(crop['height'])}:"
            f"{int(crop.get('x', 0))}:{int(crop.get('y', 0))}"
        )
        vf_args = ["-vf", crop_expr]
    else:
        input_path = None
        if crop:
            crop_expr = (
                f"crop={int(crop['width'])}:{int(crop['height'])}:"
                f"{int(crop.get('x', 0))}:{int(crop.get('y', 0))}"
            )
            vf_args = ["-vf", crop_expr]

    if input_path:
        command = [
            ffmpeg,
            "-y",
            "-i",
            str(input_path),
            *vf_args,
            "-c:v",
            "libx264",
            "-crf",
            crf,
            "-preset",
            preset,
            "-pix_fmt",
            "yuv420p",
            "-an",
            "-movflags",
            "+faststart",
            str(final_path),
        ]
    else:
        command = [
            ffmpeg,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_file),
            *vf_args,
            "-c:v",
            "libx264",
            "-crf",
            crf,
            "-preset",
            preset,
            "-pix_fmt",
            "yuv420p",
            "-an",
            "-movflags",
            "+faststart",
            str(final_path),
        ]
    run_ffmpeg(command, run_dir / "ffmpeg-final-encode.log")
    return final_path


def build_h3_command(
    runner: Path,
    server: str,
    clip: dict[str, Any],
    prompt_file: Path,
    output_dir: Path,
    ref_images: list[Path],
    first_frame: Path | None,
    last_frame: Path | None,
) -> list[str]:
    mode = str(clip.get("mode", "r2v"))
    command = [
        sys.executable,
        str(runner),
        mode,
        "--server",
        server,
        "--prompt-file",
        str(prompt_file),
        "--width",
        str(int(clip.get("width", DEFAULT_WIDTH))),
        "--height",
        str(int(clip.get("height", DEFAULT_HEIGHT))),
        "--duration",
        str(float(clip.get("duration", DEFAULT_DURATION))),
        "--steps",
        str(int(clip.get("steps", DEFAULT_STEPS))),
        "--prefix",
        str(clip.get("prefix")),
        "--output-dir",
        str(output_dir),
        "--poll",
        str(float(clip.get("poll", 10))),
        "--timeout",
        str(float(clip.get("timeout", DEFAULT_TIMEOUT))),
    ]
    if clip.get("seed") is not None:
        command.extend(["--seed", str(int(clip["seed"]))])
    if as_bool(clip.get("turbo"), True):
        command.append("--turbo")
    if as_bool(clip.get("turbo_low_vram"), True):
        command.append("--turbo-low-vram")
    if as_bool(clip.get("no_audio"), True):
        command.append("--no-audio")
    if as_bool(clip.get("overwrite_upload"), True):
        command.append("--overwrite-upload")
    if clip.get("turbo_strength") is not None:
        command.extend(["--turbo-strength", str(float(clip["turbo_strength"]))])
    if clip.get("turbo_lora"):
        command.extend(["--turbo-lora", str(clip["turbo_lora"])])
    if clip.get("ref_image_size"):
        command.extend(["--ref-image-size", str(clip["ref_image_size"])])
    if first_frame:
        command.extend(["--first-frame", str(first_frame)])
    if last_frame:
        command.extend(["--last-frame", str(last_frame)])
    for ref in ref_images:
        command.extend(["--ref-image", str(ref)])
    return command


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")


def command_run(args: argparse.Namespace) -> int:
    config_path = Path(args.sequence).resolve()
    config = load_config(config_path)
    base_dir = config_path.parent
    sequence_id = slug(str(config.get("sequence_id") or config_path.stem))
    run_id = slug(args.run_id or now_id())
    run_dir = (Path(args.output_root) / sequence_id / run_id).resolve()
    run_dir.mkdir(parents=True, exist_ok=True)

    runner = Path(args.runner).resolve() if args.runner else Path(__file__).with_name("h3_runner.py").resolve()
    if not runner.exists():
        raise SequenceError(f"h3_runner.py not found: {runner}")

    defaults = {
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
        "timeout": DEFAULT_TIMEOUT,
    }
    defaults.update(config.get("defaults") or {})

    raw_clips = config.get("clips") or []
    if not isinstance(raw_clips, list) or not raw_clips:
        raise SequenceError("Sequence config needs a non-empty `clips` list")

    server = args.server or str(config.get("server") or DEFAULT_SERVER)
    manifest: dict[str, Any] = {
        "sequence_id": sequence_id,
        "run_id": run_id,
        "config_path": str(config_path),
        "server": server,
        "started_at": dt.datetime.now().isoformat(timespec="seconds"),
        "run_dir": str(run_dir),
        "clips": [],
        "final_video": None,
    }
    manifest_path = run_dir / "sequence-manifest.json"
    write_json(manifest_path, manifest)

    ffmpeg = ffmpeg_bin(args.ffmpeg) if not args.dry_run else (args.ffmpeg or "ffmpeg")
    videos: list[Path] = []
    previous_last_frame: Path | None = None

    for index, raw_clip in enumerate(raw_clips, start=1):
        if not isinstance(raw_clip, dict):
            raise SequenceError(f"Clip #{index} must be an object")
        clip = merge_dict(defaults, raw_clip)
        clip_id = slug(str(clip.get("id") or clip.get("name") or f"clip-{index:02d}"))
        clip.setdefault("prefix", f"sequence/{sequence_id}/{run_id}/{clip_id}")
        clip_dir = run_dir / clip_id
        clip_dir.mkdir(parents=True, exist_ok=True)

        prompt_text = read_prompt(clip, base_dir)
        prompt_file = clip_dir / "prompt.txt"
        prompt_file.write_text(prompt_text + "\n", encoding="utf-8", newline="\n")

        refs = [rel_path(str(path), base_dir) for path in (clip.get("ref_images") or [])]
        if previous_last_frame and as_bool(clip.get("use_previous_last_frame_as_ref"), False):
            refs.insert(0, previous_last_frame)

        first_frame = rel_path(str(clip["first_frame"]), base_dir) if clip.get("first_frame") else None
        last_frame = rel_path(str(clip["last_frame"]), base_dir) if clip.get("last_frame") else None
        if previous_last_frame and as_bool(clip.get("use_previous_last_frame_as_first_frame"), False):
            first_frame = previous_last_frame

        inputs_to_check = refs[:]
        if first_frame:
            inputs_to_check.append(first_frame)
        if last_frame:
            inputs_to_check.append(last_frame)
        require_files(inputs_to_check)

        write_json(
            clip_dir / "clip-config.json",
            {
                "clip": clip,
                "prompt_file": str(prompt_file),
                "ref_images": [str(path) for path in refs],
                "first_frame": str(first_frame) if first_frame else None,
                "last_frame": str(last_frame) if last_frame else None,
            },
        )

        existing = find_existing_video(clip_dir) if args.resume else None
        if existing:
            print(f"[sequence] resume {clip_id}: {existing}", flush=True)
            local_video = existing
            seconds = 0.0
            status = "resumed"
        else:
            command = build_h3_command(runner, server, clip, prompt_file, clip_dir, refs, first_frame, last_frame)
            print(f"[sequence] running {clip_id}: {clip.get('width')}x{clip.get('height')} {clip.get('duration')}s", flush=True)
            if args.dry_run:
                print(" ".join(command), flush=True)
                local_video = clip_dir / f"{clip_id}.dry-run.mp4"
                seconds = 0.0
                status = "dry-run"
            else:
                code, output, seconds = run_streamed(command, clip_dir / "runner.log", timeout=float(clip.get("timeout", DEFAULT_TIMEOUT)) + 900)
                if code != 0:
                    raise SequenceError(f"Clip {clip_id} failed with exit code {code}. See {clip_dir / 'runner.log'}")
                parsed = parse_downloaded_path(output)
                local_video = parsed if parsed and parsed.exists() else find_existing_video(clip_dir)
                if not local_video:
                    raise SequenceError(f"Clip {clip_id} finished but no video was found in {clip_dir}")
                status = "success"

        last_frame = None
        if not args.dry_run and as_bool(clip.get("extract_last_frame"), True):
            last_frame = clip_dir / "last-frame.png"
            extract_last_frame(ffmpeg, local_video, last_frame)
            previous_last_frame = last_frame
        elif not args.dry_run:
            previous_last_frame = None

        videos.append(local_video)
        manifest["clips"].append(
            {
                "id": clip_id,
                "status": status,
                "seconds": round(seconds, 2),
                "video": str(local_video),
                "last_frame": str(last_frame) if last_frame else None,
            }
        )
        write_json(manifest_path, manifest)

    if args.no_concat or args.dry_run:
        write_json(manifest_path, manifest)
        print(f"[sequence] manifest: {manifest_path}", flush=True)
        return 0

    final_options = config.get("final") or {}
    final_name = str(final_options.get("filename") or f"{sequence_id}_{run_id}_final.mp4")
    final_path = run_dir / final_name
    concat_mode = str(args.concat_mode or final_options.get("concat_mode") or "both")
    final_video = concat_videos(ffmpeg, videos, run_dir, final_path, final_options, concat_mode)
    manifest["final_video"] = str(final_video)
    manifest["finished_at"] = dt.datetime.now().isoformat(timespec="seconds")
    write_json(manifest_path, manifest)
    print(f"[sequence] final video: {final_video}", flush=True)
    print(f"[sequence] manifest: {manifest_path}", flush=True)
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run and stitch a MiniMax H3 multi-clip sequence")
    parser.add_argument("run", choices=["run"], help="Run the sequence")
    parser.add_argument("--sequence", required=True, help="Path to sequence JSON")
    parser.add_argument("--server", default=None, help="ComfyUI API URL, overrides config")
    parser.add_argument("--output-root", default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--runner", default=None, help="Path to h3_runner.py")
    parser.add_argument("--ffmpeg", default=None)
    parser.add_argument("--concat-mode", choices=["copy", "reencode", "both"], default=None)
    parser.add_argument("--resume", action="store_true", help="Reuse existing clip videos in the run directory")
    parser.add_argument("--no-concat", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        return command_run(args)
    except KeyboardInterrupt:
        return 130
    except SequenceError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
