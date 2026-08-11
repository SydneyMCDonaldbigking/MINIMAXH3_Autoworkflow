# MiniMax H3 A100 Migration Cheat Sheet

Purpose: future Codex tasks can bring up a fresh China GPU server, run MiniMax
H3 one-shot ads without the ComfyUI GUI, and know which card to trust.

Do not store SSH passwords or API keys in this file.

## Production Decision

- Main worker: A100 40G.
- Current stable production spec: `r2v`, `768x1344`, `duration 15`, `steps 4`,
  Turbo LoRA. This is not native 1080p.
- Measured A100 time: about 850s per 15.084s vertical ad.
- Native vertical 1080p probe: `1088x1920`, `duration 15`, `steps 4`, Turbo
  LoRA, `--turbo-low-vram` OOMed at sampler after about 25s.
- Do not report upscaled `1080x1920` files as native 1080p H3 output.
- L40 48G can run 5s 720P tests, but failed the 15s vertical R2V production
  probe after sampling, during VAE decode/save.
- Run one H3 job per GPU. For batch production, scale with more servers/GPUs.

## Clean Environment

Use:

```text
OS: Ubuntu 22.04
Conda: /home/node/anaconda3
Env: comfy_h3_torch29_cu126
Python: 3.12
PyTorch: 2.9.1+cu126
ComfyUI: /root/ComfyUI, v0.30.2
API: 127.0.0.1:8189
Startup flag: --lowvram
```

If one server already has the env, prefer `conda-pack` and `scp` to migrate it
to the next server. It was faster than rebuilding PyTorch wheels on the L40
server during the 2026-08-09 run.

## Required Files

Model files:

```text
/root/ComfyUI/models/diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors
/root/ComfyUI/models/diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors
/root/ComfyUI/models/text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors
/root/ComfyUI/models/vae/minimax_h3_video_vae_fp16.safetensors
/root/ComfyUI/models/vae/minimax_h3_audio_vae_fp32.safetensors
/root/ComfyUI/models/loras/minimax_h3_turbo_v4_step600_ema.safetensors
```

Local repo files to copy into `/root/ComfyUI`:

```text
h3_runner.py
server_scripts/
```

China download route:

```bash
export HF_ENDPOINT=https://hf-mirror.com
export HF_HUB_DISABLE_XET=1
```

For large model files, `aria2c` from `hf-mirror.com` was the most reliable
download path in this run.

## Start And Verify

```bash
cd /root/ComfyUI
source /home/node/anaconda3/etc/profile.d/conda.sh
conda activate comfy_h3_torch29_cu126
nohup python main.py --listen 127.0.0.1 --port 8189 --lowvram > comfyui_h3_torch29_cu126.log 2>&1 &
echo $! > comfyui_h3_torch29_cu126.pid
curl -fsS http://127.0.0.1:8189/system_stats
```

Verify nodes:

```bash
python - <<'PY'
import json, urllib.request
obj=json.load(urllib.request.urlopen("http://127.0.0.1:8189/object_info"))
for n in ["MiniMaxH3TurboLoRA", "MiniMaxH3TurboSampler", "MiniMaxH3ImageToVideo", "MiniMaxH3ReferenceToVideo"]:
    print(n, "OK" if n in obj else "MISSING")
PY
```

## First-Frame And References

Use `viral-social-remix` style prompting for the storyboard and opening frame.

Default AGO / English-region brand asset:

```text
company_logo/AGO.png
```

Current image route:

- Use OpenRouter `bytedance-seed/seedream-4.5`, `resolution=2K`,
  `aspect_ratio=9:16`, then reframe to `1080x1920`.
- Seedream is cheap and fast enough for scene/person/action reference frames.
- Do not ask Seedream to generate exact logo text. It can misspell brand text.
- Generate clean no-readable-text scene references, then pass the official
  `company_logo/AGO.png` separately to H3.

The company logo is allowed as a brand reference. In H3 prompts, render it as a
real printed package, tabletop sign, store sign, or physical brand card when
natural. Avoid floating overlay logos.

MiniMax H3 R2V reference order:

1. high-quality opening frame;
2. product/source image;
3. company logo or official brand lockup;
4. optional scene, model, hands, package, or style references.

## A100 Production Command

```bash
cd /root/ComfyUI
source /home/node/anaconda3/etc/profile.d/conda.sh
conda activate comfy_h3_torch29_cu126

/usr/bin/time -p python h3_runner.py r2v \
  --server http://127.0.0.1:8189 \
  --prompt "<15s storyboard prompt>" \
  --ref-image /root/ComfyUI/test_assets/<opening>.png \
  --ref-image /root/ComfyUI/test_assets/<product>.png \
  --ref-image /root/ComfyUI/test_assets/AGO.png \
  --ref-image-size match \
  --width 768 --height 1344 \
  --duration 15 \
  --steps 4 \
  --turbo \
  --prefix video/<job>_15s_vertical_r2v \
  --output-dir /root/ComfyUI/outputs_h3_jobs/<job> \
  --poll 5 \
  --timeout 21600
```

After generation:

```bash
ffprobe -hide_banner -v error -show_entries format=duration,size:stream=width,height,codec_name,avg_frame_rate -of default=noprint_wrappers=1 /root/ComfyUI/outputs_h3_jobs/<job>/<file>.mp4
tar -czf /root/<job_outputs>.tar.gz /root/ComfyUI/outputs_h3_jobs/<job>
```

Download the tarball with `scp`, extract it under local `outputs/`, and report
the local MP4 path for user review.
