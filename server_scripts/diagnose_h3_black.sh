#!/usr/bin/env bash
set -uo pipefail

# Diagnose MiniMax-H3 black-video output (constant-luma frames caused by NaN
# latents). Runs a cheap-to-expensive probe ladder and stops as soon as a stage
# is decisive, so a dead GPU is found before spending A100 minutes on renders.
#
# Ladder:
#   1 environment snapshot      free
#   2 GPU health (ECC / Xid)    free
#   3 torch numeric sanity      seconds
#   4 model file integrity      ~1 min
#   5 tiny T2V 512x512          ~1 min
#   6 native T2V 1088x1920      ~8 min   (only if 5 is clean)
#   7 native R2V 1088x1920      ~9 min   (only if 6 is clean)
#
# Optional env:
#   COMFYUI_DIR=/root/ComfyUI
#   CONDA_ENV=comfy_h3_torch29_cu126
#   PORT=8189
#   MODELS_DIR=$COMFYUI_DIR/models
#   NATIVE_WIDTH=1088
#   NATIVE_HEIGHT=1920
#   MAX_STAGE=7          stop after this stage
#   FORCE_ALL=0          1 = keep going even after a decisive failure
#   REPORT=<path>        defaults to $COMFYUI_DIR/h3_black_diagnostic_<ts>.log

COMFYUI_DIR="${COMFYUI_DIR:-/root/ComfyUI}"
CONDA_ENV="${CONDA_ENV:-comfy_h3_torch29_cu126}"
CONDA_SH="${CONDA_SH:-/home/node/anaconda3/etc/profile.d/conda.sh}"
ENV_PYTHON="${ENV_PYTHON:-/home/node/anaconda3/envs/$CONDA_ENV/bin/python}"
PORT="${PORT:-8189}"
MODELS_DIR="${MODELS_DIR:-$COMFYUI_DIR/models}"
NATIVE_WIDTH="${NATIVE_WIDTH:-1088}"
NATIVE_HEIGHT="${NATIVE_HEIGHT:-1920}"
MAX_STAGE="${MAX_STAGE:-7}"
FORCE_ALL="${FORCE_ALL:-0}"
TS="$(date +%Y%m%d_%H%M%S)"
REPORT="${REPORT:-$COMFYUI_DIR/h3_black_diagnostic_${TS}.log}"
PROBE_DIR="$COMFYUI_DIR/test_outputs/black_diag_${TS}"

VERDICTS=()
DECISIVE=""

note()    { echo "[$(date +%H:%M:%S)] $*"; }
banner()  { echo; echo "=================================================================="; echo "  $*"; echo "=================================================================="; }
verdict() { VERDICTS+=("$1|$2"); note "VERDICT($1): $2"; }

# Mark a root cause as found. Later generation stages are skipped unless
# FORCE_ALL=1, because they cost GPU time and cannot change the conclusion.
decisive() {
  DECISIVE="$1"
  if [ "$FORCE_ALL" != "1" ]; then
    note "Decisive result reached; skipping remaining stages (FORCE_ALL=1 to override)."
  fi
}

should_run() {
  local stage="$1"
  [ "$stage" -le "$MAX_STAGE" ] || return 1
  [ -z "$DECISIVE" ] || [ "$FORCE_ALL" = "1" ]
}

activate_python() {
  # A non-interactive ssh shell does not have conda on PATH, so source the
  # profile script by explicit path before falling back to PATH lookup.
  if [ -f "$CONDA_SH" ]; then
    # shellcheck disable=SC1091
    source "$CONDA_SH"
    conda activate "$CONDA_ENV" || note "WARNING: conda activate $CONDA_ENV failed"
  elif command -v conda >/dev/null 2>&1; then
    # shellcheck disable=SC1091
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate "$CONDA_ENV" || note "WARNING: conda activate $CONDA_ENV failed"
  elif [ -f "$COMFYUI_DIR/venv/bin/activate" ]; then
    # shellcheck disable=SC1091
    source "$COMFYUI_DIR/venv/bin/activate"
  fi

  if ! command -v python >/dev/null 2>&1; then
    if [ -x "$ENV_PYTHON" ]; then
      note "conda activation did not put python on PATH; using $ENV_PYTHON"
      PATH="$(dirname "$ENV_PYTHON"):$PATH"
      export PATH
    else
      note "WARNING: no python on PATH and $ENV_PYTHON is missing"
    fi
  fi
  note "python in use: $(command -v python || echo none)"
}

