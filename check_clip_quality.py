#!/usr/bin/env python3
"""
Technical QC gate for generated MiniMax H3 clips.

Two failure modes have actually bitten this project, and both are invisible in a
still frame:

1. Dead output. A NaN latent decodes to a constant frame. The file plays, has the
   right duration and frame count, and is uniformly black.
2. Camera jitter. Individual frames are sharp, but the framing oscillates
   frame to frame. Played back it reads as mush. Measured on 2026-08-10, a clip
   judged bad had 33.6% of frames reversing direction (45% in its last third),
   while a clip judged good had 15.6% overall and settled to 7.5% by the end.

Sharpness is deliberately not a gate. The bad beef clip measured sharper per
frame than the good egg tart clip, so it does not separate the cases.

Usage:
  python check_clip_quality.py clip.mp4
  python check_clip_quality.py outputs/server_reviews/*/clip*.mp4
  python check_clip_quality.py clip.mp4 --max-flip-rate 20 --json

Exit code is 0 when every clip passes, 1 when any clip fails, 2 on a tool error.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

# Thresholds come from the 2026-08-10 measurements described above. A good clip
# sat at 15.6% overall, a bad one at 33.6%, so 20% separates them with margin.
DEFAULT_MAX_FLIP_RATE = 20.0
DEFAULT_MAX_TAIL_FLIP_RATE = 25.0
# A constant frame has zero variation. Real content measured 235-244.
CONSTANT_FRAME_EPSILON = 1.0


class ProbeError(RuntimeError):
    pass


def run(args: list[str], timeout: float = 900, cwd: str | None = None) -> str:
    try:
        proc = subprocess.run(args, capture_output=True, text=True,
                              timeout=timeout, cwd=cwd)
    except FileNotFoundError as exc:
        raise ProbeError(f"missing tool: {exc}") from exc
    except subprocess.TimeoutExpired as exc:
        raise ProbeError(f"timed out: {' '.join(args[:3])}") from exc
    return proc.stdout + proc.stderr


def measure_luma(path: Path) -> dict[str, float]:
    """Detect the constant-frame (NaN latent) signature."""
    out = run([
        "ffprobe", "-v", "error", "-f", "lavfi",
        "-i", f"movie={path.as_posix()},signalstats",
        "-show_entries",
        "frame_tags=lavfi.signalstats.YMIN,lavfi.signalstats.YMAX,lavfi.signalstats.YAVG",
        "-of", "json",
    ])
    try:
        frames = json.loads(out[out.index("{"):]).get("frames", [])
    except (ValueError, json.JSONDecodeError) as exc:
        raise ProbeError(f"could not read luma stats: {exc}") from exc

    rows = []
    for frame in frames:
        tags = frame.get("tags", {})
        try:
            rows.append((
                float(tags["lavfi.signalstats.YMIN"]),
                float(tags["lavfi.signalstats.YMAX"]),
                float(tags["lavfi.signalstats.YAVG"]),
            ))
        except (KeyError, ValueError):
            continue
    if not rows:
        raise ProbeError("no frames analysed")

    avgs = [yavg for _, _, yavg in rows]
    return {
        "frames": float(len(rows)),
        "within_frame_range": max(ymax - ymin for ymin, ymax, _ in rows),
        "across_frame_range": max(avgs) - min(avgs),
    }


def frame_motion(path: Path) -> list[tuple[int, int]]:
    """Per-frame global motion, as the median of vidstabdetect's local vectors."""
    with tempfile.TemporaryDirectory() as tmp:
        trf = Path(tmp) / "motion.trf"
        # The result path goes in as a bare relative name with ffmpeg running in
        # the temp directory: filter options are colon-separated, so a Windows
        # absolute path like C:/... would be parsed as an option boundary.
        run([
            "ffmpeg", "-y", "-loglevel", "error", "-i", str(path.resolve()),
            "-vf", "vidstabdetect=shakiness=10:accuracy=15:result=motion.trf",
            "-f", "null", "-",
        ], cwd=tmp)
        if not trf.exists():
            raise ProbeError("vidstabdetect produced no result file")
        text = trf.read_text(encoding="utf-8", errors="replace")

    motion: list[tuple[int, int]] = []
    for block in re.split(r"\nFrame \d+ ", text)[1:]:
        vectors = re.findall(r"\(LM (-?\d+) (-?\d+) ", block)
        if not vectors:
            continue
        motion.append((
            int(statistics.median(int(dx) for dx, _ in vectors)),
            int(statistics.median(int(dy) for _, dy in vectors)),
        ))
    if len(motion) < 6:
        raise ProbeError("too few motion samples")
    return motion


