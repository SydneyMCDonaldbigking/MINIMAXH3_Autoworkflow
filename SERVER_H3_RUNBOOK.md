# MiniMax H3 ComfyUI Server Runbook

Purpose: a future Codex agent should be able to SSH into the China GPU server,
recover the MiniMax H3 ComfyUI setup, and run T2V/I2V/FLF2V/R2V jobs without
using the ComfyUI GUI.

This file is ASCII on purpose so it stays readable from Windows PowerShell and
remote shells. Do not add SSH passwords, cloud console passwords, or private
asset URLs here.

## 1. Verified Server Baseline

Observed on 2026-08-08:

- OS: Ubuntu 22.04
- GPU: 1x NVIDIA A100-PCIE-40GB
- NVIDIA driver: `550.127.08`
- `nvidia-smi` CUDA display: `12.4`
- Conda path: `/home/node/anaconda3/bin/conda`
- ComfyUI path: `/root/ComfyUI`
- ComfyUI version: `0.30.2`
- Old env: `comfy_h3`, Python 3.12, PyTorch `2.6.0+cu124`
- New env: `comfy_h3_torch29_cu126`, Python 3.12, PyTorch `2.9.1+cu126`

Important result:

- The old env can run 720P-ish jobs, but native 1080P jobs OOM.
- The new env enables `DynamicVRAM support` and has successfully run native
  1080P T2V and I2V.
- The host driver is still `550.127.08`, so ComfyUI still prints a warning that
  `cu130 optimized CUDA operations` are unavailable.
- To use PyTorch/cu130 optimized paths, the cloud image or host driver must be
  upgraded to a CUDA 13 compatible NVIDIA 580+ driver. Conda alone cannot
  replace the host driver.
- Do not run multiple H3 jobs concurrently on one A100 40G. Queue jobs
  sequentially, or use one ComfyUI process per GPU on multi-GPU servers.

## 2. Required Model Files

Expected server layout:

```text
/root/ComfyUI/models/diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors
/root/ComfyUI/models/diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors
/root/ComfyUI/models/text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors
/root/ComfyUI/models/vae/minimax_h3_video_vae_fp16.safetensors
/root/ComfyUI/models/vae/minimax_h3_audio_vae_fp32.safetensors
/root/ComfyUI/models/loras/minimax_h3_turbo_v4_step600_ema.safetensors
/root/ComfyUI/custom_nodes/ComfyUI-MiniMax-H3-Turbo/
```

Turbo LoRA sources:

- LoRA repo: `larryvrh/MiniMax-H3-Turbo-Lora`
- LoRA file: `minimax_h3_turbo_v4_step600_ema.safetensors`
- Custom node repo: `Larryvrh/ComfyUI-MiniMax-H3-Turbo`

For China servers, try the Hugging Face mirror first:

```bash
export HF_ENDPOINT=https://hf-mirror.com
export HF_HUB_DISABLE_XET=1
hf download Comfy-Org/MiniMax-H3 \
  diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors \
  diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors \
  text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors \
  vae/minimax_h3_video_vae_fp16.safetensors \
  vae/minimax_h3_audio_vae_fp32.safetensors \
  --local-dir /root/ComfyUI/models \
  --max-workers 2
```

If Hugging Face or GitHub is blocked, download locally and transfer with Baidu
Cloud or `scp`, then place the files in the exact paths above.

## 3. Recommended Conda Env

Keep the old env. Create a separate env for the better PyTorch path:

```bash
source /home/node/anaconda3/etc/profile.d/conda.sh
conda create -n comfy_h3_torch29_cu126 python=3.12 -y
conda activate comfy_h3_torch29_cu126

python -m pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
python -m pip config set global.trusted-host mirrors.aliyun.com

python -m pip install \
  torch==2.9.1+cu126 \
  torchvision==0.24.1+cu126 \
  torchaudio==2.9.1+cu126 \
  --index-url https://download.pytorch.org/whl/cu126 \
  --extra-index-url https://mirrors.aliyun.com/pypi/simple/

cd /root/ComfyUI
python -m pip install -r requirements.txt
```

Verify CUDA from Python:

```bash
python - <<'PY'
import torch
print(torch.__version__)
print(torch.version.cuda)
print(torch.cuda.is_available())
print(torch.cuda.get_device_name(0))
x = torch.ones((1,), device="cuda")
print(x)
PY
```

Expected key values:

```text
2.9.1+cu126
12.6
True
NVIDIA A100-PCIE-40GB
```

## 4. Start ComfyUI

Use port `8189` for the new env to avoid confusing it with the old `8188`
service:

```bash
cd /root/ComfyUI
source /home/node/anaconda3/etc/profile.d/conda.sh
conda activate comfy_h3_torch29_cu126

nohup python main.py \
  --listen 127.0.0.1 \
  --port 8189 \
  --lowvram \
  > comfyui_h3_torch29_cu126.log 2>&1 &

echo $! > comfyui_h3_torch29_cu126.pid
```

Wait for readiness:

```bash
for i in $(seq 1 90); do
  curl -fsS http://127.0.0.1:8189/system_stats >/dev/null && break
  sleep 2
done

curl -s http://127.0.0.1:8189/system_stats | head -c 1000
tail -n 120 comfyui_h3_torch29_cu126.log
```

Good startup signals:

```text
pytorch version: 2.9.1+cu126
Device: cuda:0 NVIDIA A100-PCIE-40GB : cudaMallocAsync
DynamicVRAM support detected and enabled
```

If two ComfyUI instances are running, the log may show:

```text
Could not acquire lock on database '/root/ComfyUI/user/comfyui.db'
```

Prefer running only one instance on a single-GPU server. To stop the old `8188`
process:

```bash
ps -eo pid,cmd | grep 'python main.py' | grep -v grep
kill <old_8188_pid>
sleep 3
nvidia-smi
```

## 5. Verify H3 and Turbo Nodes

```bash
python - <<'PY'
import json, urllib.request
obj=json.load(urllib.request.urlopen("http://127.0.0.1:8189/object_info"))
for n in ["MiniMaxH3TurboLoRA", "MiniMaxH3TurboSampler", "MiniMaxH3ImageToVideo", "MiniMaxH3ReferenceToVideo"]:
    print(n, "OK" if n in obj else "MISSING")
PY
```

All four should print `OK`.

## 6. Local Repo Files

Local workspace:

```text
C:\Users\uryuu\Desktop\comfyui_workflow
```

Important files:

```text
h3_runner.py                         # ComfyUI API runner: t2v/i2v/flf2v/r2v
h3_server_setup.py                   # Older remote bootstrap helper
SERVER_H3_RUNBOOK.md                 # This handoff runbook
server_scripts/install_h3_turbo.sh   # Server-side Turbo custom node + LoRA installer
server_scripts/run_h3_turbo_probe.sh # Server-side probe script
workflows/*.json                     # Generated ComfyUI API workflow JSON examples
server_outputs/                      # Downloaded test videos and preview frames
```

Upload runner files to the server:

```bash
scp -P <ssh_port> h3_runner.py root@<server_ip>:/root/ComfyUI/
scp -P <ssh_port> -r server_scripts root@<server_ip>:/root/ComfyUI/
```

Install Turbo support on the server:

```bash
cd /root/ComfyUI
source /home/node/anaconda3/etc/profile.d/conda.sh
conda activate comfy_h3_torch29_cu126
CONDA_ENV=comfy_h3_torch29_cu126 bash server_scripts/install_h3_turbo.sh
```

If downloading inside the server fails, use uploaded files:

```bash
TURBO_LORA_SOURCE=/root/uploads/minimax_h3_turbo_v4_step600_ema.safetensors \
TURBO_NODE_ZIP=/root/uploads/ComfyUI-MiniMax-H3-Turbo-main.zip \
CONDA_ENV=comfy_h3_torch29_cu126 \
bash server_scripts/install_h3_turbo.sh
```

## 7. Workflow Modes

`h3_runner.py` supports:

| Mode | Command | Use case | Diffusion model |
| --- | --- | --- | --- |
| Text to video | `t2v` | Prompt-only video | FL2VA |
| Image to video | `i2v` | First-frame guided video | FL2VA |
| First-last-frame video | `flf2v` | Transition between first and last frames | FL2VA |
| Reference image video | `r2v` | Reference-guided subject/style video | REF2VA |

Common settings:

- Speed first: `--steps 4 --turbo`
- Safer quality: `--steps 6 --turbo`
- Native 1080P: add `--turbo-low-vram`
- 720P-ish landscape: `1344x768`
- 1080P-ish landscape: `1920x1088`
- `--duration 5` outputs about 124 frames, 24fps, 5.17s
- Do not run concurrent H3 jobs on one A100 40G

`--turbo` inserts:

- `MiniMaxH3TurboLoRA`
- `MiniMaxH3TurboSampler`
- Scheduler: simple Turbo path
- Default Turbo LoRA: `minimax_h3_turbo_v4_step600_ema.safetensors`

## 8. Example Commands

### 8.1 T2V 720P