# ---------------------------------------------------------------- stage 1 ----
stage_env() {
  banner "STAGE 1  Environment snapshot"

  if command -v nvidia-smi >/dev/null 2>&1; then
    nvidia-smi
    echo
    nvidia-smi --query-gpu=name,driver_version,memory.total,memory.used,temperature.gpu,clocks_throttle_reasons.active \
      --format=csv 2>/dev/null || true
  else
    verdict "stage1" "nvidia-smi missing - driver not visible in this container"
    decisive "no-driver"
    return
  fi

  echo
  note "Disk usage (a full disk can truncate model downloads and outputs):"
  df -h "$COMFYUI_DIR" "$MODELS_DIR" 2>/dev/null || df -h

  local avail
  avail="$(df -Pk "$COMFYUI_DIR" 2>/dev/null | awk 'NR==2{print $4}')"
  if [ -n "$avail" ] && [ "$avail" -lt 5242880 ]; then
    verdict "stage1" "less than 5 GB free on $COMFYUI_DIR - suspect truncated weights or outputs"
  fi

  echo
  note "Python / torch:"
  python - <<'PY'
import sys
print("python  :", sys.version.split()[0])
try:
    import torch
    print("torch   :", torch.__version__)
    print("cuda    :", torch.version.cuda)
    print("avail   :", torch.cuda.is_available())
    if torch.cuda.is_available():
        print("device  :", torch.cuda.get_device_name(0))
        print("capab   :", torch.cuda.get_device_capability(0))
except Exception as exc:
    print("torch import FAILED:", exc)
PY

  echo
  note "ComfyUI API on port $PORT:"
  if curl -fsS "http://127.0.0.1:${PORT}/system_stats" 2>/dev/null; then
    echo
  else
    note "ComfyUI is not responding on port $PORT (generation stages will be skipped)"
  fi
}

# ---------------------------------------------------------------- stage 2 ----
stage_gpu_health() {
  banner "STAGE 2  GPU health - ECC, retired pages, Xid"

  local ecc_bad=0

  note "ECC error counters:"
  nvidia-smi --query-gpu=ecc.errors.uncorrected.volatile.total,ecc.errors.uncorrected.aggregate.total,retired_pages.pending \
    --format=csv 2>/dev/null || note "(ECC query unsupported on this GPU/driver)"

  local unc
  unc="$(nvidia-smi --query-gpu=ecc.errors.uncorrected.aggregate.total --format=csv,noheader,nounits 2>/dev/null | head -1 | tr -d ' ')"
  if [ -n "$unc" ] && [ "$unc" != "N/A" ] && [ "$unc" != "0" ] && [ "$unc" != "[NotSupported]" ]; then
    ecc_bad=1
    verdict "stage2" "uncorrected ECC errors = $unc - GPU memory is faulty"
  fi

  echo
  note "Retired / remapped pages:"
  nvidia-smi -q 2>/dev/null | grep -iA6 -E "retired pages|remapped rows" | head -40 || true

  # Retired Pages is a pre-Ampere field. On A100 and newer it reports N/A and
  # the real signal is Remapped Rows, so only treat "Yes" or a positive count
  # as a fault and ignore N/A / [N/A] / Not Supported.
  local pending
  pending="$(nvidia-smi --query-gpu=retired_pages.pending --format=csv,noheader,nounits 2>/dev/null | head -1 | tr -d ' ')"
  if [ "$pending" = "Yes" ] || printf '%s' "$pending" | grep -qE '^[1-9][0-9]*$'; then
    ecc_bad=1
    verdict "stage2" "retired pages pending = $pending - GPU memory is being retired"
  fi

  local remap_unc
  remap_unc="$(nvidia-smi -q 2>/dev/null | awk '/Remapped Rows/,/Bank Remap/' | grep -i "uncorrectable" | head -1 | sed 's/.*: *//' | tr -d ' ')"
  if printf '%s' "$remap_unc" | grep -qE '^[1-9][0-9]*$'; then
    ecc_bad=1
    verdict "stage2" "$remap_unc uncorrectable remapped rows - GPU memory is degrading"
  fi

  if nvidia-smi -q 2>/dev/null | grep -iE "remapping failure occurred *: *yes" >/dev/null; then
    ecc_bad=1
    verdict "stage2" "row remapping failure - GPU needs a reset or replacement"
  fi

  echo
  note "Xid errors in kernel log (needs privileges; empty output is good):"
  { dmesg 2>/dev/null || cat /var/log/kern.log 2>/dev/null; } | grep -iE "xid|nvrm" | tail -20 || true

  if { dmesg 2>/dev/null || true; } | grep -iE "Xid.*(13|31|43|48|63|64|74|79|92|94|95)" >/dev/null; then
    ecc_bad=1
    verdict "stage2" "NVIDIA Xid fault found in kernel log - hardware or driver level fault"
  fi

  if [ "$ecc_bad" = "1" ]; then
    decisive "gpu-hardware"
  else
    verdict "stage2" "no ECC/Xid evidence of hardware fault"
  fi
}

