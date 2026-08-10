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

### ROOT CAUSE FOUND, later on 2026-08-10: the GPU corrupts bf16 GEMM

The cuDNN fault above was real but was only a second, later problem. The actual
cause of the black videos, on 2026-08-09 and again on 2026-08-10, is that
**this A100 produces corrupt results for bf16 matrix multiplication**.

Measured on an otherwise idle card:

| Operation | Result |
| --- | --- |
| fp32 matmul, 4096x4096 | absmax `339.9`, correct |
| **fp16** matmul, same shapes and data | absmax `340`, **correct** |
| bf16 **elementwise** multiply and sum | absmax `288`, **correct** |
| **bf16 matmul**, same shapes and data | **909-1338 `inf` values, finite absmax `2.8e+38`** |

The same input run four times gave inf counts of `1079, 983, 1022, 1053`. It is
**non-deterministic**, which is what rules out a software bug.

Every software explanation was eliminated: the process loads the correct cu12
libraries (checked in `/proc/PID/maps`), force-reinstalling `nvidia-cublas-cu12`
changed nothing, `CUBLAS_WORKSPACE_CONFIG` changed nothing, switching between
the cuBLAS and cuBLASLt backends changed nothing, and toggling
`allow_bf16_reduced_precision_reduction` changed nothing.

The corruption scales with sequence length, tested at H3's own hidden dimension
of 5376:

```text
(256x5376)@(5376x5376)   ->   46 inf
(1024x5376)@(5376x5376)  ->  223 inf
(4096x5376)@(5376x5376)  -> 1338 inf
```

MiniMax H3's Turbo LoRA runs in bfloat16, so its transformer projections land
squarely on the broken path, and native `1088x1920` at 124 frames is the longest
sequence in the pipeline and therefore the most exposed configuration.

Confirmed end to end. A full three-clip beef sequence run at native resolution
produced three black clips, `0/3` through `check_clip_quality.py`, and the
ComfyUI log shows the mechanism directly:

```text
video_rms=0.9999 audio_rms=1.0102    <- first sampler call is clean
video_rms=nan audio_rms=nan          <- corrupt from there on
```

That is the same line the original diagnostic recorded on 2026-08-09.

### The 2026-08-09 mystery, resolved

The open question was what changed between the good duck soup run at 19:45 and
the black beef runs at 22:37, given identical configuration on the same machine.

**Nothing changed, and nothing needed to.** The corruption is intermittent. Some
runs get a clean sampling trajectory and produce real video, as one beef clip did
on 2026-08-10 at native resolution; others hit a corrupted GEMM early and go NaN.
ECC counters stay at zero throughout because ECC protects memory, not the
tensor-core compute path.

Do not debug prompts, references, resolution or Turbo settings on this machine.
`--fp16-unet` is not a workaround: H3's int8 weights need bf16's exponent range
and fp16 produced an immediately black clip.

### Proven at the instruction level, software fully exonerated

A second instance was provisioned by full-disk copy and failed identically, so
the first conclusion of "replace this one card" was wrong. Everything below was
then eliminated by measurement, not argument:

| Suspicion | How it was ruled out |
| --- | --- |
| That one A100's silicon | New instance, same disk, identical failure |
| cu13 wheels shadowing cu12 | `/proc/PID/maps` shows only cu12 loaded |
| cuBLAS version | 12.4 via LD_PRELOAD and 12.6 both fail |
| cuBLAS vs cuBLASLt | Both fail when selected explicitly |
| bf16 reduced-precision reduction | Fails with the flag on and off |
| JIT / compile caches | Cleared, plus `CUDA_CACHE_DISABLE=1`; still fails |
| Clock or power margin | Locked to 900 MHz; still fails |
| Shape alignment or tiling heuristics | N sweep 4080-4112 all fail |
| Uninitialized memory | Bad values are only `0x7f80` and `0xff80`, exact bf16 ±Inf |
| Deterministic kernel indexing bug | 50 runs on fixed A and B: intersection 0, Jaccard 0.000000 |
| MIG or vGPU slicing | MIG Mode Disabled, full physical GPU |

The decisive test calls the Ampere tensor-core instruction directly, compiled to
a native `sm_80` cubin with no PTX JIT, bypassing PyTorch, ATen, cuBLAS,
cuBLASLt, Triton and Inductor. Same kernel, same `HMMA.16816` instruction, same
shapes and iteration count, only the input dtype differs:

```text
bf16: 2.097e+11 MACs -> 40 wrong accumulators, all inf, 1.91e-10 per MAC   FAIL
fp16: 2.097e+11 MACs ->  0 wrong accumulators                              PASS
```

Inputs are all `1.0` and the expected accumulator is `320000`, so no legitimate
path reaches infinity. The reproducer is `server_scripts/bf16_mma_acceptance.cu`,
run by `server_scripts/check_bf16_mma.sh`.

The fault is therefore in GPU execution, the driver, or the virtualization layer,
and not in any user-space library. What is still not separated is silicon from
driver `550.127.08`, because both instances ran the same driver and the original
GPU UUID was never recorded. Record `nvidia-smi --query-gpu=uuid,serial` on every
machine from now on; `check_bf16_mma.sh` does it automatically.

Send providers the fp16-versus-bf16 pair. It is not arguable: identical
instruction family, identical workload, one dtype clean and the other not, with
ECC at zero throughout because ECC covers memory and not the tensor-core
datapath.

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
