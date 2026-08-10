# MiniMax H3 A100 Diagnostic - 2026-08-10

## CORRECTION - 2026-08-10, live session on the same server

**The hardware conclusion at the bottom of this file is wrong. Do not act on it.**
The server was re-examined over SSH after a reboot, with a seven-stage probe
ladder. Everything this file blames turned out to be healthy.

### What was measured, not guessed

| Check | Result |
| --- | --- |
| ECC uncorrected, aggregate (survives reboot) | `0` |
| Remapped rows correctable / uncorrectable | `0 / 0`, pending `No`, failure `No` |
| VRAM write/read sweep, 54 x 512MB on an idle card | `0` mismatches |
| fp32 / fp16 / bf16 matmul, fp16 SDPA | all finite, no NaN |
| All six model files | open and sample clean |
| Disk | 68 GB free, nothing truncated |

The GPU was never faulty and the weights were never corrupt.

### What was actually broken on 2026-08-10, and fixed

cuDNN. The cu130 attempt described below pulled the entire CUDA 13 NVIDIA
runtime, and rolling PyTorch back to cu126 did not remove those wheels. Both
variants install into the same `site-packages/nvidia/cudnn/lib/` directory, so
`nvidia-cudnn-cu13 9.13.0.50` had overwritten `nvidia-cudnn-cu12 9.10.2.21`,
leaving one `libcudnn.so.9` built for CUDA 13 on a CUDA 12.4 host.

Every convolution then failed with `CUDNN_STATUS_NOT_INITIALIZED`, on a
completely idle GPU with 39.0 GB free, so it was never a memory problem.
Sampling survived because it is matmul and attention; `VAEDecode` died on its
first convolution.

Fix applied:

```bash
pip uninstall -y nvidia-cudnn-cu13
pip install --force-reinstall --no-deps nvidia-cudnn-cu12==9.10.2.21
```

cuDNN `91300` -> `91002`, conv2d and conv3d restored.

### Verified working afterwards

| Probe | Within-frame Y range | Wall time | Result |
| --- | ---: | ---: | --- |
| T2V 512x512, 4 step, no turbo | 235.00 | ~30s | real content |
| T2V 1088x1920, 4 step, turbo | 244.00 | 8 min | real content |
| R2V 1088x1920, 4 step, turbo, 3 synthetic refs | 240.00 | 10 min | real content |

Black clips measure `0.00`. The native 1080 production path - resolution, Turbo
LoRA and reference conditioning - is confirmed working on this machine, and the
8 and 10 minute timings match section 10 of `SERVER_H3_RUNBOOK.md`.

### What this does NOT explain

**The 2026-08-09 black clips remain unexplained.** By this file's own ordering,
the black probes were run *before* the cu130 attempt, so the CUDA 13 wheels did
not exist yet when the black videos were produced. The cuDNN fault is a second,
later problem, not the original one.

The symptoms differ too. The 2026-08-09 runs produced playable files that were
uniformly black; the 2026-08-10 fault produces a hard error and no file at all.

The 2026-08-09 cause is still open. What is established is that the machine
produces real video now, and that the black-frame signature is a NaN latent
(constant `Y=16`, zero within-frame and across-frame variation), not a weak
render.

### Corrections to the recommendations below

- "Require CUDA Version 13.0 or higher" is backwards. Driver `550.127.08` with
  PyTorch cu126 is the combination every successful run used. The damage came
  from putting CUDA 13 packages on a CUDA 12 host.
- The `cu130 optimized CUDA operations` startup warning is cosmetic on this
  driver and was present during every successful run. Do not chase it.
- "Use the `compat5` sequences first on a corrected CUDA 13 / PyTorch cu130
  server" is void. There is no need for a cu130 server.
- The `*_ascii_rgb` sequences and `runtime_sanitized_refs/` were built on the
  theory that non-ASCII paths or RGBA references caused the black output. That
  theory is disproved: the failing beef references and the working duck-soup
  references are identical in mode and size (RGB 1080x1920), and RGBA product
  and logo images were used in the successful runs too. Those sequence files
  also still point at a `runtime_sanitized_refs/` directory that no longer
  exists, so they cannot run as written.

See `SERVER_H3_RUNBOOK.md`, section 1, for the detection and repair procedure,
and `server_scripts/diagnose_h3_black.sh` for the probe ladder.

---

## Summary

The rented A100 server did not produce usable new MiniMax H3 videos tonight.
Every generated beef probe failed the technical black-frame check before full beef
or kelp pork rib soup production was started.