# ---------------------------------------------------------------- stage 3 ----
stage_torch_numeric() {
  banner "STAGE 3  Torch numeric sanity - does this GPU still do float math"

  python - <<'PY'
import sys
try:
    import torch
except Exception as exc:
    print("torch import FAILED:", exc); sys.exit(3)

if not torch.cuda.is_available():
    print("CUDA not available"); sys.exit(3)

torch.manual_seed(0)
bad = []

# 1. Matmul in each dtype the H3 graph touches.
for name, dt in (("fp32", torch.float32), ("fp16", torch.float16), ("bf16", torch.bfloat16)):
    try:
        a = torch.randn(4096, 4096, device="cuda", dtype=dt)
        b = a @ a
        torch.cuda.synchronize()
        n = bool(b.isnan().any()); i = bool(b.isinf().any())
        print(f"{name} matmul : nan={n} inf={i} absmax={b.abs().max().item():.4g}")
        if n or i:
            bad.append(f"{name} matmul produced nan/inf")
    except Exception as exc:
        print(f"{name} matmul : FAILED {exc}")
        bad.append(f"{name} matmul raised {exc}")

# 2. VRAM write/read integrity sweep over most of free memory.
try:
    free, total = torch.cuda.mem_get_info()
    budget = int(free * 0.7)
    chunk = 512 * 1024 * 1024
    n_chunks = max(1, budget // chunk)
    print(f"vram sweep : {n_chunks} x 512MB over {free/2**30:.1f} GB free")
    held, errors = [], 0
    for k in range(n_chunks):
        t = torch.full((chunk // 4,), float(k + 1), device="cuda", dtype=torch.float32)
        held.append(t)
    torch.cuda.synchronize()
    for k, t in enumerate(held):
        if not bool((t == float(k + 1)).all()):
            errors += 1
    print(f"vram sweep : mismatched chunks = {errors}")
    if errors:
        bad.append(f"{errors} VRAM chunks read back wrong - bad video memory")
    del held
    torch.cuda.empty_cache()
except torch.cuda.OutOfMemoryError:
    # Another process (usually ComfyUI) holds the card. Not a hardware fault.
    print("vram sweep : SKIPPED - GPU is busy, not enough free VRAM to sweep")
except Exception as exc:
    print("vram sweep : FAILED", exc)
    bad.append(f"VRAM sweep raised {exc}")

# 3. Attention-shaped softmax, the usual first place a sick GPU shows NaN.
try:
    q = torch.randn(8, 4096, 128, device="cuda", dtype=torch.float16)
    o = torch.nn.functional.scaled_dot_product_attention(q, q, q)
    torch.cuda.synchronize()
    n = bool(o.isnan().any())
    print(f"sdpa fp16  : nan={n} absmax={o.abs().max().item():.4g}")
    if n:
        bad.append("scaled_dot_product_attention produced nan")
except torch.cuda.OutOfMemoryError:
    print("sdpa fp16  : SKIPPED - GPU is busy")
except Exception as exc:
    print("sdpa fp16  : FAILED", exc)
    bad.append(f"sdpa raised {exc}")

print()
if bad:
    print("NUMERIC FAULT:")
    for b in bad:
        print(" -", b)
    sys.exit(1)
print("All numeric checks clean.")
PY

  local rc=$?
  if [ "$rc" = "1" ]; then
    verdict "stage3" "raw torch math already produces NaN or corrupt memory - the GPU is the cause, not ComfyUI"
    decisive "gpu-numeric"
  elif [ "$rc" = "3" ]; then
    verdict "stage3" "torch/CUDA unusable in env $CONDA_ENV"
    decisive "torch-broken"
  else
    verdict "stage3" "raw torch math is clean - GPU arithmetic is healthy"
  fi
}

# ---------------------------------------------------------------- stage 4 ----
stage_model_integrity() {
  banner "STAGE 4  Model file integrity"

  MODELS_DIR="$MODELS_DIR" python - <<'PY'
import os, sys, pathlib

models = pathlib.Path(os.environ["MODELS_DIR"])
targets = [
    "diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors",
    "diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors",
    "text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors",
    "vae/minimax_h3_video_vae_fp16.safetensors",
    "vae/minimax_h3_audio_vae_fp32.safetensors",
    "loras/minimax_h3_turbo_v4_step600_ema.safetensors",
]

try:
    from safetensors import safe_open
except Exception as exc:
    print("safetensors unavailable:", exc); sys.exit(3)

import torch

bad = []
for rel in targets:
    path = models / rel
    if not path.exists():
        print(f"MISSING  {rel}")
        if "loras/" not in rel:
            bad.append(f"missing {rel}")
        continue

    size = path.stat().st_size
    try:
        with safe_open(str(path), framework="pt", device="cpu") as f:
            keys = list(f.keys())
            # Sample across the file: first, middle and last tensors.
            picks = {keys[0], keys[len(keys) // 2], keys[-1]} if keys else set()
            flags = []
            for k in sorted(picks):
                t = f.get_tensor(k)
                if t.dtype.is_floating_point:
                    # isnan/isinf are not implemented for float8 dtypes, so
                    # promote to float32 before testing.
                    probe = t.float() if t.dtype not in (torch.float32, torch.float64) else t
                    nan = bool(probe.isnan().any()); inf = bool(probe.isinf().any())
                    zero = bool((probe == 0).all())
                    flags.append(f"{k}:{tuple(t.shape)}:{t.dtype}"
                                 f"{' NAN' if nan else ''}{' INF' if inf else ''}{' ALLZERO' if zero else ''}")
                    if nan or inf:
                        bad.append(f"{rel} tensor {k} contains nan/inf")
                else:
                    zero = bool((t == 0).all())
                    flags.append(f"{k}:{tuple(t.shape)}:{t.dtype}{' ALLZERO' if zero else ''}")
                # An all-zero tensor is reported for information only. Zeroed
                # mask tokens and unused bias rows are normal in these files,
                # so it is far too weak on its own to call a file corrupt.
            print(f"OK       {rel}  {size/2**30:.2f} GB  {len(keys)} tensors")
            for fl in flags:
                print(f"           {fl}")
    except Exception as exc:
        print(f"CORRUPT  {rel}  {size/2**30:.2f} GB  -> {exc}")
        bad.append(f"{rel} failed to open: {exc}")

print()
if bad:
    print("WEIGHT FAULT:")
    for b in bad:
        print(" -", b)
    sys.exit(1)
print("Sampled weights are readable and finite.")
PY

  local rc=$?
  if [ "$rc" = "1" ]; then
    verdict "stage4" "model weights are corrupt or contain NaN - re-download the affected file"
    decisive "weights-corrupt"
  elif [ "$rc" = "3" ]; then
    verdict "stage4" "could not check weights (safetensors missing)"
  else
    verdict "stage4" "sampled model weights are clean"
  fi
}

# ------------------------------------------------------------ video check ----
# Returns 0 when the clip has real picture variation, 1 when it is a constant
# frame (the NaN signature), 2 when it could not be checked.
check_video() {
  local path="$1"
  if ! command -v ffprobe >/dev/null 2>&1; then
    note "ffprobe missing - falling back to file size only: $(du -h "$path" | cut -f1)"
    return 2
  fi

  VIDEO_PATH="$path" python - <<'PY'
import json, os, subprocess, sys

path = os.environ["VIDEO_PATH"]
# Read tags by key from JSON: ffprobe emits frame tags in its own internal
# order (YMIN, YAVG, YMAX), not the order they were requested in.
cmd = [
    "ffprobe", "-v", "error", "-f", "lavfi",
    "-i", f"movie={path},signalstats",
    "-show_entries", "frame_tags=lavfi.signalstats.YMIN,lavfi.signalstats.YMAX,lavfi.signalstats.YAVG",
    "-of", "json",
]
try:
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=600).stdout
    frames = json.loads(out).get("frames", [])
except Exception as exc:
    print("ffprobe failed:", exc); sys.exit(2)

rows = []
for fr in frames:
    tags = fr.get("tags", {})
    try:
        rows.append((
            float(tags["lavfi.signalstats.YMIN"]),
            float(tags["lavfi.signalstats.YMAX"]),
            float(tags["lavfi.signalstats.YAVG"]),
        ))
    except (KeyError, ValueError):
        pass

if not rows:
    print("no frames analysed"); sys.exit(2)

spread = max(ymax - ymin for ymin, ymax, _ in rows)   # widest within-frame contrast
avgs = [yavg for _, _, yavg in rows]
motion = max(avgs) - min(avgs)                        # variation across frames

print(f"frames={len(rows)}  max within-frame Y range={spread:.2f}  "
      f"across-frame YAVG range={motion:.2f}  YAVG[0]={avgs[0]:.2f}")

if spread < 1.0 and motion < 1.0:
    print("RESULT: CONSTANT FRAME - NaN latent signature")
    sys.exit(1)
print("RESULT: real picture content")
PY
}

run_probe() {
  local label="$1"; shift
  note "Running probe: $label"
  mkdir -p "$PROBE_DIR"

  local log="$PROBE_DIR/${label}.log"
  if ! python "$COMFYUI_DIR/h3_runner.py" "$@" > "$log" 2>&1; then
    note "probe $label FAILED to generate:"
    tail -n 30 "$log"
    return 3
  fi

  local out
  out="$(grep -m1 '^Downloaded: ' "$log" | sed 's/^Downloaded: //')"
  if [ -z "$out" ] || [ ! -f "$out" ]; then
    note "probe $label produced no downloadable file; see $log"
    return 3
  fi

  note "probe $label output: $out"
  check_video "$out"
  return $?
}

preflight_generation() {
  if [ ! -f "$COMFYUI_DIR/h3_runner.py" ]; then
    verdict "stage5" "missing $COMFYUI_DIR/h3_runner.py - upload it before generation probes"
    return 1
  fi
  if ! curl -fsS "http://127.0.0.1:${PORT}/system_stats" >/dev/null 2>&1; then
    verdict "stage5" "ComfyUI not responding on port $PORT - start it before generation probes"
    return 1
  fi
  return 0
}

# ---------------------------------------------------------------- stage 5 ----
stage_tiny_t2v() {
  banner "STAGE 5  Tiny T2V 512x512, 4 steps, no turbo"
  preflight_generation || { decisive "no-comfy"; return; }

  run_probe "tiny_t2v" t2v \
    --server "http://127.0.0.1:${PORT}" \
    --prompt "a red apple on a wooden table, soft daylight" \
    --width 512 --height 512 --duration 0.5 --steps 4 \
    --seed 20260810 --no-audio \
    --prefix "black_diag/${TS}/tiny_t2v" \
    --output-dir "$PROBE_DIR"

  case $? in
    0) verdict "stage5" "tiny T2V has real content - the model stack works at small size" ;;
    1) verdict "stage5" "tiny T2V is already black - global failure, unrelated to resolution, refs or turbo"
       decisive "global-nan" ;;
    *) verdict "stage5" "tiny T2V could not be evaluated" ;;
  esac
}

# ---------------------------------------------------------------- stage 6 ----
stage_native_t2v() {
  banner "STAGE 6  Native T2V ${NATIVE_WIDTH}x${NATIVE_HEIGHT}, 4 steps, turbo"
  preflight_generation || return

  run_probe "native_t2v" t2v \
    --server "http://127.0.0.1:${PORT}" \
    --prompt "a steaming bowl of soup on a kitchen counter, slow push in, soft window light" \
    --width "$NATIVE_WIDTH" --height "$NATIVE_HEIGHT" --duration 5 --steps 4 \
    --seed 20260811 --turbo --turbo-low-vram --no-audio \
    --prefix "black_diag/${TS}/native_t2v" \
    --output-dir "$PROBE_DIR"

  case $? in
    0) verdict "stage6" "native T2V is clean - resolution and turbo are both fine" ;;
    1) verdict "stage6" "native T2V is black while tiny T2V was clean - failure is resolution/VRAM dependent"
       decisive "resolution-vram" ;;
    *) verdict "stage6" "native T2V could not be evaluated" ;;
  esac
}

