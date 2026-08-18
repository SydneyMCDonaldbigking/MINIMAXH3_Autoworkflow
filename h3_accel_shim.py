#!/usr/bin/env python3
"""
Stand in for h3_runner.py so a whole sequence renders with acceleration on.

`h3_sequence_runner.py` already takes `--runner`, so it can be pointed at any
script with h3_runner's command line. What it does not do is forward extra
flags: `build_h3_command` emits mode, size, steps, seed, turbo and the
references, and nothing else. Pointing `--runner` straight at
`h3_accel_runner.py` therefore runs the accelerated runner *without* `--accel`,
which produces a perfectly normal-looking clip at exactly baseline speed. That
is the same class of silent no-op as the sigma shift that was already running at
its default: the measurement comes back honest and means nothing.

So this shim appends the acceleration flags and delegates. Neither
`h3_runner.py` nor `h3_sequence_runner.py` is touched, which is the point: they
produce the ads and must keep working.

    python h3_sequence_runner.py run \
      --sequence sequences/whatever.json \
      --runner h3_accel_shim.py \
      --output-root sequence_outputs --run-id whatever_sage

Sol-Attn is off by default because `SolAttnPatch` from ComfyUI-SolAttn_triton is
not installed on the machines we rent, and `JR_H3_UnifiedAcceleration` raises at
execution time when it is missing rather than falling back. Set H3_ACCEL_SOL=1
once that node is actually present.

Measured 2026-08-18 on an H100 NVL, single clip, model warm: 361 s without,
320 s with, -11.4%, mean per-pixel difference 5-9 of 255 between the two takes.
See local_artifacts/h3_accel_AD/results.md.

Acceleration changes numerics. A sequence rendered through this shim will not be
pixel-identical to the same sequence and seeds rendered through h3_runner.py.
"""

from __future__ import annotations

import os
import sys

import h3_accel_runner


def extra_flags() -> list[str]:
    flags = ["--accel"]
    if os.environ.get("H3_ACCEL_SOL", "0") not in ("1", "true", "yes"):
        flags += ["--accel-set", "enable_sol_attn=false"]
    for override in filter(None, os.environ.get("H3_ACCEL_SET", "").split(",")):
        flags += ["--accel-set", override.strip()]
    return flags


def main(argv: list[str]) -> int:
    flags = extra_flags()
    print("[accel-shim] appending " + " ".join(flags))
    return h3_accel_runner.main(list(argv) + flags)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
