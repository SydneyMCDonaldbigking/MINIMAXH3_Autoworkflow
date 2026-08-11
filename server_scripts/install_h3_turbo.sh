#!/usr/bin/env bash
set -euo pipefail

# Install MiniMax-H3 Turbo LoRA support into an existing ComfyUI checkout.
#
# Expected existing layout:
#   /root/ComfyUI
#   /root/ComfyUI/models/diffusion_models/minimax_h3_*.safetensors
#   /root/ComfyUI/models/text_encoders/qwen3vl_*.safetensors
#   /root/ComfyUI/models/vae/minimax_h3_*vae*.safetensors
#
# Optional env:
#   COMFYUI_DIR=/root/ComfyUI
#   CONDA_ENV=comfy_h3_torch29_cu126
#   HF_ENDPOINT=https://hf-mirror.com
#   TURBO_LORA_SOURCE=/path/to/minimax_h3_turbo_v4_step600_ema.safetensors
#   TURBO_NODE_ZIP=/path/to/ComfyUI-MiniMax-H3-Turbo-main.zip

COMFYUI_DIR="${COMFYUI_DIR:-/root/ComfyUI}"
CONDA_ENV="${CONDA_ENV:-comfy_h3_torch29_cu126}"
HF_ENDPOINT="${HF_ENDPOINT:-https://hf-mirror.com}"
TURBO_REPO="larryvrh/MiniMax-H3-Turbo-Lora"
TURBO_LORA_NAME="${TURBO_LORA_NAME:-minimax_h3_turbo_v4_step600_ema.safetensors}"
NODE_DIR="$COMFYUI_DIR/custom_nodes/ComfyUI-MiniMax-H3-Turbo"

activate_python() {
  if command -v conda >/dev/null 2>&1; then
    # shellcheck disable=SC1091
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate "$CONDA_ENV"
  elif [ -f "$COMFYUI_DIR/venv/bin/activate" ]; then
    # shellcheck disable=SC1091
    source "$COMFYUI_DIR/venv/bin/activate"
  fi
}

require_comfyui() {
  if [ ! -d "$COMFYUI_DIR" ]; then
    echo "ComfyUI not found: $COMFYUI_DIR" >&2
    exit 2
  fi
  mkdir -p "$COMFYUI_DIR/custom_nodes" "$COMFYUI_DIR/models/loras"
}

install_node_from_zip() {
  local zip_path="$1"
  local tmp_dir
  tmp_dir="$(mktemp -d)"
  unzip -q "$zip_path" -d "$tmp_dir"
  rm -rf "$NODE_DIR"
  local extracted
  extracted="$(find "$tmp_dir" -mindepth 1 -maxdepth 1 -type d | head -n 1)"
  mv "$extracted" "$NODE_DIR"
  rm -rf "$tmp_dir"
}

install_custom_node() {
  if [ -f "$NODE_DIR/__init__.py" ]; then
    echo "Turbo custom node already installed: $NODE_DIR"
    return
  fi

  if [ -n "${TURBO_NODE_ZIP:-}" ] && [ -f "$TURBO_NODE_ZIP" ]; then
    echo "Installing Turbo node from local zip: $TURBO_NODE_ZIP"
    install_node_from_zip "$TURBO_NODE_ZIP"
    return
  fi

  local zip_path="/tmp/ComfyUI-MiniMax-H3-Turbo-main.zip"
  echo "Downloading Turbo custom node from GitHub codeload..."
  if curl -L --retry 3 --connect-timeout 20 \
      -o "$zip_path" \
      "https://codeload.github.com/Larryvrh/ComfyUI-MiniMax-H3-Turbo/zip/refs/heads/main"; then
    install_node_from_zip "$zip_path"
  else
    echo "Could not download custom node from GitHub." >&2
    echo "Upload the node zip manually and rerun with TURBO_NODE_ZIP=/path/to/zip." >&2
    exit 3
  fi
}

install_lora() {
  local target="$COMFYUI_DIR/models/loras/$TURBO_LORA_NAME"
  if [ -f "$target" ]; then
    echo "Turbo LoRA already exists: $target"
    return
  fi

  if [ -n "${TURBO_LORA_SOURCE:-}" ] && [ -f "$TURBO_LORA_SOURCE" ]; then
    echo "Copying Turbo LoRA from local file: $TURBO_LORA_SOURCE"
    cp "$TURBO_LORA_SOURCE" "$target"
    return
  fi

  echo "Downloading Turbo LoRA from Hugging Face mirror..."
  export HF_ENDPOINT
  export HF_HUB_DISABLE_XET=1
  python -m pip install -U huggingface_hub -i https://mirrors.aliyun.com/pypi/simple/
  hf download "$TURBO_REPO" "$TURBO_LORA_NAME" \
    --local-dir "$COMFYUI_DIR/models/loras" \
    --max-workers 1
}

verify_files() {
  test -f "$NODE_DIR/__init__.py"
  test -f "$NODE_DIR/h3_silu_temb_grid.safetensors"
  test -f "$COMFYUI_DIR/models/loras/$TURBO_LORA_NAME"
  echo "Turbo install OK."
}

main() {
  require_comfyui
  activate_python
  install_custom_node
  install_lora
  verify_files
}

main "$@"