# ---------------------------------------------------------------- stage 7 ----
stage_native_r2v() {
  banner "STAGE 7  Native R2V ${NATIVE_WIDTH}x${NATIVE_HEIGHT} with synthetic references"
  preflight_generation || return

  # Synthetic refs keep this stage independent of the production asset library.
  PROBE_DIR="$PROBE_DIR" NATIVE_WIDTH="$NATIVE_WIDTH" NATIVE_HEIGHT="$NATIVE_HEIGHT" python - <<'PY'
import os
from PIL import Image, ImageDraw

d = os.environ["PROBE_DIR"]
w, h = int(os.environ["NATIVE_WIDTH"]), int(os.environ["NATIVE_HEIGHT"])
os.makedirs(d, exist_ok=True)
for idx, base in enumerate([(180, 90, 60), (60, 120, 90), (110, 90, 160)], start=1):
    img = Image.new("RGB", (w, h), base)
    dr = ImageDraw.Draw(img)
    for y in range(0, h, 4):
        c = int(40 + 120 * y / h)
        dr.line([(0, y), (w, y)], fill=(base[0], c, base[2]))
    dr.ellipse((w * 0.2, h * 0.35, w * 0.8, h * 0.65), fill=(240, 200, 120))
    img.save(os.path.join(d, f"ref_{idx}.png"))
print("wrote 3 synthetic refs")
PY

  run_probe "native_r2v" r2v \
    --server "http://127.0.0.1:${PORT}" \
    --prompt "a chef lifts a lid, steam rises from the pot, slow handheld push in" \
    --ref-image "$PROBE_DIR/ref_1.png" \
    --ref-image "$PROBE_DIR/ref_2.png" \
    --ref-image "$PROBE_DIR/ref_3.png" \
    --width "$NATIVE_WIDTH" --height "$NATIVE_HEIGHT" --duration 5 --steps 4 \
    --seed 20260812 --turbo --turbo-low-vram --no-audio --overwrite-upload \
    --ref-image-size match \
    --prefix "black_diag/${TS}/native_r2v" \
    --output-dir "$PROBE_DIR"

  case $? in
    0) verdict "stage7" "native R2V with synthetic refs is clean - suspect the production reference assets or prompt files" ;;
    1) verdict "stage7" "native R2V is black while T2V is clean - the reference-conditioning path is the fault"
       decisive "r2v-path" ;;
    *) verdict "stage7" "native R2V could not be evaluated" ;;
  esac
}

