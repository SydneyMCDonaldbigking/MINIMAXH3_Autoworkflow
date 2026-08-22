# H100 Batch: One Dish Rendered, Four Silently Didn't - 2026-08-21

A 5-dish chained batch on a rented H100 NVL reported `ALL DONE`, exit code 0.
One dish actually rendered. The other four failed before a single frame was
saved, and the failure was invisible until someone went and read the full log
instead of trusting the summary line.

## What actually happened, in order

| Dish | Result |
| --- | --- |
| `banana_milkshake` (separate earlier run) | 3/3 clips, gated, passed |
| `japanese_teriyaki_chicken_thigh` (1/5) | 3/3 clips, gated, passed |
| `freezer_shrimp_wonton_egg_drop_soup` (2/5) | clip-01 sampled ~4-6 min on the GPU, **never saved** |
| `rock_sugar_asian_pear_soup` (3/5) | failed before a job was ever queued |
| `garlic_chive_flower_pork_strips` (4/5) | failed before a job was ever queued |
| `yellow_chive_pork_strips` (5/5) | failed before a job was ever queued |

The batch was launched as one shell block with five `h3_sequence_runner.py run`
calls back to back, no `&&`, no exit-code check between them:

```bash
{
  echo "=== [1/5] ..."; python h3_sequence_runner.py run --sequence ...
  echo "=== [2/5] ..."; python h3_sequence_runner.py run --sequence ...
  ...
  echo "=== ALL DONE ==="
} 2>&1
```

A `{ }` group returns the exit status of its *last* command. The last command
is `echo`, which always succeeds. So the block reported success regardless of
what happened to dishes 2 through 5. The task-completion notification said
exactly that: `completed (exit code 0)`. It was not lying, it was answering a
question nobody should have been asking - "did the shell block finish" is not
"did the work happen."

## Layer 1: the local crash that ended dish 2 and pre-empted 3-5

`h3_sequence_runner.py`'s `run_streamed()` reads the child process's stdout
with `encoding="utf-8", errors="replace"`, then does this on every line:

```python
line = process.stdout.readline()
...
print(line, end="", flush=True)   # <- to the PARENT's own stdout
log.write(line)                   # <- to a UTF-8 log file, never reached this time
```

Somewhere in that stream a byte sequence arrived that was not valid UTF-8. The
decode step replaced it with U+FFFD, which is safe - that is what
`errors="replace"` is for. But this Windows session's console codepage is
**GBK** (`cp936`), and GBK cannot encode U+FFFD either. The `print()` call
raised, uncaught:

```
UnicodeEncodeError: 'gbk' codec can't encode character '�' in position 86: illegal multibyte sequence
```

That killed `h3_sequence_runner.py` for dish 2 outright - not after clip-01
finished, but *while streaming its output*, at the 376s mark of an ~800s job.
`log.write(line)` for that line never ran, so the actual offending bytes are
not recoverable from the log; the log simply stops at `376s`.

Dishes 3, 4 and 5 then failed *immediately*, all at nearly the same character
offset (86, 90, 90, 90 - not dish-specific content, the same fixed message each
time). That is the second-order effect covered next, not four independent
Unicode bugs.

**This class of bug is not specific to tonight's trigger.** Any non-UTF-8 byte
from any subprocess, on any GBK/cp936 Windows console, will always crash this
exact way. Whatever caused the bad byte tonight is almost incidental; the
missing try/except around a console `print()` is the real defect and it will
fire again on a different trigger.

## Layer 2: why dishes 3, 4, 5 never even queued a job

By the time dish 3 started, ComfyUI on the remote box was **dead** -
`curl http://127.0.0.1:8189/system_stats` returned connection refused, no
`main.py` process existed, `nvidia-smi` showed `0% util, 0 MiB`. Every
subsequent `h3_runner.py` invocation failed to connect immediately, which is
consistent with hitting the same doomed print path in a different place.

