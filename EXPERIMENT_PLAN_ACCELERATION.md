# Acceleration and sampling experiments

Written 2026-08-11 as a plan. Run the same day on an A100 PCIE 40 GB and then an
H100 SXM 80 GB. **Results are at the top; the plan below is kept because two of
its four questions are still open and the reasoning still holds.**

## Results, 2026-08-11

Same clip throughout: `shuizhu_beef_roll_clip_01`, seed `202608090301`, six
references in sequence order, `1088x1920`, 5.0s, 8 steps, turbo.

| Run | Card | Wall | vs that card's baseline | $/clip |
| --- | --- | ---: | ---: | ---: |
| baseline | A100 PCIE 40 GB | 907 s | - | $0.211 |
| baseline | H100 SXM 80 GB | 471 s | - | $0.302 |
| **+ Sage attention (fp8)** | H100 SXM | **401 s** | **-15%** | **$0.257** |
| + Sigma Shift 12.0 | A100 PCIE | 862 s | no-op, see below | - |
| 6 steps | A100 PCIE | 602 s | -33%, **rejected** | - |

**Sage attention is the only real win of the day.** 15% off every clip on Hopper,
with QC metrics unchanged (flip rate 2.5% -> 1.6%) and no ghosting or content
error visible on frames 40, 60, 75 and 100. Power draw goes from 333 W to 606 W,
which is the fp8 kernels actually loading the tensor cores. Getting there needs
three things that are easy to miss, all covered in `H200_DAY_PLAN.md`: KJNodes
for `PathchSageAttentionKJ`, SageAttention **2.x built from source** because PyPI
ships 1.x without the `sageattn_qk_int8_pv_*` entry points, and **sm_89 or newer**
- on the A100 this experiment could not be run at all.

**Six steps is rejected, and the way it failed is the point.** It was 33% faster
and `check_clip_quality.py` *passed* it with a better flip rate than the 8-step
control (1.6% vs 2.5%). Looking at frames showed the napa cabbage rendered
**whole and uncut**, destroying the one thing clip 01 exists to prove. The gate
has no semantic or ghosting detector and never will catch this. Look at frames.

**Sigma shift was not actually tested.** `MiniMaxH3SigmaShift` declares
`shift_video` default 12.0, and the sampler is *already* running shift 12. Proof:
the ComfyUI log prints its sigmas, and feeding `s' = k*s/(1+(k-1)*s)` with k=12
reproduces `[1.0, 0.9882, 0.973, 0.9524, 0.9231, 0.878, 0.8, 0.6316, 0.0]`
exactly. Setting the node to 12.0 changes nothing, and the output was
**pixel-identical to baseline** on decoded frames. The 862 s against 907 s was a
warm weight cache, not a speedup, and would have been reported as a 5% win if the
md5s had not been checked. A real test needs k != 12; k=3.0 crashed
`SamplerCustomAdvanced` with "size of tensor a (2) must match tensor b (3)" after
461 s of work, which is still unexplained.

**The full Unified chain is still untested.** `JR_H3_UnifiedAcceleration` also
delegates Sol-Attn to `SolAttnPatch` from `ComfyUI-SolAttn_triton`, which was not
installed. Worth noting as a design error on our side: `h3_accel_runner.py`'s
`--accel` turns on Sage *and* Sol-Attn together, so experiment 2 could not be run
in isolation until `--accel-set enable_sol_attn=false` was passed. A flag that
means "the author's defaults" and a flag that means "one factor" are not the same
flag.

### Still open

1. Sigma shift at a value other than 12, and why 3.0 crashes the sampler.
2. The full Unified chain, after installing `ComfyUI-SolAttn_triton`.
3. Whether Sage attention holds up across all three clip shapes, not just clip 01.
4. Wiring Sage into `h3_sequence_runner.py`, which still calls `h3_runner.py` and
   therefore produces at 471 s/clip rather than 401 s.

---

The original plan follows.

## Where this came from

`Goldlionren/ComfyUI_JR_MiniMaxH3Node`, a node suite for MiniMax H3. Its author
publishes a full pipeline and, unusually, its limitations - the docs state
outright that selecting a cache profile does not guarantee a speedup, and mark
Adaptive Cache and Sol-Attn as experimental with no per-prompt consistency
guarantee.

Their graph:

```text
Load MiniMax H3 Model
  -> MiniMax H3 Turbo LoRA
  -> Reserved VRAM
  -> H3 Unified Acceleration        (Sage -> Low VRAM Attention -> Chunk FFN -> Sol)
  -> MiniMax H3 Sigma Shift
  -> Sampler
  -> VAE Decode
  -> RTX Upscale / Refine
```

Their measurement, RTX 4080 SUPER 16 GB: a 15-second video at about 0.8 MP,
full workflow about 8 minutes, then upscaled to about 2.4 MP.

Ours, A100 40 GB: a 15-second ad at 2.09 MP (`1088x1920`, three 5s clips),
39 minutes, 83 s per sampling step.