def stability(motion: list[tuple[int, int]]) -> dict[str, float]:
    xs = [dx for dx, _ in motion]
    ys = [dy for _, dy in motion]
    pairs = len(xs) - 1
    # A direction reversal is the signature of vibration. A deliberate camera
    # move keeps its sign and changes magnitude smoothly.
    flips = sum(1 for i in range(pairs) if xs[i] * xs[i + 1] < 0)
    jerk_x = statistics.mean(abs(xs[i + 1] - xs[i]) for i in range(pairs))
    jerk_y = statistics.mean(abs(ys[i + 1] - ys[i]) for i in range(pairs))
    return {
        "flip_rate": 100.0 * flips / pairs,
        "motion_x": statistics.mean(abs(v) for v in xs),
        "motion_y": statistics.mean(abs(v) for v in ys),
        "jerk_x": jerk_x,
        "jerk_y": jerk_y,
    }


def analyse(path: Path, max_flip: float, max_tail_flip: float) -> dict[str, Any]:
    result: dict[str, Any] = {"file": str(path), "failures": []}

    luma = measure_luma(path)
    result["luma"] = luma
    if (luma["within_frame_range"] < CONSTANT_FRAME_EPSILON
            and luma["across_frame_range"] < CONSTANT_FRAME_EPSILON):
        result["failures"].append("constant frame - NaN latent, the clip is dead")
        result["passed"] = False
        return result

    motion = frame_motion(path)
    result["overall"] = stability(motion)

    third = len(motion) // 3
    names = ["head", "middle", "tail"]
    spans = [motion[:third], motion[third:2 * third], motion[2 * third:]]
    result["thirds"] = {n: stability(s) for n, s in zip(names, spans) if len(s) > 5}

    if result["overall"]["flip_rate"] > max_flip:
        result["failures"].append(
            f"camera jitter: {result['overall']['flip_rate']:.1f}% of frames reverse "
            f"direction (limit {max_flip:.0f}%)")

    tail = result["thirds"].get("tail")
    if tail and tail["flip_rate"] > max_tail_flip:
        result["failures"].append(
            f"tail jitter: last third at {tail['flip_rate']:.1f}% reversals "
            f"(limit {max_tail_flip:.0f}%) - the closing beat probably has no "
            f"directional action to perform")

    result["passed"] = not result["failures"]
    return result


def report(result: dict[str, Any]) -> None:
    status = "PASS" if result["passed"] else "FAIL"
    print(f"\n[{status}] {result['file']}")

    luma = result["luma"]
    print(f"  frames={int(luma['frames'])}  within-frame Y range="
          f"{luma['within_frame_range']:.2f}  across-frame YAVG range="
          f"{luma['across_frame_range']:.2f}")

    overall = result.get("overall")
    if overall:
        print(f"  camera: flip rate={overall['flip_rate']:.1f}%  "
              f"motion=({overall['motion_x']:.1f},{overall['motion_y']:.1f})px  "
              f"jerk=({overall['jerk_x']:.2f},{overall['jerk_y']:.2f})px/frame")
        for name, stats in result.get("thirds", {}).items():
            print(f"    {name:6} flips={stats['flip_rate']:5.1f}%  "
                  f"motion=({stats['motion_x']:4.1f},{stats['motion_y']:4.1f})")

    for failure in result["failures"]:
        print(f"  ! {failure}")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Technical QC gate for generated MiniMax H3 clips.")
    parser.add_argument("clips", nargs="+", help="video files to check")
    parser.add_argument("--max-flip-rate", type=float, default=DEFAULT_MAX_FLIP_RATE,
                        help="max %% of frames reversing direction, overall")
    parser.add_argument("--max-tail-flip-rate", type=float,
                        default=DEFAULT_MAX_TAIL_FLIP_RATE,
                        help="max %% of frames reversing direction in the last third")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of text")
    args = parser.parse_args(argv)

    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            print(f"ERROR: {tool} not found on PATH", file=sys.stderr)
            return 2

    results = []
    for raw in args.clips:
        path = Path(raw)
        if not path.is_file():
            print(f"ERROR: not a file: {path}", file=sys.stderr)
            return 2
        try:
            results.append(analyse(path, args.max_flip_rate, args.max_tail_flip_rate))
        except ProbeError as exc:
            print(f"ERROR: {path}: {exc}", file=sys.stderr)
            return 2

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        for result in results:
            report(result)
        failed = [r for r in results if not r["passed"]]
        print(f"\n{len(results) - len(failed)}/{len(results)} passed")

    return 1 if any(not r["passed"] for r in results) else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except KeyboardInterrupt:
        raise SystemExit(130)
