# MiniMax H3 A100 Diagnostic - 2026-08-10

## CORRECTION - 2026-08-10 later the same day

**The conclusion below is wrong. Do not act on it.**

The same server was re-examined after a reboot. Findings:

- The GPU is healthy: uncorrected ECC aggregate `0`, remapped rows `0/0`,
  pending `No`, remapping failure `No`, and a 54 x 512MB VRAM write/read sweep
  returned zero mismatches.
- Plain torch math is clean: fp32/fp16/bf16 matmul and fp16 SDPA all finite.
- All six model files open and sample clean.
- The real fault was **cuDNN**. The cu130 attempt described below installed the
  whole CUDA 13 NVIDIA runtime, and rolling PyTorch back to cu126 did not remove
  it. `nvidia-cudnn-cu13 9.13.0.50` had overwritten `nvidia-cudnn-cu12 9.10.2.21`
  in the shared `site-packages/nvidia/cudnn/lib/` directory, so every convolution
  failed with `CUDNN_STATUS_NOT_INITIALIZED`. Sampling survived because it uses
  matmul and attention; `VAEDecode` died on its first convolution.

Fix applied: `pip uninstall -y nvidia-cudnn-cu13` then force-reinstall
`nvidia-cudnn-cu12==9.10.2.21`. cuDNN went `91300` -> `91002`, conv2d and conv3d
started working, and a 512x512 T2V probe produced real picture content
(within-frame Y range `235.00`).

So the recommendation below - require a CUDA 13 driver image - is backwards. The
`550.127.08` + cu126 combination is fine and is what every successful run used.
The damage came from introducing CUDA 13 packages onto a CUDA 12 host.

Unresolved: this does not prove the 2026-08-09 black clips had the same cause.
The symptoms differ - the failure found today is a hard error that produces no
file, while the 2026-08-09 runs produced files that were fully black. Re-run one
real production clip before assuming the black-video issue is closed.

See `SERVER_H3_RUNBOOK.md`, section 1, for the detection and repair procedure.

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