Do not read that as "a 4080 beats an A100". Their frame is a quarter the pixels,
and attention is quadratic in sequence length, so the comparison is not linear
and probably favours them by construction. What it does establish is that a
serious H3 pipeline runs an acceleration stack and a sigma shift, and **our graph
has neither**. That gap is worth measuring.

The RTX upscale tail is not interesting to us: upscaling from a lower native
resolution was tried before and the quality was not acceptable. The value is
everything before the Sampler.

## What we are testing and why

**Sigma shift** changes the noise schedule. At 4-8 steps the schedule matters a
lot, so this is the one most likely to pay: we currently buy our way out of
ghosting by doubling steps from 4 to 8, which doubles cost. If a shift gets
8-step quality at 5 or 6 steps, that is a permanent saving on every clip.

**Sage attention and the rest of the Unified chain** attack the actual
bottleneck. A `1088x1920` by 124-frame latent is a very long sequence and
attention is quadratic in it.

**Reserved VRAM** is likely irrelevant here. We already measured that weight
residency changes nothing (83.7 vs 86.0 s/it), so it is last on the list.

## Baseline

Established 2026-08-10 on a verified-healthy A100 40 GB. **Re-measure it on the
H200 before anything else** - a different card invalidates the timings, though
not the quality numbers.

| | Value |
| --- | --- |
| Config | `r2v`, `1088x1920`, 5.0s, 8 steps, turbo, `turbo_low_vram`, no audio |
| Sampling | 83 s/it, 11:08 for 8 steps |
| Clip wall time | 13 min |
| Camera flip rate | 2.5% overall, 5.0% opening third, 0.0% closing |
| Ghosting | none |

## Held constant across every run

Changing any of these invalidates the comparison:

- seed `202608090301`
- prompt `prompts/h3_3x5_1080/shuizhu_beef_roll_clip_01.md`
- the same six references in the same order
- `1088x1920`, 5.0s, turbo on
- the same machine, one run at a time, no concurrent jobs

Note that acceleration changes numerics, so the same seed will **not** give a
pixel-identical result. Compare perceptually and by metric, never by pixel diff.

## Phase 1: one factor at a time

Each run is one clip. Isolating first means a later combination that fails can be
attributed.

| # | Change from baseline | Question |
| --- | --- | --- |
| 1 | nothing, re-baseline on H200 | what is s/it on this card |
| 2 | + Sage attention only | does it cut s/it, does quality hold |
| 3 | + full Unified chain | does the rest add anything over Sage alone |
| 4 | + Sigma Shift only, still 8 steps | does quality improve at fixed cost |

## Phase 2: only if Phase 1 earns it

If run 4 shows a quality gain, the real prize is fewer steps:

| # | Change | Question |
| --- | --- | --- |
| 5 | Sigma Shift, 6 steps | does it match the 8-step baseline |
| 6 | Sigma Shift, 4 steps | does it match, or does ghosting return |

If runs 2 or 3 cut s/it, stack the winners:

| # | Change | Question |
| --- | --- | --- |
| 7 | best acceleration + lowest passing step count + shift | the candidate production config |

Run 7 is the only one that has to survive a full three-clip ad before it replaces
the current settings.

## How each run is judged

**Speed**: s/it from the ComfyUI log, and total prompt execution time.

**Camera stability**: `python check_clip_quality.py <clip>.mp4`. Baseline is
2.5% overall and 5.0% in the opening third. Note the tool counts shot cuts as
motion, so all three-shot clips carry the same inflation and only relative
comparison is meaningful.

**Ghosting**: by eye, on frames 40, 60, 75 and 100. **The gate cannot detect
this.** It passed a 4-step clip whose cutting board was transparent. Any
acceleration that trades away structural coherence will show here and nowhere
else.

**Content**: the napa cabbage must stay napa, the knife must stay intact, the
brand card must stay legible. These were the failure modes that 8 steps fixed.

## Installing the node suite

```bash
cd /root/ComfyUI/custom_nodes
git clone https://github.com/Goldlionren/ComfyUI_JR_MiniMaxH3Node.git
/venv/main/bin/pip install -r ComfyUI_JR_MiniMaxH3Node/requirements.txt
```

Then restart ComfyUI and confirm the nodes register, the same way we checked the
Turbo nodes:

```bash
python -c "
import json,urllib.request
obj=json.load(urllib.request.urlopen('http://127.0.0.1:8189/object_info',timeout=60))
print([n for n in obj if 'JR' in n or 'Sigma' in n or 'Acceleration' in n])
"
```

`h3_runner.py` builds its graph in Python and knows nothing about these nodes, so
Phase 1 needs the graph extended before any of this can run. That work is not
done yet.

## One caveat about their numbers

Their Prompt Review node needs a live browser and cannot run unattended, which
they document. Our three ads yesterday were produced by a queue with nobody
watching. If we adopt anything from that suite, it has to be the parts that run
headless.