# ------------------------------------------------------------------ report ---
summary() {
  banner "SUMMARY"
  for v in "${VERDICTS[@]+"${VERDICTS[@]}"}"; do
    echo "  ${v%%|*}: ${v#*|}"
  done

  echo
  echo "------------------------------------------------------------------"
  case "$DECISIVE" in
    gpu-hardware|gpu-numeric)
      cat <<'TXT'
ROOT CAUSE: the GPU itself is faulty.
  Rented A100s do degrade after hours of sustained load, and this reproduces
  outside ComfyUI entirely.
NEXT: ask the provider to migrate you to another physical GPU, or try
  `nvidia-smi -r` / a full instance reboot first.
  Do NOT re-rent purely for a CUDA 13 image - that would not fix this.
TXT
      ;;
    weights-corrupt)
      cat <<'TXT'
ROOT CAUSE: model weights on disk are damaged (likely a truncated or partly
  written download - check the disk usage in stage 1).
NEXT: delete and re-download the file named above with HF_ENDPOINT=https://hf-mirror.com,
  then rerun this script from stage 4.
TXT
      ;;
    global-nan)
      cat <<'TXT'
ROOT CAUSE: every generation is NaN, even 512x512 with turbo off, while raw
  torch math and the sampled weights are clean.
  This points at the runtime stack rather than the hardware: the quantized
  int8/nvfp4 kernels, the custom H3 nodes, or a ComfyUI/custom-node version skew.
