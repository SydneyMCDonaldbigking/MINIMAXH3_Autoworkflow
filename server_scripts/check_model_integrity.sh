#!/usr/bin/env bash
set -euo pipefail

# Verify the H3 model files are the ones we have rendered with before.
#
# We already accept the card before installing anything (check_bf16_mma.sh). This
# is the other half: accept the *weights*. 63 GB arrives over the network onto a
# machine we have never used, and a silently truncated or corrupted file does not
# announce itself - it shows up as a bad clip after minutes of paid sampling, which
# is exactly the failure mode that cost two days in August on the hardware side.
#
# Usage:
#   bash check_model_integrity.sh                 verify against the manifest
#   bash check_model_integrity.sh --write         print a fresh manifest to stdout
#
# The manifest lives in the repo at server_scripts/model_manifest.sha256 and is
# generated once from a machine whose output we have already accepted. Until it
# exists, run --write on a known-good box and commit the result.
#
# Optional env:
#   COMFYUI_DIR=/opt/ComfyUI

COMFYUI_DIR="${COMFYUI_DIR:-/opt/ComfyUI}"
MANIFEST="${MANIFEST:-$(dirname "$0")/model_manifest.sha256}"

FILES=(
  "models/diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors"
  "models/diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors"
  "models/text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors"
  "models/vae/minimax_h3_video_vae_fp16.safetensors"
  "models/vae/minimax_h3_audio_vae_fp32.safetensors"
  "models/loras/minimax_h3_turbo_v4_step600_ema.safetensors"
  "custom_nodes/ComfyUI-MiniMax-H3-Turbo/h3_silu_temb_grid.safetensors"
)

cd "$COMFYUI_DIR"

if [ "${1:-}" = "--write" ]; then
  echo "# H3 model manifest, generated $(date -u +%Y-%m-%dT%H:%M:%SZ) on $(hostname)"
  echo "# Generated from a machine whose rendered output was reviewed and accepted."
  for f in "${FILES[@]}"; do
    if [ -f "$f" ]; then
      sha256sum "$f"
    else
      echo "# MISSING $f" >&2
    fi
  done
  exit 0
fi

if [ ! -f "$MANIFEST" ]; then
  echo "No manifest at $MANIFEST." >&2
  echo "Run 'bash check_model_integrity.sh --write > $MANIFEST' on a known-good machine" >&2
  echo "and commit it. Skipping verification rather than pretending to verify." >&2
  exit 2
fi

echo "== verifying ${#FILES[@]} files against $(basename "$MANIFEST")"
fail=0
missing=0
while read -r want path; do
  case "$want" in \#*|"") continue ;; esac
  if [ ! -f "$path" ]; then
    printf '  MISSING  %s\n' "$path"; missing=$((missing+1)); continue
  fi
  got="$(sha256sum "$path" | cut -d' ' -f1)"
  if [ "$got" = "$want" ]; then
    printf '  ok       %s\n' "$path"
  else
    printf '  MISMATCH %s\n           want %s\n           got  %s\n' "$path" "$want" "$got"
    fail=$((fail+1))
  fi
done < "$MANIFEST"

echo
if [ "$fail" -gt 0 ] || [ "$missing" -gt 0 ]; then
  echo "FAIL: $fail mismatched, $missing missing."
  echo "Re-download the offending files before spending GPU time. A mismatch is not"
  echo "a warning: the weights differ from the ones every measurement in this repo"
  echo "was taken on, so nothing downstream is comparable."
  exit 1
fi
echo "PASS: every model file matches the manifest."