```bash
cd /root/ComfyUI
source /home/node/anaconda3/etc/profile.d/conda.sh
conda activate comfy_h3_torch29_cu126

/usr/bin/time -p python h3_runner.py t2v \
  --server http://127.0.0.1:8189 \
  --prompt "A fast commercial video for handmade steamed buns, chef hands shaping soft white baozi dough on a floured kitchen table, warm restaurant light, appetizing food advertising style, realistic texture, gentle steam, slow camera push-in, no text, no logo, no watermark." \
  --width 1344 --height 768 \
  --duration 5 \
  --steps 4 \
  --seed 2026080830 \
  --prefix test_outputs/baozi_t2v_720_turbo_4step \
  --output-dir test_outputs \
  --turbo \
  --poll 10 \
  --timeout 10800
```

### 8.2 I2V 720P

Upload the input image first:

```bash
scp -P <ssh_port> C:/path/to/input.png root@<server_ip>:/root/ComfyUI/baozi_reference.png
```

Run:

```bash
/usr/bin/time -p python h3_runner.py i2v \
  --server http://127.0.0.1:8189 \
  --prompt "Animate this food production scene into a premium short commercial: chef hands gently shaping steamed bun dough, flour particles on the table, soft warm kitchen light, subtle camera push-in, appetizing realistic food texture, no text, no logo, no watermark." \
  --first-frame baozi_reference.png \
  --width 1344 --height 768 \
  --duration 5 \
  --steps 4 \
  --seed 2026080831 \
  --prefix test_outputs/baozi_i2v_720_turbo_4step \
  --output-dir test_outputs \
  --overwrite-upload \
  --turbo \
  --poll 10 \
  --timeout 10800
```

### 8.3 R2V 720P

For reference video, mention `<Picture 1>` in the prompt:

```bash
/usr/bin/time -p python h3_runner.py r2v \
  --server http://127.0.0.1:8189 \
  --prompt "Use <Picture 1> as the visual reference. Create a premium commercial food video of handmade steamed buns being shaped by chef hands on a floured kitchen counter, warm restaurant lighting, realistic texture, gentle steam, subtle camera push-in, appetizing advertisement style, no text, no logo, no watermark." \
  --ref-image baozi_reference.png \
  --width 1344 --height 768 \
  --duration 5 \
  --steps 4 \
  --seed 2026080832 \
  --prefix test_outputs/baozi_r2v_720_turbo_4step \
  --output-dir test_outputs \
  --overwrite-upload \
  --turbo \
  --poll 10 \
  --timeout 10800
```

### 8.4 T2V 1080P

Use the new env and `--turbo-low-vram`:

```bash
/usr/bin/time -p python h3_runner.py t2v \
  --server http://127.0.0.1:8189 \
  --prompt "A fast commercial video for handmade steamed buns, chef hands shaping soft white baozi dough on a floured kitchen table, warm restaurant light, appetizing food advertising style, realistic texture, gentle steam, slow camera push-in, no text, no logo, no watermark." \
  --width 1920 --height 1088 \
  --duration 5 \
  --steps 4 \
  --seed 2026080830 \
  --prefix test_outputs/baozi_t2v_1080_turbo_4step_torch29_lowvram \
  --output-dir test_outputs \
  --turbo \
  --turbo-low-vram \
  --poll 10 \
  --timeout 10800
```

### 8.5 I2V 1080P

```bash
/usr/bin/time -p python h3_runner.py i2v \
  --server http://127.0.0.1:8189 \
  --prompt "Animate this food production scene into a premium short commercial: chef hands gently shaping steamed bun dough, flour particles on the table, soft warm kitchen light, subtle camera push-in, appetizing realistic food texture, no text, no logo, no watermark." \
  --first-frame baozi_reference.png \
  --width 1920 --height 1088 \
  --duration 5 \
  --steps 4 \
  --seed 2026080831 \
  --prefix test_outputs/baozi_i2v_1080_turbo_4step_torch29_lowvram \
  --output-dir test_outputs \
  --overwrite-upload \
  --turbo \
  --turbo-low-vram \
  --poll 10 \
  --timeout 10800
```

### 8.6 R2V 1080P

This was started but the server died before a final result. Retry only if needed,
with the new env, no other ComfyUI process, and `--turbo-low-vram`.

```bash
/usr/bin/time -p python h3_runner.py r2v \
  --server http://127.0.0.1:8189 \
  --prompt "Use <Picture 1> as the visual reference. Create a premium commercial food video of handmade steamed buns being shaped by chef hands on a floured kitchen counter, warm restaurant lighting, realistic texture, gentle steam, subtle camera push-in, appetizing advertisement style, no text, no logo, no watermark." \
  --ref-image baozi_reference.png \
  --width 1920 --height 1088 \
  --duration 5 \
  --steps 4 \
  --seed 2026080832 \
  --prefix test_outputs/baozi_r2v_1080_turbo_4step_torch29_lowvram \
  --output-dir test_outputs \
  --overwrite-upload \
  --turbo \
  --turbo-low-vram \
  --poll 10 \
  --timeout 10800
```

## 9. Download and Inspect Outputs

Download:

