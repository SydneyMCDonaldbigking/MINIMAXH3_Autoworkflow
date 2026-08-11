# MiniMax H3 ComfyUI Remote Runner

This folder contains a small Python runner that can control a remote ComfyUI
server through the ComfyUI HTTP API. It is designed for a headless Linux A100
server.

For the SSH cluster dispatcher, install optional local dependencies:

```bash
python -m pip install -r requirements.txt
```

## Start here

`CURRENT_WORKFLOW.md` is the single operational path from renting a machine to a
gated clip, and it marks which claims are verified and which are not. Read it
before the route-specific documents below.

## Files

- `CURRENT_WORKFLOW.md`: the current end-to-end working path. Start here.
- `RENTAL_CHECKLIST.md`: how to accept a rented GPU and avoid the traps that cost two days.
- `H200_DAY_PLAN.md`: one page, in order, for the next render session.
- `EXPERIMENT_PLAN_ACCELERATION.md`: untested acceleration and sigma-shift experiments, with the baseline to beat.
- `check_clip_quality.py`: technical QC gate for generated clips.
- `server_scripts/diagnose_h3_black.sh`: staged probe ladder for black or failed output.
- `h3_server_setup.py`: SSH bootstrap for installing/updating ComfyUI and H3.
- `h3_runner.py`: local API runner for text/image/reference video jobs.
- `image2_first_frame.py`: OpenRouter GPT Image 2 first-frame runner.
- `cluster_runner.py`: local SSH cluster dispatcher for batch H3 jobs.
- `h3_sequence_runner.py`: runs 3x5s MiniMax H3 clips sequentially and stitches them.
- `generate_reference_assets.ps1`: generates protagonist, scene, mid-state, and final-state Seedream references before H3.
- `prompts/COOKING_PROMPT_PRODUCTION_STANDARD.md`: recipe-grounded prompt package standard, including H3 prompts, Reels caption, subtitles, and source notes.
- `prompts/templates/preproduction_package/`: tracked skeleton for the ignored `sequence_outputs/<dish>/preproduction/` package.
- `BRAND_ASSETS.md`: local brand/logo memory for Image2 and MiniMax H3 jobs.
- `SERVER_H3_RUNBOOK.md`: distilled server environment and workflow runbook.
- `MIGRATION_A100_H3.md`: short A100 migration and production cheat sheet.
- `BENCHMARKS_2026-08-09.md`: A100/L40 MiniMax H3 Turbo setup and speed results.
- `MINIMAX_H3_15S_STORYBOARD_WORKFLOW.md`: one-shot 10s/15s storyboard + Image2 opening-frame workflow.
- `MINIMAX_H3_3X5_NATIVE1080_WORKFLOW.md`: A100-40G native vertical 1080 workaround using three stitched 5s clips.
- `IMAGE2_FIRST_FRAME_RUNBOOK.md`: `.env.local` setup and first-frame commands.
- `CLUSTER_RUNNER.md`: multi-server batch runner documentation.
- `servers.example.yaml`, `jobs.example.yaml`: cluster config templates.
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
source /home/node/anaconda3/etc/profile.d/conda.sh
conda activate comfy_h3_torch29_cu126
python main.py --listen 127.0.0.1 --port 8189 --lowvram
```

Then open an SSH tunnel from this PC:

```bash
ssh -N -L 8189:127.0.0.1:8189 user@SERVER_IP
```

After that, this local script can send jobs to `http://127.0.0.1:8189`.

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

Validate all generated dish configs without overwriting production prompts:

```bash
python generate_clip_prompts.py --all --check
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

Use the PyTorch CUDA wheel that matches the current runbook:

```bash
python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126 --extra-index-url https://mirrors.aliyun.com/pypi/simple/
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

## Current production baseline

Use `CURRENT_WORKFLOW.md` as the source of truth before paying for GPU time.
The current production baseline is:

- Driver `550.127.08`
- Conda env `comfy_h3_torch29_cu126`
- ComfyUI port `8189`
- Native vertical `1088x1920`
- R2V with reference stack
- Turbo LoRA on, `steps: 8`, `turbo_low_vram: true`
- `no_audio: true`
- Final crop to exact `1080x1920`

Older `8188`, `comfy_h3`, cu124, and 4-step timings are historical benchmark or
diagnostic context only. See `BENCHMARKS_2026-08-09.md` and
`SERVER_H3_RUNBOOK.md` when investigating old runs.

## LoRA note

MiniMax H3 Turbo LoRA:

- Repo: `larryvrh/MiniMax-H3-Turbo-Lora`
- Recommended file: `minimax_h3_turbo_v4_step600_ema.safetensors`
- Custom node: `Larryvrh/ComfyUI-MiniMax-H3-Turbo`
- Put the LoRA in `ComfyUI/models/loras/`
- Use `--turbo`, production `8` steps, scheduler `simple`, strength `1.0`

Server install, assuming `h3_runner.py` and `server_scripts/` have been uploaded
to `/root/ComfyUI`:

```bash
cd /root/ComfyUI
bash server_scripts/install_h3_turbo.sh
```

Run a 768x448, 5-second, 8-step Turbo I2V probe:

```bash
cd /root/ComfyUI
bash server_scripts/run_h3_turbo_probe.sh
```

Run a lower-step experiment only when intentionally benchmarking quality loss:

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

## Cluster preflight

Before running a batch across old/new servers:

```powershell
python cluster_runner.py check --servers servers.yaml
python cluster_runner.py check --servers servers.yaml --upload-runner --start-comfy
```
