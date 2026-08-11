# Which card, what it costs, what to set

Everything here was measured by us on the same clip: `shuizhu_beef_roll_clip_01`,
seed `202608090301`, six references in sequence order, `1088x1920`, 5.0s, 8 steps,
turbo. Nothing is taken from a spec sheet or a vendor claim.

## The table to read before renting

| | A100 SXM4 40GB | A100 PCIE 40GB | H100 SXM 80GB |
| --- | --- | --- | --- |
| Measured | 2026-08-10 | 2026-08-11 | 2026-08-11 |
| Rented at | $0.713/hr | $0.836/hr | $2.311/hr |
| One 5s clip, 8 steps | 780 s | 907 s | **471 s** |
| **$ per clip** | **$0.154** | $0.210 | $0.302 |
| One 15s ad, 3 clips + stitch | ~39 min | ~24 min* | **~24 min** |
| Power limit | 400 W | 250 W | 700 W |
| Observed draw | - | 247 W, capped | 333 W idle-ish, 606-700 W under Sage |
| VRAM peak at 1088x1920 | ~30 GB | 33.1 GB | 33.1 GB |
| Sage attention fp8 | **impossible**, sm_80 | **impossible**, sm_80 | **yes**, 401 s (-15%) |

\* the A100 PCIE figure is for the whole ad including model load and stitching,
which is why it is not simply three times the clip time.

## How to choose

- **Cheapest per clip is the A100 SXM4.** If you are not in a hurry, this is the
  right card. The H100 buys wall-clock time, not money: it is 1.93x faster and
  43% more expensive per clip.
- **40 GB is enough.** Native `1088x1920` peaks at 33.1 GB, measured twice.
  Paying for 80 GB buys nothing on its own.
- **Read the power limit, not the TFLOPS number.** An A100 SXM4 and an A100 PCIE
  are the same silicon at the same memory bandwidth (1314.9 vs 1312.4 GB/s, 0.2%
  apart) and both advertise 15.6 TFLOPS. SXM4 is a 400 W part, PCIE is 250 W. The
  PCIE card sat at 247 W of its 250 W cap for an entire clip, clocking 1080 MHz
  against a 1410 MHz maximum, and took 16% longer. Renting it was a mistake made
  by comparing $/hr instead of $/clip.
- **Only Hopper can run the acceleration.** The fp8 Sage attention path needs
  sm_89 or newer. On any A100 it cannot run at all, so the only reason to pay
  H100 rates is speed plus that 15%.

## Settings, identical on every card

These are not card-dependent. They are the production settings and they are
measured, not preferred - see `h3-render-settings-are-measured`.

```
mode            r2v
size            1088x1920, cropped to 1080x1920 at the final encode
duration        5.0 s per clip, three clips per ad
steps           8
turbo           on, with turbo_low_vram
ref_image_size  match
audio           on: defaults.no_audio=false, final.keep_audio=true
```

**Do not drop to 6 steps to save time.** It is 33% faster, it passes
`check_clip_quality.py` with a *better* flip rate than the 8-step control, and it
rendered a napa cabbage whole and uncut. The gate cannot read the picture.

## Environment, same on every card

Driver 595.71.05 and the vast.ai PyTorch image gave torch 2.12.0+cu130 with the
venv at `/venv/main`, on both the A100 PCIE and the H100. Full install steps are
in `H200_DAY_PLAN.md`; the parts people miss:

- **KJNodes is not optional** if you want acceleration. `JR_H3_UnifiedAcceleration`
  delegates to `PathchSageAttentionKJ` and raises at execution time without it.
- **PyPI's `sageattention` is 1.x** and lacks the `sageattn_qk_int8_pv_*` entry
  points the node names. 2.x has to be built from source, and only on sm_89+.
- Models are about 60 GB. Download time is set by the host's link, not the card:
  13 minutes at 620 Mbps, under a minute at 15 Gbps.

## Before anything else

`bash server_scripts/check_bf16_mma.sh` must print `bf16 ... PASS`. It builds for
the card's own compute capability, so it handles sm_90 by itself; the prebuilt
`tools/bf16_check_sm80` binary is A100-only. Run it on every machine, every time,
including after a stop/start of the same instance - the fault that cost two days
was intermittent. See `RENTAL_CHECKLIST.md`.