`/root/comfyui_h3.log` shows exactly where the server itself stopped: three
complete `Prompt executed in 00:13:2Xs` cycles (dish 1's three clips, matching
its successful local result), then a fourth `got prompt` that samples cleanly
through step 3 of 8 and **the log file simply ends there**. No traceback, no
error line, no OOM entry in `dmesg`, no `journalctl` entries (this is a
container - there is nothing to read). The server did not report why it died;
it just stopped writing.

### The leading suspect - UNVERIFIED, stated as such on purpose

While dish 1's clip-03 and dish 2's clip-01 were sampling, a SageAttention
2.x source build was deliberately started on the *same box*, concurrently, to
prep acceleration for the remaining dishes:

```bash
export CUDA_HOME=/usr/local/cuda-12.8 MAX_JOBS=32 EXT_PARALLEL=8 TORCH_CUDA_ARCH_LIST=9.0
python -m pip install --no-build-isolation -v .
```

32 parallel `nvcc` jobs plus an `apt-get install cuda-toolkit-12-8` full
meta-package install, sharing the same CPU/RAM/driver stack as a live paid
render. The timing lines up: the compile was mid-flight, dish 2's clip-01 died
mid-sampling. It also does not line up perfectly: `dish 1`'s clip-03 sampled
to completion *after* the `apt-get install` had already run, and the pip build
log showed `Successfully installed sageattention-2.2.0` before dish 2 even
started - so the heaviest part of the compile may have already finished by the
time the crash happened. No OOM-killer evidence exists either way.

**Follow the project's own rule here: this is not proven, so it is not stated
as fact.** What is fact is that running a 32-job source compile next to a live
render is an unforced risk that did not need to be taken mid-batch, and the
crash happened during the window it was live. Treat it as guilty until a
cleaner reproduction says otherwise.

## What was actually lost

- `japanese_teriyaki_chicken_thigh` and `banana_milkshake`: nothing lost, both
  complete and gated.
- `freezer_shrimp_wonton_egg_drop_soup` clip-01: roughly 4-6 minutes of paid
  H100 sampling, zero output - it never reached `VAEDecode`/save.
- `rock_sugar_asian_pear_soup`, `garlic_chive_flower_pork_strips`,
  `yellow_chive_pork_strips`: zero GPU cost (failed before queuing), but zero
  progress.
- An unknown span of fully idle GPU time between the server dying and someone
  noticing - `0% util, 0 MiB`, still billing, doing nothing. This is the most
  expensive line item and the easiest one to have caught immediately with a
  single `curl`.

## What to do differently

1. **Never run a source compile or a system package install on the same box
   as a live paid render.** If acceleration needs prepping mid-batch, do it on
   a second scratch instance, or actually stop the queue at a dish boundary
   first instead of assuming there will be time to catch the boundary later.
   The original plan here *was* to catch the boundary between dishes - it
   failed because the compile work absorbed attention right as dish 1 finished
   and dish 2's clip-01 had already been queued by the time anyone checked.
2. **A chained batch script must check exit status per command.** `cmd1 &&
   cmd2 && cmd3` or an explicit `if [ $? -ne 0 ]; then break; fi` between
   dishes - not a bare sequence where only the final `echo` decides the
   reported result.
3. **`ALL DONE` / `exit code 0` on an orchestration script is not evidence
   anything rendered.** This is the same law `check_clip_quality.py` already
   teaches at the picture level - a pass is necessary, not sufficient - now
   applied one layer up. Read the actual `[sequence] final video:` lines per
   dish before reporting a batch as done.
4. **`run_streamed()`'s passthrough `print()` needs to stop being able to kill
   the whole run.** Wrap it, or set `PYTHONIOENCODING=utf-8` (or route through
   a stream that can't raise on encode) so a stray non-UTF-8 byte from a
   subprocess degrades to a garbled character on screen instead of an
   uncaught exception that takes down orchestration for every dish behind it.
5. **After launching anything on a rented box, a `curl .../system_stats` and
   an `nvidia-smi` are cheap enough to run before ever trusting silence.** The
   dead server sat unnoticed until someone went looking for a completely
   different reason (gating a finished dish). It should have been the first
   thing checked when the batch's own log started showing crashes.
