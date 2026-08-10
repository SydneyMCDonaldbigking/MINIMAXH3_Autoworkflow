# Current Working Workflow

Last verified end to end on 2026-08-10 against an A100-PCIE-40GB, driver
`550.127.08`, conda env `comfy_h3_torch29_cu126`, PyTorch `2.9.1+cu126`,
ComfyUI `0.30.2`.

This is the single operational path. Everything else in this repo is either
detail behind one of these steps or a record of how we got here. Where a claim
is marked UNVERIFIED, it has not been demonstrated and should not be trusted
until it is.

## What is actually established

| Claim | Status |
| --- | --- |
| Native 1088x1920, 4-step Turbo, R2V with references produces real video | verified 2026-08-10 |
| Driver 550.127.08 + PyTorch cu126 is a good combination | verified, and it is what every successful run has used |
| A `cu130 optimized CUDA operations` startup warning is harmless here | verified, present during every successful run |
| Black clips are a NaN latent, not a weak render | verified, constant `Y=16`, zero variation |
| The 2026-08-09 black clips have an explanation | **NO. Still unknown.** The cuDNN fault found on 2026-08-10 came later and cannot explain them |
| The Ref2VA prompt format produces better video than the old prose format | **UNVERIFIED.** Format and a machine repair changed together |
| The rewritten beef clip 01 prompt fixes the jitter | **UNVERIFIED.** Not generated even once |

## 0. Rent a machine

Ask for a CUDA 12.x driver image. Do **not** pay extra for CUDA 13 - the
2026-08-09 diagnostic recommended that and it was wrong.

Install your SSH key before anything else. Do not use password auth for the
tooling; `cluster_runner.py` and the scripts assume key auth.

```bash
ssh -p PORT root@HOST "mkdir -p ~/.ssh && chmod 700 ~/.ssh && echo 'YOUR_PUBLIC_KEY' >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys && echo INSTALLED"
```

Note: `cat key.pub | ssh ...` fails on Windows OpenSSH. The pipe takes stdin, so
the password prompt never gets the terminal. Use the inline form above.

## 1. Preflight before spending GPU time

```bash
python cluster_runner.py check --servers servers.yaml --upload-runner --start-comfy
```

This now compares the remote `h3_runner.py` against the local one by sha256 and
prints `STALE` if they differ. Existence alone is not enough: on 2026-08-10 a
stale remote copy accepted a job and then failed on an argument the local
version had added, wasting rental time.

## 2. Health ladder, free stages first

```bash
scp -P PORT server_scripts/diagnose_h3_black.sh root@HOST:/root/ComfyUI/server_scripts/
ssh -p PORT root@HOST 'cd /root/ComfyUI && MAX_STAGE=4 bash server_scripts/diagnose_h3_black.sh'
```

Stages 1-4 cost nothing and take about two minutes: GPU inventory and disk, ECC
and Xid, torch numerics **including convolution**, and model file integrity.

The convolution check is the important one. On 2026-08-10 matmul and attention
were perfectly healthy while every convolution failed, because CUDA 13 wheels
left behind by a cu130 rollback had overwritten `nvidia-cudnn-cu12` in the
shared `site-packages/nvidia/cudnn/lib/` directory. Sampling ran, `VAEDecode`
died. Repair is in `SERVER_H3_RUNBOOK.md` section 1.

If stages 1-4 are clean, run the paid stages:

```bash
ssh -p PORT root@HOST 'cd /root/ComfyUI && bash server_scripts/diagnose_h3_black.sh'
```

Stage 5 is a 512x512 smoke test, about 30 seconds. Stages 6 and 7 are native
1088x1920 T2V and R2V, about 8 and 10 minutes. Skip 6 and 7 once you trust a
machine; never skip stage 5.

## 3. Generate references before touching the A100

```powershell
.\generate_reference_assets.ps1 -PrintOnly   # cost preview
.\generate_reference_assets.ps1
```

Every 3x5s ad needs its protagonist, scene, prep-state, mid-state and
final-state references generated first. The sequence JSONs refuse to run when
these are missing, which is deliberate: A100 time is far more expensive than
Seedream time. See `MINIMAX_H3_3X5_NATIVE1080_WORKFLOW.md`.

The prep-state reference carries real weight. It exists so H3 does not have to
perform knife work on camera, which it does badly - see step 5.

## 4. Generate

```bash
python h3_sequence_runner.py run \
  --sequence sequences/<ad>_3x5_1080.json \
  --server http://127.0.0.1:8189 \
  --output-root sequence_outputs
```

Production settings, identical across all four ads and not to be varied casually:
`r2v`, `1088x1920`, `5.0s`, `4` steps, turbo on, `turbo_low_vram` on, no audio,
`ref_image_size: match`. About 9-10 minutes per clip, 25-30 minutes for three
clips plus stitching.

Final crop to exactly `1080x1920` is `crop=1080:1920:4:0`. This is a native-detail
render plus a small side crop, not an upscale.

## 5. Write prompts to the official format, with our house rules on top

The container is the official MiniMax Ref2VA format from
`MiniMax-AI/MiniMax-H3`, `skills/h3-prompt-writing`: six plain labeled sections
in order, `<Picture N>` bound positionally to `ref_images`, `[Shot N]` headings
with `At MM:SS.mmm` cut times.

The content rules are ours, derived from measuring our own output, because the
official spec was written for full-step inference and we run a 4-step distilled
LoRA. All of them live in `MINIMAX_H3_3X5_NATIVE1080_WORKFLOW.md`:

- every beat is a directional action that completes inside its window, never a
  state to hold;
- one action, one actor, per shot;
- commit the camera to a definite move or lock it off explicitly, never hedge;
- no tight close-ups of a hand working a tool;
- name an ingredient's distinguishing features and rule out the confusable one.

Watch the reference-order trap: clips using `use_previous_last_frame_as_ref`
shift every label by one, because the runner prepends the carried frame.

## 6. Gate every clip before assembling

```bash
python check_clip_quality.py sequence_outputs/<id>/<run>/clip-01/*.mp4
```

Fails on a constant frame (the NaN signature) and on camera jitter above 20%
overall or 25% in the last third. It deliberately does not gate on sharpness:
the clip we judged bad measured *sharper* per frame than the clip we judged
good, so sharpness does not separate the cases.

Do not stitch a sequence until every clip passes.

## 7. Brand rules

Non-negotiable, from `BRAND_ASSETS.md`. English-region default is
`company_logo/AGO.png`, brand written as `ASIAN GROCER ONLINE / POWERED BY
UMALL`. `UMALL.png` only when Chinese-region or mother-brand output is asked for
explicitly. The logo may appear only as a real printed prop inside the scene,
never as an overlay, and never fixed up locally after the fact. No invented
prices, UI, store claims or availability.

## Open items

- The 2026-08-09 black-video cause is unknown. Run one clip and gate it before
  committing to a batch on any machine.
- The rewritten `prompts/h3_3x5_1080/shuizhu_beef_roll_clip_01.md` has never
  been generated. Validate it before converting the other 17 prompt files.
- `sequences/*_ascii_rgb.json` point at a deleted `runtime_sanitized_refs/`
  directory and are based on a disproved theory. They cannot run as written.
- Other `*-cu13` wheels remain installed on that server image. Only cuDNN was
  repaired, because that was the one blocking generation.