NEXT: check the ComfyUI log for the first NaN line and for custom node import
  errors, and confirm the H3 node pack version matches the one that last worked.
TXT
      ;;
    resolution-vram)
      cat <<'TXT'
ROOT CAUSE: small renders are fine, native 1088x1920 is NaN.
  This is the offload/precision path under --lowvram at high token count.
NEXT: retry native size with turbo_low_vram off, then with --normalvram, then at
  1344x768. If only the largest size fails, treat it as a VRAM-pressure overflow
  and go back to the 720p-then-upscale route.
TXT
      ;;
    r2v-path)
      cat <<'TXT'
ROOT CAUSE: T2V is clean but R2V is NaN even with synthetic references.
  The fault is in MiniMaxH3ReferenceToVideo / the ref2va model, not your assets.
NEXT: verify the ref2va checkpoint separately and compare the H3 node pack
  version against the run that last produced good duck-soup clips.
TXT
      ;;
    torch-broken|no-driver|no-comfy)
      echo "BLOCKED: fix the environment problem listed above, then rerun."
      ;;
    "")
      cat <<'TXT'
No decisive failure was reproduced by this ladder.
  If the production sequences still come out black while these probes are clean,
  the difference is in the production assets, prompt files or sequence JSON -
  rerun one real clip and compare its ComfyUI log against a probe log.
TXT
      ;;
  esac
  echo "------------------------------------------------------------------"
  echo
  echo "Full report: $REPORT"
  echo "Probe files: $PROBE_DIR"
}

main() {
  note "MiniMax H3 black-video diagnostic"
  note "ComfyUI dir : $COMFYUI_DIR"
  note "Conda env   : $CONDA_ENV"
  note "Port        : $PORT"
  note "Report      : $REPORT"

  activate_python
  mkdir -p "$PROBE_DIR"

  should_run 1 && stage_env
  should_run 2 && stage_gpu_health
  should_run 3 && stage_torch_numeric
  should_run 4 && stage_model_integrity
  should_run 5 && stage_tiny_t2v
  should_run 6 && stage_native_t2v
  should_run 7 && stage_native_r2v

  summary
}

mkdir -p "$(dirname "$REPORT")" "$PROBE_DIR"
main "$@" 2>&1 | tee "$REPORT"
