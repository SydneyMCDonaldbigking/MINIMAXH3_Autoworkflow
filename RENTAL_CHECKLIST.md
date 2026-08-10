# Renting a GPU and Setting It Up

Written 2026-08-10 after losing roughly two days and several rentals to a single
faulty GPU that every ordinary check called healthy. This is the procedure that
would have caught it in the first minute, plus the traps found along the way.

## The one rule

**Test bf16 tensor-core math before you install anything, every time, on every
machine.** It costs about a minute. Not testing it cost two days.

```bash
scp -P PORT tools/bf16_check_sm80 root@HOST:/tmp/
ssh -p PORT root@HOST 'chmod +x /tmp/bf16_check_sm80 && nvidia-smi --query-gpu=uuid,serial,driver_version --format=csv,noheader && REPS=3 /tmp/bf16_check_sm80'
```

Healthy looks like this:

```text
bf16   MACs=1.258e+11  bad=0  inf=0  rate/MAC=0  PASS
fp16   MACs=1.258e+11  bad=0  inf=0  rate/MAC=0  PASS
```

The machine we wasted two days on printed `bad=40 rate/MAC=1.91e-10 FAIL` on the
bf16 line while fp16 stayed perfect. Reject on any bf16 failure. Do not start
debugging prompts, models or PyTorch.

The binary is prebuilt and self-contained; it needs only a driver, no CUDA
toolkit and no Python. Rebuild it for other architectures with
`server_scripts/check_bf16_mma.sh`, which auto-detects compute capability and
falls back to a PyTorch-level check when `nvcc` is missing.

**Record the UUID and serial the script prints.** We compared two machines
without them and could not tell whether the second was even a different card.

## Why the ordinary checks all passed

Every one of these said the GPU was fine while it was silently corrupting one in
five billion multiply-accumulates:

| Check | What it said |
| --- | --- |
| `nvidia-smi` | Normal. No errors |
| ECC uncorrected, aggregate | `0`. ECC covers memory, **not the tensor-core datapath** |
| Xid in `dmesg` | None |
| Remapped rows | `0 / 0`, pending No |
| fp32 and fp16 matmul | Correct to the digit |
| bf16 **elementwise** | Correct |
| Driver install integrity | Kernel module, NVML and libcuda all matching versions |
| A full VRAM write/read sweep | Zero mismatches |

Only bf16 through the tensor cores was wrong, and only about 1 in 5e9 operations.
MiniMax H3's Turbo LoRA runs entirely in bfloat16, so a five-second clip does
enough multiply-accumulates to hit it many times. One bad value becomes `inf`,
`inf` propagates through the sampler, and the clip decodes to a uniform black
frame.

It is **intermittent**. One clip rendered perfectly at 19:45 and three in a row
came out black at 22:37 with no configuration change between them. That
intermittency is what made it look like a software problem for two days.

## Traps in the environment

**Never install a CUDA version your driver does not report.** Trying PyTorch
cu130 on a driver reporting CUDA 12.4 pulls the entire CUDA 13 NVIDIA runtime.

**pip downgrades do not remove what they pulled in.** Rolling PyTorch back to
cu126 left every CUDA 13 wheel installed. Because both variants install into the
same `site-packages/nvidia/<lib>/lib/` directory, `nvidia-cudnn-cu13` had
overwritten `nvidia-cudnn-cu12`, leaving one `libcudnn.so.9` built for CUDA 13.
Every convolution then failed with `CUDNN_STATUS_NOT_INITIALIZED`: sampling ran
because it is matmul and attention, and `VAEDecode` died on its first conv.

Detect and repair:

```bash
python -c "import torch;print(torch.backends.cudnn.version())"
pip list | grep -iE "nvidia-(cudnn|cublas|nccl)"
pip uninstall -y nvidia-cudnn-cu13
pip install --force-reinstall --no-deps nvidia-cudnn-cu12==9.10.2.21
```

**A disk-image copy carries the fault as faithfully as the fix.** Migrating to a
new instance by full-disk copy brought along the repaired cuDNN, which was good,
and reproduced the bf16 fault exactly, which was confusing until we realised the
driver came with the image too.

**"It worked before" is not evidence about your specific operation.** The old
`comfy_h3` env with torch 2.6.0+cu124 was treated as a known-good baseline
because it had rendered 720p successfully. Tested directly on the failing GEMM
shape, 2.6.0+cu124 failed identically to 2.9.1+cu126. A successful render does
not prove a particular kernel path was ever exercised.

## Choosing a machine

- **40 GB is enough.** Native `1088x1920` peaks around 30 GB. Paying for 80 GB
  buys nothing here.
- **Check available disk, not just the price.** The cheapest A100 we found had
  46 GB free; the models alone are 60 GB.
- **Check disk bandwidth and download speed.** They decide setup time, not
  render time. 60 GB at 800 Mbps is ten minutes; at 5800 Mbps it is ninety
  seconds.
- **Prefer an image that already ships PyTorch and CUDA.** On Vast the
  `PyTorch (Vast)` template saved a multi-gigabyte download and includes `nvcc`
  and SSH.
- Newer driver is fine and preferable. A driver reporting CUDA 12.9 or 13.x
  removes the minor-version-compatibility question entirely.

## Costs and timings on a healthy A100 40 GB

Measured 2026-08-10 at `$0.713/hr`:

| Item | Time | Cost |
| --- | ---: | ---: |
| Download 60 GB of models | ~10 min | $0.12 |
| Install ComfyUI and the H3 node | ~3 min | $0.04 |
| One clip, 8 steps, `1088x1920` | 13 min | $0.15 |
| One three-clip 15s ad | 39 min | $0.46 |

Sampling costs about 83 seconds per step **with no attention acceleration in the
graph**. `--lowvram` and `NORMAL_VRAM` measured 83.7 and 86.0 s/it respectively,
so keeping weights resident buys nothing: the cost is not weight streaming. Keep
`--lowvram` for the headroom.

This was first written as "that is the floor", which overstated what had been
measured. Two vram modes only rule out weight movement; they say nothing about
the attention path, which is where a `1088x1920` by 124-frame sequence actually
spends its time. Sage attention, chunked feed-forward and sigma shift are all
untested here. See `EXPERIMENT_PLAN_ACCELERATION.md`.

## Process lessons, mostly mine

- **Non-determinism alone does not prove hardware.** JIT-compiled kernels and
  race conditions produce it too. This reasoning caused a wrong "replace the
  card" call that cost a full disk migration.
- **Change one variable at a time.** Swapping the card and keeping the driver
  proved less than it appeared to, because both travelled together.
- **Go below the libraries when the libraries disagree.** Calling the Ampere
  `mma.sync` instruction directly from a native `sm_80` cubin settled in one
  test what a dozen library-level experiments could not.
- **Check the bit patterns.** The corrupt values were exactly `0x7f80` and
  `0xff80`, bf16 `+Inf` and `-Inf`, which killed the uninitialized-memory theory
  immediately. Uninitialized memory is not two distinct values.
- **A passing QC gate is necessary, not sufficient.** `check_clip_quality.py`
  passed a clip whose cutting board was transparent. It gates constant frames
  and camera jitter and has no ghosting detector. Look at frames.
- **Windows-to-Linux shell differences bit three times in one day:** CRLF in a
  script piped to remote `bash`, `pkill -f` matching its own command line, and
  `pgrep` not existing in Git Bash so a wait loop never waited. Prefer polling an
  HTTP endpoint over process-name matching, and send remote scripts as bytes with
  explicit LF.
