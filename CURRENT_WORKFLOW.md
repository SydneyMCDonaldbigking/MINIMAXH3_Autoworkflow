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
| The 2026-08-09 black clips have an explanation | **YES, found later on 2026-08-10.** The A100 corrupts bf16 matrix multiplication non-deterministically. H3's Turbo LoRA runs in bf16, so sampling goes NaN and decodes to a constant frame. See `H3_A100_DRIVER_DIAGNOSTIC_2026-08-10.md` |
| The Ref2VA prompt format produces better video than the old prose format | **UNVERIFIED.** Format and a machine repair changed together |
| The rewritten beef clip 01 prompt fixes the jitter | **UNVERIFIED.** Not generated even once |

## 0. Rent a machine, then test the GPU before anything else

Ask for a CUDA 12.x driver image. Do **not** pay extra for CUDA 13 - the
2026-08-09 diagnostic recommended that and it was wrong.

**Test bf16 matrix multiplication before you trust a card.** A faulty A100 cost
this project two days of misdiagnosis: it corrupts bf16 GEMM non-deterministically
while fp32, fp16 and every other check stays clean, and H3's Turbo LoRA runs in
bf16. Symptoms are black clips that arrive intermittently with no configuration
change.

```bash
bash server_scripts/check_bf16_mma.sh
```

It records the GPU UUID and serial, builds a native `sm_80` cubin that calls the
tensor-core instruction directly, and reports bf16 against fp16. **bf16 must say
PASS.** A failing machine looks like this:

```text
bf16   MACs=2.097e+11  bad=40  inf=40  rate/MAC=1.91e-10  FAIL
fp16   MACs=2.097e+11  bad=0   inf=0   rate/MAC=0         PASS
```

Reject the machine on any bf16 failure, and do not start debugging prompts,
models or PyTorch. Because the test bypasses PyTorch, cuBLAS and PTX JIT
entirely, a failure cannot be argued away as a software problem.

If a provider insists the card is fine because ECC is clean, ECC covers memory
and not the tensor-core datapath. The fp16 line is the argument that this is
neither a driver installation nor a library problem: same instruction family,
same workload, one dtype clean and the other not.

Always record the UUID and serial the script prints. Two instances were compared
on 2026-08-10 without them, which made it impossible to tell whether the second
machine was even a different card.

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
`r2v`, `1088x1920`, `5.0s`, **`8` steps**, turbo on, `turbo_low_vram` on, no
audio, `ref_image_size: match`. About 13 minutes per clip, 39 minutes for three
clips plus stitching, roughly $0.46 of A100 time at $0.713/hr.

Four steps is not usable: whole objects render semi-transparent and doubled. See
the step comparison in `MINIMAX_H3_3X5_NATIVE1080_WORKFLOW.md`.

Sampling costs about 83 seconds per step on a 40 GB A100 **with no attention
acceleration in the graph**. `--lowvram` and `NORMAL_VRAM` measured 83.7 and
86.0 s/it, so keeping weights resident buys nothing; the cost is not weight
streaming. Keep `--lowvram` for the headroom.

This was previously written here as "the floor", which was wrong. That pair of
measurements only rules out weight movement. The graph runs plain attention with
no Sage, no chunked feed-forward and no sigma shift, and none of those has been
tested. See `EXPERIMENT_PLAN_ACCELERATION.md`.

Final crop to exactly `1080x1920` is `crop=1080:1920:4:0`. This is a native-detail
render plus a small side crop, not an upscale.

## 5. Write prompts to the official format, with our house rules on top

For every new cooking dish, first apply
`prompts/COOKING_PROMPT_PRODUCTION_STANDARD.md`. The prompt package must be
recipe-grounded: search real recipes, record source URLs and production facts,
distill them into a `recipe_bible.md`, and save the H3 prompts plus English
Instagram Reels caption/subtitles under the real `sequence_outputs/<dish>/...`
output tree.

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

**A pass is necessary, not sufficient, and the clearest proof arrived
2026-08-11.** A 6-step clip was 33% faster, passed the gate, and scored a
*better* flip rate than the 8-step control (1.6% vs 2.5%). On frames 40, 60, 75
and 100 the napa cabbage was whole and uncut, destroying the one thing clip 01
exists to prove. The gate measures luminance and motion; it cannot read the
picture. **Look at frames 40, 60, 75, 100 of every clip before assembling.**

## 6b. Audio

H3 samples audio in the same pass as video. `--no-audio` only discards it at save
time, so keeping it costs nothing: re-rendering the identical clip with audio on
took 35 s against 907 s, because ComfyUI reused the cached sampling and only had
to decode the audio VAE and mux. Verified 2026-08-11 by md5-comparing decoded
frames of the two outputs.

To keep it through stitching a sequence needs both:

```json
"defaults": { "no_audio": false },
"final":    { "keep_audio": true }
```

The result is AAC stereo at 32 kHz, matching the video duration, and it survives
the concat and the final crop. Every ad before this date was hand-dubbed over
audio the pipeline had already generated and thrown away.

## 7. Brand rules

Non-negotiable, from `BRAND_ASSETS.md`. English-region default is
`company_logo/AGO.png`, brand written as `ASIAN GROCER ONLINE / POWERED BY
UMALL`. `UMALL.png` only when Chinese-region or mother-brand output is asked for
explicitly. The logo may appear only as a real printed prop inside the scene,
never as an overlay, and never fixed up locally after the fact. No invented
prices, UI, store claims or availability.

**A product photo of a packaged product is a text hazard, and negatives will not
save you.** Half our product images are retail packs carrying a UMALL label, a
nutrition panel and a barcode. H3 cannot render small text legibly at
`1088x1920`, so whatever it does with that label comes out as pseudo-text - the
same failure that made Seedream write "UMANE". Three of the six 2026-08-11 ads
shipped with a fake label and a fake barcode in the opening shot.

`<Picture 5>` is marked `fully_preserved`. That marker beats any wording in the
negatives list, so the fix is not to forbid what the image contains:

- **Wrong, and what we shipped:** describing wings "tipped out of their
  packaging, no bag or wrapper anywhere in frame" while the image is a sealed
  bag. The description contradicts the reference and the reference wins.
- **Also wrong:** naming the tray but not the label, which leaves the model to
  invent one.
- **Worst:** spelling out the label text for it to render, which is asking
  directly for the failure.
- **Right:** describe what the photograph actually shows, then control the
  *framing* - "frame the meat and the bare tray rim only: the printed label and
  barcode sit outside the shot, and no text of any kind appears in frame".

Better still, crop the reference so only food is in it. A reference that cannot
show text cannot have its text invented.

## Open items

- The 2026-08-09 black-video cause is unknown. Run one clip and gate it before
  committing to a batch on any machine.
- The rewritten `prompts/h3_3x5_1080/shuizhu_beef_roll_clip_01.md` has never
  been generated. Validate it before converting the other 17 prompt files.
- `sequences/*_ascii_rgb.json` point at a deleted `runtime_sanitized_refs/`
  directory and are based on a disproved theory. They cannot run as written.
- Other `*-cu13` wheels remain installed on that server image. Only cuDNN was
  repaired, because that was the one blocking generation.