```bash
scp -P <ssh_port> root@<server_ip>:/root/ComfyUI/test_outputs/<file>.mp4 server_outputs/
```

Check video metadata:

```bash
ffprobe -v error \
  -select_streams v:0 \
  -show_entries stream=width,height,r_frame_rate,duration,nb_frames \
  -of default=nw=1 \
  server_outputs/<file>.mp4
```

Extract preview frames:

```bash
mkdir -p server_outputs/previews/<name>
ffmpeg -y -i server_outputs/<file>.mp4 \
  -vf "fps=1,scale=480:-1" \
  server_outputs/previews/<name>/frame_%02d.jpg
```

## 10. Measured Speed

Test settings:

- GPU: A100-PCIE-40GB
- Output length: 5s, about 124 frames, 24fps
- Turbo LoRA: `minimax_h3_turbo_v4_step600_ema.safetensors`
- Steps: 4
- 720P-ish: `1344x768`
- 1080P-ish: `1920x1088`

Measured results:

| Mode | Size | Env | Result | Wall time |
| --- | ---: | --- | --- | ---: |
| T2V | 1344x768 | old env / runnable | success | 260s |
| I2V | 1344x768 | old env / runnable | success | 340s |
| R2V | 1344x768 | old env / runnable | success | 370s |
| T2V | 1920x1088 | `comfy_h3_torch29_cu126` | success | 480.18s |
| I2V | 1920x1088 | `comfy_h3_torch29_cu126` | success | 510.21s |
| R2V | 1920x1088 | `comfy_h3_torch29_cu126` | incomplete | server died / SSH dropped |

Extra result:

- Egg tart ad T2V, `1344x768`, 6 steps, about 5.17s output: `370.16s`.
- Old env native 1080P OOMed after about 120s-250s depending on mode.
- New env native 1080P T2V/I2V succeeded, so PyTorch 2.9 + DynamicVRAM matters.

Throughput estimate:

- 720P/4-step: about 9.7 to 13.8 videos/hour/GPU.
- 1080P/4-step: about 7 videos/hour/GPU, based only on successful T2V/I2V.
- Practical production path: batch-generate 720P, then upscale to 1080P.

## 11. Parallelism and Hardware Notes

Single GPU:

- Do not run multiple H3 jobs at once on one A100 40G.
- H3 consumes VRAM and memory bandwidth heavily.
- Concurrent jobs usually become slower and more likely to OOM.
- Use the ComfyUI/API queue sequentially.

Multi GPU:

- Run one ComfyUI process per GPU.
- Use one port per process, for example `8188`, `8189`, `8190`.
- Pin each process with `CUDA_VISIBLE_DEVICES`.

Example:

```bash
CUDA_VISIBLE_DEVICES=0 python main.py --listen 127.0.0.1 --port 8188 --lowvram
CUDA_VISIBLE_DEVICES=1 python main.py --listen 127.0.0.1 --port 8189 --lowvram
```

Hardware decision:

- CPU upgrades help very little for H3 generation speed.
- The bottleneck is GPU VRAM, memory bandwidth, and offload behavior.
- A100 40G is fine for 720P batch work.
- Native 1080P works for T2V/I2V in the new env, but is slow.
- For serious native 1080P batch work, prefer 80G VRAM or multiple GPUs.
- If the provider supports image/driver switching, test a newer Ubuntu image with
  NVIDIA driver 580+ and PyTorch/cu130.

## 12. Recovery Checklist After Crash or Reboot

After reconnecting, do not immediately rerun. Check state first:

```bash
nvidia-smi
df -h
ps -eo pid,cmd | grep 'python main.py' | grep -v grep
ls -lh /root/ComfyUI/test_outputs | tail
tail -n 200 /root/ComfyUI/comfyui_h3_torch29_cu126.log
curl -fsS http://127.0.0.1:8189/system_stats
```

If ComfyUI is down:

```bash
cd /root/ComfyUI
source /home/node/anaconda3/etc/profile.d/conda.sh
conda activate comfy_h3_torch29_cu126
nohup python main.py --listen 127.0.0.1 --port 8189 --lowvram > comfyui_h3_torch29_cu126.log 2>&1 &
echo $! > comfyui_h3_torch29_cu126.pid
```

If GPU memory is stuck:

```bash
nvidia-smi
kill <stale_python_pid>
sleep 3
nvidia-smi
```

## 13. Short Boss Summary

Current A100 40G MiniMax H3 Turbo result:

- 720P batch production works: around 4 to 6 minutes per 5s clip.
- Native 1080P T2V/I2V works in the new env, but takes around 8 to 8.5 minutes
  per 5s clip.
- Best production plan: generate 720P clips in batch, then upscale to 1080P.
- For native 1080P batch production, rent 80G VRAM or build a multi-GPU queue.
