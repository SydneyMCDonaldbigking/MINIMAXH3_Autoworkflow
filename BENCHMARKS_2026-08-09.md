# MiniMax H3 Benchmarks - 2026-08-09

Purpose: record the actual China-server setup and MiniMax H3 Turbo timings for
future Codex tasks. Do not store SSH passwords here.

## Server Setup

Both servers were rebuilt with the same clean environment:

- OS: Ubuntu 22.04.4
- NVIDIA driver: `550.127.08`
- Conda: `/home/node/anaconda3`
- Conda env: `comfy_h3_torch29_cu126`
- Python: `3.12`
- PyTorch: `2.9.1+cu126`
- ComfyUI: `0.30.2`, commit/tag observed as `dec5d94`
- ComfyUI API: `127.0.0.1:8189`
- Startup flag: `--lowvram`
- Turbo LoRA: `minimax_h3_turbo_v4_step600_ema.safetensors`

Observed GPUs:

| Server label | GPU | Torch CUDA | VRAM from ComfyUI |
| --- | --- | --- | ---: |
| `a100-cn` | NVIDIA A100-PCIE-40GB | 12.6 | 40.3 GB |
| `l40-cn` | NVIDIA L40 | 12.6 | 47.6 GB |

## China Download Notes

The most reliable path during this setup was:

1. Build the conda env once on the faster server.
2. Pack it with `conda-pack`.
3. Transfer the packed env to the slower server with `scp`.
4. Download MiniMax H3 model files directly with `aria2c` from `hf-mirror.com`.

The direct PyTorch wheel download on the L40 server was too slow to be practical
in this run. The A100-to-L40 `conda-pack` transfer was much faster.

Model download files:

```text
/root/ComfyUI/models/diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors
/root/ComfyUI/models/diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors
/root/ComfyUI/models/text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors
/root/ComfyUI/models/vae/minimax_h3_video_vae_fp16.safetensors
/root/ComfyUI/models/vae/minimax_h3_audio_vae_fp32.safetensors
/root/ComfyUI/models/loras/minimax_h3_turbo_v4_step600_ema.safetensors
```

`aria2c` can print occasional 403 or low-speed errors for individual chunks.
That was acceptable as long as the final line showed `OK` and no `.aria2` file
remained.

## Test Settings

All tests below used:

- MiniMax H3 Turbo LoRA
- `--steps 4`
- `--duration 5`
- 124 frames at 24 fps, output duration about 5.17s
- 720P-ish: `1344x768`
- 1080P-ish: `1920x1088` because H3 sizes must be multiples of 32
- 1080P runs used `--turbo-low-vram`

Modes:

- `t2v`: prompt only, FL2VA model
- `i2v`: uploaded first frame, FL2VA model
- `r2v`: uploaded reference image, REF2VA model

## Results

### A100 40G

| Mode | Size | Runtime | Output |
| --- | --- | ---: | --- |
| T2V | 1344x768 | 205.17s | `outputs/a100/a100_t2v_720p_4step_00001_.mp4` |
| I2V | 1344x768 | 205.20s | `outputs/a100/a100_i2v_720p_4step_00001_.mp4` |
| R2V | 1344x768 | 210.20s | `outputs/a100/a100_r2v_720p_4step_00001_.mp4` |
| T2V | 1920x1088 | 475.29s | `outputs/a100/a100_t2v_1080p_4step_00001_.mp4` |
| I2V | 1920x1088 | 515.33s | `outputs/a100/a100_i2v_1080p_4step_00001_.mp4` |
| R2V | 1920x1088 | 500.29s | `outputs/a100/a100_r2v_1080p_4step_00001_.mp4` |

### L40 48G

| Mode | Size | Runtime | Output |
| --- | --- | ---: | --- |
| T2V | 1344x768 | 245.34s | `outputs/l40/l40_t2v_720p_4step_00001_.mp4` |
| I2V | 1344x768 | 230.33s | `outputs/l40/l40_i2v_720p_4step_00001_.mp4` |
| R2V | 1344x768 | 250.37s | `outputs/l40/l40_r2v_720p_4step_00001_.mp4` |
| T2V | 1920x1088 | 575.91s | `outputs/l40/l40_t2v_1080p_4step_00001_.mp4` |

### 15s Vertical R2V Production Probe

Settings:

- `r2v`
- `--width 768 --height 1344`
- `--duration 15`
- `--steps 4 --turbo`
- References in order: Image2/opening-frame image, source product image,
  `company_logo/AGO.png`
- Output duration: 15.084s at 24fps

| Server | Job | Runtime | Result | Local output |
| --- | --- | ---: | --- | --- |
| A100 40G | egg tart ad | 850.43s | success | `outputs/a100_egg_tart/a100_egg_tart_15s_vertical_r2v_00001_.mp4` |
| A100 40G | baozi ad | 850.41s | success | `outputs/a100_baozi/a100_baozi_15s_vertical_r2v_00001_.mp4` |
| L40 48G | baozi ad | 1001.18s | failed | no mp4; sampling reached 4/4, then the ComfyUI process was killed during VAE decode/save |

### 1080p Vertical Probe

For vertical social delivery, exact `1080x1920` is not divisible by 32, so the
native H3 test used `1088x1920`.

| Server | Size | Flags | Runtime before failure | Result |
| --- | --- | --- | ---: | --- |
| A100 40G | 1088x1920 | `--duration 15 --steps 4 --turbo --turbo-low-vram` | 25.14s | sampler OOM |
| A100 40G | 960x1696 | `--duration 15 --steps 4 --turbo --turbo-low-vram` | 25.15s | sampler OOM |

Strict conclusion: A100 40G did not pass native vertical 1080p 15s R2V. Upscaled
`768x1344 -> 1080x1920` files are delivery-size files only and must not be
reported as native 1080p H3 generation.

The old-duck-soup output below was generated at `768x1344` and then upscaled to
`1080x1920`; it is useful as a workflow proof, but not as a 1080p quality proof.

| Server | Job | Internal generation | Delivery file | Runtime | Result |
| --- | --- | --- | --- | ---: | --- |
| A100 40G | old duck soup tutorial | 768x1344 | upscaled 1080x1920 | 855.42s | success, but not native 1080p |

## Conclusion

For this MiniMax H3 Turbo workflow, A100 40G was faster and more stable than
L40 48G despite the L40 having more VRAM.

Practical production result:

| Target | A100 40G | L40 48G |
| --- | ---: | ---: |
| 15s 768x1344 R2V | 14.17 min/job, measured twice | not reliable in this run |
| 15s native 1088x1920 vertical R2V | OOM at sampler | not tested after L40 15s failure |
| 15s 1344x768 estimate from 5s tests | about 10-13 min/job | about 12-15 min/job |
| 15s 1920x1088 estimate from 5s tests | about 24-30 min/job | likely 29-36 min/job |

Use one H3 job per GPU. For batch advertising production, scale by running more
servers or more GPUs in parallel rather than trying to run parallel jobs on a
single GPU.

Recommendation: use A100 as the primary 15s one-shot R2V production card. Use
L40 for shorter tests, lower-risk 5s/720P jobs, or as a queue worker only after
another successful 15s stability test.

## Commands Used

Example 720P T2V:

```bash
cd /root/ComfyUI
/usr/bin/time -p python h3_runner.py t2v \
  --server http://127.0.0.1:8189 \
  --prompt "15-second premium bakery commercial for golden egg tarts, glossy flaky pastry, warm oven light, close-up macro shots, steam rising, smooth slow push-in camera, appetizing product hero, elegant food advertising, no text, no watermark" \
  --width 1344 --height 768 --duration 5 --steps 4 --turbo \
  --prefix video/test_t2v_720p_4step \
  --output-dir /root/ComfyUI/outputs_h3_tests
```

Example 1080P R2V:

```bash
cd /root/ComfyUI
/usr/bin/time -p python h3_runner.py r2v \
  --server http://127.0.0.1:8189 \
  --prompt "Premium food commercial guided by the reference image: chef hands making handmade steamed buns on a flour-dusted stainless counter, realistic warm kitchen lighting, macro closeups, gentle cinematic camera movement, appetizing product hero shot, no text, no watermark" \
  --ref-image /root/ComfyUI/test_assets/baozi_ref.png \
  --ref-image-size match \
  --width 1920 --height 1088 --duration 5 --steps 4 --turbo --turbo-low-vram \
  --prefix video/test_r2v_1080p_4step \
  --output-dir /root/ComfyUI/outputs_h3_tests
```