No final beef or pork-rib soup clips were handed off because the candidates were
black videos.

## Server State Observed

- GPU: NVIDIA A100-PCIE-40GB
- Driver: 550.127.08
- `nvidia-smi` CUDA Version: 12.4
- Conda env: `/home/node/anaconda3/envs/comfy_h3_torch29_cu126`
- Starting torch state: `torch 2.9.1+cu126`, `torch.version.cuda == 12.6`
- ComfyUI API: `http://127.0.0.1:8189`

ComfyUI on cu126 starts, but the startup log warns:

```text
WARNING: You need pytorch with cu130 or higher to use optimized CUDA operations.
```

For Turbo runs, ComfyUI then logs NaN values from the first sampler step:

```text
denoised_rms=nan
video: x_rms=nan v_rms=nan
audio: x_rms=nan v_rms=nan
```

The resulting MP4s are about 51-52 kb/s and are fully black.

## Probes Run

- `beef_probe_ascii_compat_001`
  - Turbo 4-step, RGB/ASCII product refs, current 3-shot prompt
  - Output: black for full 5.125s

- `beef_probe_compat5_001`
  - Turbo 4-step, old successful 5-beat prompt rhythm
  - Output: black for full 5.125s

- `beef_probe_fresh_compat5_001`
  - Same as above after a full ComfyUI restart
  - Output: black for full 5.125s

- `beef_probe_base4_001`
  - Turbo disabled, base model at 4 steps
  - Output: black for full 5.125s
  - This avoided Turbo-specific NaN lines but 4 base steps still did not produce a usable video.

All black checks used `ffmpeg blackdetect` and showed:

```text
black_start:0 black_end:5.125 black_duration:5.125
```

## cu130 Attempt

I installed:

```text
torch==2.9.1+cu130
torchvision==0.24.1+cu130
torchaudio==2.9.1+cu130
```

The install succeeded, but ComfyUI could not start because the machine driver is
too old for CUDA 13.0:

```text
RuntimeError: The NVIDIA driver on your system is too old (found version 12040).
```

I then rolled the environment back to:

```text
torch==2.9.1+cu126
torchvision==0.24.1+cu126
torchaudio==2.9.1+cu126
```

ComfyUI was restarted and the queue was available again, but cu126 remains a
black-output environment for H3 Turbo on this image.

## Practical Conclusion

Do not rent this exact image for MiniMax H3 Turbo 4-step production:

- Driver 550.127.08 / CUDA 12.4 is too old for PyTorch cu130.
- PyTorch cu126 starts but disables the optimized H3 CUDA backend.
- In this state, 4-step H3 generation returns black videos.

For the next rental, require one of these:

- `nvidia-smi` reports CUDA Version 13.0 or higher, then install/use PyTorch cu130.
- Or provider image already has MiniMax H3 ComfyUI working with cu130 and no startup warning about needing cu130.
- If the provider only offers CUDA 12.x driver images, do a one-clip blackdetect probe before renting long time.

## Reusable Assets Added

New prompt files:

- `prompts/h3_3x5_1080_compat/shuizhu_beef_roll_clip_01.md`
- `prompts/h3_3x5_1080_compat/shuizhu_beef_roll_clip_02.md`
- `prompts/h3_3x5_1080_compat/shuizhu_beef_roll_clip_03.md`
- `prompts/h3_3x5_1080_compat/kelp_pork_rib_soup_clip_01.md`
- `prompts/h3_3x5_1080_compat/kelp_pork_rib_soup_clip_02.md`
- `prompts/h3_3x5_1080_compat/kelp_pork_rib_soup_clip_03.md`

New sequence files:

- `sequences/shuizhu_beef_roll_3x5_1080_ascii_rgb.json`
- `sequences/shuizhu_beef_roll_3x5_1080_compat5_ascii_rgb.json`
- `sequences/kelp_pork_rib_soup_3x5_1080_ascii_rgb.json`
- `sequences/kelp_pork_rib_soup_3x5_1080_compat5_ascii_rgb.json`
- `sequences/shuizhu_beef_roll_probe_clip01_1080_ascii_rgb.json`
- `sequences/shuizhu_beef_roll_probe_clip01_1080_compat5_ascii_rgb.json`
- `sequences/shuizhu_beef_roll_probe_clip01_1080_base4_ascii_rgb.json`

Use the `compat5` sequences first on a corrected CUDA 13 / PyTorch cu130 server,
then run a single beef probe and check for non-black output before launching the
full beef and kelp pork rib soup batches.
