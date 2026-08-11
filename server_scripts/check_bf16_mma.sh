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
REPS="${REPS:-5}"
SRC="$(dirname "$0")/bf16_mma_acceptance.cu"
BIN="/tmp/bf16_mma_acceptance"

echo "== GPU identity (record this; you cannot compare cards later without it) =="
nvidia-smi --query-gpu=name,uuid,serial,pci.bus_id,driver_version --format=csv,noheader || true
nvidia-smi -q 2>/dev/null | grep -A1 -i "MIG Mode" | head -2 || true

# Compute capability decides the -gencode target. Ask the GPU rather than making
# the caller know it: 8.0 = A100, 8.6 = A10/3090, 8.9 = 4090/L40S, 9.0 = H100.
if [ -z "${ARCH:-}" ]; then
  cap="$(nvidia-smi --query-gpu=compute_cap --format=csv,noheader 2>/dev/null | head -1 | tr -d ' .')"
  ARCH="${cap:-80}"
fi
echo "   compute capability -> building for sm_${ARCH}"

if [ "$ARCH" -lt 80 ] 2>/dev/null; then
  echo "ERROR: bf16 tensor-core MMA needs sm_80 or newer. This GPU is sm_${ARCH}." >&2
  exit 2
fi

if [ -z "$NVCC" ]; then
  NVCC="$(command -v nvcc 2>/dev/null || true)"
  [ -z "$NVCC" ] && NVCC="$(ls /usr/local/cuda*/bin/nvcc 2>/dev/null | head -1)"
fi

# Without nvcc, fall back to the PyTorch-level check. It is less airtight, since
# it cannot prove the fault is below the libraries, but it is still decisive
# enough to reject a machine: a healthy GPU returns zero inf.
if [ -z "$NVCC" ] || [ ! -x "$NVCC" ]; then
  echo
  echo "== nvcc not found, falling back to the PyTorch-level check =="
  python - <<'PY' || exit 2
import sys
try:
    import torch
except Exception as exc:
    print("Neither nvcc nor a usable PyTorch is present:", exc)
    print("Use a CUDA devel image, or copy in a prebuilt binary.")
    sys.exit(2)
torch.manual_seed(0)
a = torch.randn(4096, 4096, device="cuda", dtype=torch.bfloat16)
b = torch.randn(4096, 4096, device="cuda", dtype=torch.bfloat16)
print("  torch %s / cuda %s on %s" % (torch.__version__, torch.version.cuda,
                                      torch.cuda.get_device_name(0)))
print("  fp32 reference absmax :", round((a.float() @ b.float()).abs().max().item(), 1))
print("  fp16 same shape absmax:", round((a.half() @ b.half()).abs().max().item(), 1))
inf = [int((a @ b).isinf().sum()) for _ in range(3)]
print("  bf16 inf counts x3    :", inf)
print()
if any(inf):
    print("  FAIL - bf16 matmul produces inf. Reject this machine.")
    sys.exit(1)
print("  PASS - bf16 matmul is clean. fp32 and fp16 should both read about 340.")
PY
  exit $?
fi

if [ ! -f "$SRC" ]; then
  echo "ERROR: missing $SRC" >&2
  exit 2
fi

echo
echo "== Building native sm_${ARCH} cubin =="
# -cudart static makes the binary self-contained: it then runs on any machine
# with an NVIDIA driver and needs no CUDA toolkit, Python or PyTorch. Build it
# once on a machine that has nvcc and scp the ~1 MB result to bare images.
"$NVCC" "$SRC" -O3 -gencode "arch=compute_${ARCH},code=sm_${ARCH}" -cudart static -o "$BIN" || exit 2

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
