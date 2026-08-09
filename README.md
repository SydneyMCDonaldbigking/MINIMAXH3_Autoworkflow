# MiniMax H3 ComfyUI Remote Runner

This folder contains a small Python runner that can control a remote ComfyUI
server through the ComfyUI HTTP API. It is designed for a headless Linux A100
server.

## Files

- `h3_server_setup.py`: SSH bootstrap for installing/updating ComfyUI and H3.
- `h3_runner.py`: local API runner for text/image/reference video jobs.
- `SERVER_H3_RUNBOOK.md`: distilled server environment and workflow runbook.
- `MINIMAX_H3_15S_STORYBOARD_WORKFLOW.md`: one-shot 10s/15s storyboard + Image2 opening-frame workflow.
- `server_scripts/install_h3_turbo.sh`: server-side Turbo LoRA installer.
- `server_scripts/run_h3_turbo_probe.sh`: server-side Turbo LoRA speed probe.
- `workflows/*.json`: generated ComfyUI API JSON examples.

## What must exist on the server

ComfyUI must be running with MiniMax H3 support and these model files:

- `models/diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors`
- `models/diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors`
- `models/text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors`
- `models/vae/minimax_h3_video_vae_fp16.safetensors`
- `models/vae/minimax_h3_audio_vae_fp32.safetensors`

Start ComfyUI on the server like this:

```bash
cd /root/ComfyUI
conda activate comfy_h3
python main.py --listen 127.0.0.1 --port 8188 --lowvram
```

Then open an SSH tunnel from this PC:

```bash
ssh -N -L 8188:127.0.0.1:8188 user@SERVER_IP
```

After that, this local script can send jobs to `http://127.0.0.1:8188`.

## Commands

Text to video:

```bash
python h3_runner.py t2v --prompt "A cinematic shot of..." --duration 5
```

Image to video:

```bash
python h3_runner.py i2v --prompt "Camera slowly pushes in..." --first-frame C:\path\image.png
```

First and last frame to video:

```bash
python h3_runner.py flf2v --prompt "A smooth transition..." --first-frame C:\path\start.png --last-frame C:\path\end.png
```

Reference image to video:

```bash
python h3_runner.py r2v --prompt "The same character walks through..." --ref-image C:\path\ref1.png --ref-image C:\path\ref2.png
```

Save the ComfyUI API workflow JSON without submitting:

```bash
python h3_runner.py t2v --prompt "test" --save-api-json workflows/h3_t2v_api.json --no-submit
```

## Server download mirrors for China

Use PyPI mirrors:

```bash
python -m pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
python -m pip config set global.trusted-host mirrors.aliyun.com
```

Use Aliyun's PyTorch CUDA wheel mirror:

```bash
python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124 --extra-index-url https://mirrors.aliyun.com/pypi/simple/
```

Use Hugging Face mirror for the H3 model repo:

```bash
export HF_ENDPOINT=https://hf-mirror.com
export HF_HUB_DISABLE_XET=1
hf download Comfy-Org/MiniMax-H3 \
  diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors \
  diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors \
  text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors \
  vae/minimax_h3_video_vae_fp16.safetensors \
  vae/minimax_h3_audio_vae_fp32.safetensors \
  --local-dir /opt/ComfyUI/models \
  --max-workers 2
```

MiniMax H3's bundled local template asks for about 57 GB VRAM. An A100 80 GB is
the expected target; an A100 40 GB can run with offload/lowvram, but it is much
slower and less comfortable.

## Current server result

The current test server was set up with:

- Ubuntu 22.04
- 1x NVIDIA A100-PCIE-40GB
- Conda env `comfy_h3`, Python 3.12
- ComfyUI 0.30.2
- PyTorch 2.6.0+cu124
- H3 FL2VA + REF2VA diffusion models, Qwen3-VL text encoder, video VAE, audio VAE

ComfyUI is running at `127.0.0.1:8188` on the server. Because the driver is CUDA
12.4, the server cannot use ComfyUI's newer CUDA 13 / PyTorch 2.8 optimized path;
it works, but performance is not ideal.

Measured image-to-video speed on A100 40GB:

| Settings | Runtime |
| --- | ---: |
| 768x448, 22 frames, 4 steps, cold load | 115s, first run also hit an old SaveVideo API issue |
| 768x448, 22 frames, 4 steps, warm | 15s |
| 768x448, 124 frames, 4 steps | 140s |
| 768x448, 124 frames, 20 steps | 335s |
| 1344x768, 124 frames, 4 steps | 330s |

Downloaded test videos are in `server_outputs/`.

## LoRA note

MiniMax H3 Turbo LoRA:

- Repo: `larryvrh/MiniMax-H3-Turbo-Lora`
- Recommended file: `minimax_h3_turbo_v4_step600_ema.safetensors`
- Custom node: `Larryvrh/ComfyUI-MiniMax-H3-Turbo`
- Put the LoRA in `ComfyUI/models/loras/`
- Use `--turbo`, 4-8 steps, scheduler `simple`, strength `1.0`

Server install, assuming `h3_runner.py` and `server_scripts/` have been uploaded
to `/root/ComfyUI`:

```bash
cd /root/ComfyUI
bash server_scripts/install_h3_turbo.sh
```

Run a 768x448, 5-second, 6-step Turbo I2V probe:

```bash
cd /root/ComfyUI
bash server_scripts/run_h3_turbo_probe.sh
```

Run a 4-step probe:

```bash
cd /root/ComfyUI
STEPS=4 bash server_scripts/run_h3_turbo_probe.sh
```

If Hugging Face mirror is blocked on the server, download the LoRA on this PC and
transfer it to the server by Baidu Cloud or `scp`, then run:

```bash
cd /root/ComfyUI
TURBO_LORA_SOURCE=/root/uploads/minimax_h3_turbo_v4_step600_ema.safetensors \
  bash server_scripts/install_h3_turbo.sh
```

If GitHub is blocked for the custom node, upload the node zip and run:

```bash
cd /root/ComfyUI
TURBO_NODE_ZIP=/root/uploads/ComfyUI-MiniMax-H3-Turbo-main.zip \
  bash server_scripts/install_h3_turbo.sh
```

## Remote bootstrap

After SSH works:

```bash
python h3_server_setup.py --ssh user@SERVER_IP --start
```

Start one ComfyUI instance per GPU for a 6-card server:

```bash
python h3_server_setup.py --ssh user@SERVER_IP --start --instances 6
```

Print the remote shell commands without running them:

```bash
python h3_server_setup.py --ssh user@SERVER_IP --print-only
```
