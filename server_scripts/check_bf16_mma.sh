#!/usr/bin/env bash
set -uo pipefail

# GPU acceptance test. Run this before paying for a machine and before every
# production batch.
#
# It calls the Ampere BF16 tensor-core instruction directly and compares it
# against the FP16 instruction in the same kernel, so a failure cannot be blamed
# on PyTorch, cuBLAS, cuBLASLt, Triton or PTX JIT. The binary is compiled to a
# native sm_80 cubin, which cuobjdump verifies before the test runs.
#
# Background: on 2026-08-10 a rented A100 (driver 550.127.08) failed this at
# 1.91e-10 errors per MAC on bf16 while fp16 was perfectly clean over the same
# 2.1e11 MACs. MiniMax H3's Turbo LoRA runs in bfloat16, so the corruption
# reached the sampler as NaN and every clip decoded to a constant black frame.
# Two instances and five days of prompt debugging were lost to it.
#
# Optional env:
#   NVCC=/usr/local/cuda-12.4/bin/nvcc
#   ARCH=80          GPU compute capability without the dot: 80=A100, 90=H100
#   REPS=5

NVCC="${NVCC:-}"
ARCH="${ARCH:-80}"
REPS="${REPS:-5}"
SRC="$(dirname "$0")/bf16_mma_acceptance.cu"
BIN="/tmp/bf16_mma_acceptance"

if [ -z "$NVCC" ]; then
  NVCC="$(command -v nvcc 2>/dev/null || true)"
  [ -z "$NVCC" ] && NVCC="$(ls /usr/local/cuda*/bin/nvcc 2>/dev/null | head -1)"
fi
if [ -z "$NVCC" ] || [ ! -x "$NVCC" ]; then
  echo "ERROR: nvcc not found. Set NVCC=/path/to/nvcc." >&2
  exit 2
fi
if [ ! -f "$SRC" ]; then
  echo "ERROR: missing $SRC" >&2
  exit 2
fi

echo "== GPU identity (record this; you cannot compare cards later without it) =="
nvidia-smi --query-gpu=name,uuid,serial,pci.bus_id,driver_version --format=csv,noheader || true
nvidia-smi -q 2>/dev/null | grep -A1 -i "MIG Mode" | head -2 || true

echo
echo "== Building native sm_${ARCH} cubin =="
"$NVCC" "$SRC" -O3 -gencode "arch=compute_${ARCH},code=sm_${ARCH}" -o "$BIN" || exit 2

CUOBJ="$(dirname "$NVCC")/cuobjdump"
if [ -x "$CUOBJ" ]; then
  hmma="$("$CUOBJ" --dump-sass "$BIN" 2>/dev/null | grep -cE 'HMMA' || true)"
  echo "   SASS contains ${hmma} HMMA instructions (0 would mean tensor cores are not being used)"
fi

echo
echo "== Running (REPS=$REPS per dtype) =="
REPS="$REPS" "$BIN"
rc=$?

echo
if [ "$rc" = "0" ]; then
  echo "Read the two lines above. bf16 must report PASS."
  echo "If bf16 FAILs while fp16 PASSes, the GPU miscomputes the BF16 tensor-core"
  echo "path. Reject the machine. Do not debug prompts, models or PyTorch."
fi
exit $rc
