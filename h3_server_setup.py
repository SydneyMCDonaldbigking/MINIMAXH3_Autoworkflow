#!/usr/bin/env python3
"""
Bootstrap MiniMax H3 ComfyUI on a remote Linux server over SSH.

Example:
  python h3_server_setup.py --ssh user@SERVER_IP

The remote side uses China-friendly mirrors by default. The script is careful
about staying inside one install directory and does not delete existing files.
"""

from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from textwrap import dedent


DEFAULT_INSTALL_DIR = "/opt/ComfyUI"
DEFAULT_PYPI_INDEX = "https://mirrors.aliyun.com/pypi/simple/"
DEFAULT_TORCH_INDEX = "https://download.pytorch.org/whl/cu124"
DEFAULT_HF_ENDPOINT = "https://hf-mirror.com"
DEFAULT_COMFY_REF = "v0.30.2"


def q(value: str) -> str:
    return shlex.quote(value)


def build_remote_script(args: argparse.Namespace) -> str:
    maybe_models = "" if args.skip_models else model_download_block(args)
    maybe_start = start_block(args) if args.start else ""

    return dedent(
        f"""\
        set -euo pipefail

        INSTALL_DIR={q(args.install_dir)}
        COMFY_REF={q(args.comfy_ref)}
        PYPI_INDEX={q(args.pypi_index)}
        TORCH_INDEX={q(args.torch_index)}
        HF_ENDPOINT_VALUE={q(args.hf_endpoint)}

        echo "[1/7] GPU status"
        if command -v nvidia-smi >/dev/null 2>&1; then
          nvidia-smi
        else
          echo "nvidia-smi not found; install NVIDIA driver/CUDA runtime first."
        fi

        echo "[2/7] System tools"
        if ! command -v git >/dev/null 2>&1; then
          echo "git is not installed. Please install git first, then rerun."
          exit 2
        fi
        if ! command -v python3 >/dev/null 2>&1; then
          echo "python3 is not installed. Please install Python 3.11/3.12/3.13 first."
          exit 2
        fi

        echo "[3/7] Clone or update ComfyUI"
        if [ ! -d "$INSTALL_DIR/.git" ]; then
          mkdir -p "$(dirname "$INSTALL_DIR")"
          if git ls-remote https://gitclone.com/github.com/Comfy-Org/ComfyUI.git >/dev/null 2>&1; then
            git clone https://gitclone.com/github.com/Comfy-Org/ComfyUI.git "$INSTALL_DIR"
          else
            git clone https://github.com/Comfy-Org/ComfyUI.git "$INSTALL_DIR"
          fi
        fi
        cd "$INSTALL_DIR"
        git fetch --tags || true
        git checkout "$COMFY_REF" || git checkout master

        echo "[4/7] Python virtualenv"
        python3 -m venv venv
        . venv/bin/activate
        python -m pip install -U pip setuptools wheel -i "$PYPI_INDEX"
        python -m pip config set global.index-url "$PYPI_INDEX"

        echo "[5/7] PyTorch and ComfyUI dependencies"
        python -m pip install torch torchvision torchaudio --index-url "$TORCH_INDEX" --extra-index-url "$PYPI_INDEX"
        python -m pip install -r requirements.txt -i "$PYPI_INDEX"
        python -m pip install -U huggingface_hub -i "$PYPI_INDEX"

        echo "[6/7] MiniMax H3 models"
        export HF_ENDPOINT="$HF_ENDPOINT_VALUE"
        export HF_HUB_DISABLE_XET=1
        {maybe_models}

        echo "[7/7] Import check"
        python - <<'PY'
        import torch
        print("torch:", torch.__version__)
        print("cuda:", torch.cuda.is_available())
        if torch.cuda.is_available():
            print("gpu:", torch.cuda.get_device_name(0))
            props = torch.cuda.get_device_properties(0)
            print("vram_gb:", round(props.total_memory / 1024**3, 2))
        PY

        echo "Done. ComfyUI path: $INSTALL_DIR"
        {maybe_start}
        """
    )


def model_download_block(args: argparse.Namespace) -> str:
    return dedent(
        """\
        mkdir -p models/diffusion_models models/text_encoders models/vae
        hf download Comfy-Org/MiniMax-H3 \
          diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors \
          diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors \
          text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors \
          vae/minimax_h3_video_vae_fp16.safetensors \
          vae/minimax_h3_audio_vae_fp32.safetensors \
          --local-dir models \
          --max-workers 2
        """
    ).strip()


def start_block(args: argparse.Namespace) -> str:
    listen = q(args.listen)
    port = int(args.port)
    instances = int(args.instances)
    if instances <= 1:
        return dedent(
            f"""\
            echo "Starting ComfyUI in background on {args.listen}:{port}"
            nohup "$INSTALL_DIR/venv/bin/python" main.py --listen {listen} --port {port} > comfyui_h3.log 2>&1 &
            echo $! > comfyui_h3.pid
            echo "PID: $(cat comfyui_h3.pid)"
            echo "Log: $INSTALL_DIR/comfyui_h3.log"
            """
        ).strip()

    return dedent(
        f"""\
        echo "Starting {instances} ComfyUI instances in background"
        for GPU_ID in $(seq 0 {instances - 1}); do
          INSTANCE_PORT=$(({port} + GPU_ID))
          LOG_FILE="comfyui_h3_gpu${{GPU_ID}}.log"
          PID_FILE="comfyui_h3_gpu${{GPU_ID}}.pid"
          echo "GPU $GPU_ID -> {args.listen}:$INSTANCE_PORT"
          CUDA_VISIBLE_DEVICES="$GPU_ID" nohup "$INSTALL_DIR/venv/bin/python" main.py --listen {listen} --port "$INSTANCE_PORT" > "$LOG_FILE" 2>&1 &
          echo $! > "$PID_FILE"
        done
        echo "Logs: $INSTALL_DIR/comfyui_h3_gpu*.log"
        """
    ).strip()


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Install/update ComfyUI MiniMax H3 on a remote Linux server."
    )
    parser.add_argument("--ssh", required=True, help="SSH target, for example root@1.2.3.4")
    parser.add_argument("--install-dir", default=DEFAULT_INSTALL_DIR)
    parser.add_argument("--comfy-ref", default=DEFAULT_COMFY_REF)
    parser.add_argument("--pypi-index", default=DEFAULT_PYPI_INDEX)
    parser.add_argument("--torch-index", default=DEFAULT_TORCH_INDEX)
    parser.add_argument("--hf-endpoint", default=DEFAULT_HF_ENDPOINT)
    parser.add_argument("--skip-models", action="store_true")
    parser.add_argument("--start", action="store_true")
    parser.add_argument("--instances", type=int, default=1)
    parser.add_argument("--listen", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8189)
    parser.add_argument("--print-only", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    script = build_remote_script(args)

    if args.print_only:
        print(script)
        return 0

    cmd = ["ssh", args.ssh, "bash", "-s"]
    print("Running remote bootstrap:", " ".join(shlex.quote(part) for part in cmd))
    proc = subprocess.run(cmd, input=script, text=True, check=False)
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
