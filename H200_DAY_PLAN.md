# H200 day plan

One page, in order. Everything before "Produce" is cheap; do not skip the first
step to save a minute, because skipping it once cost two days.

## 0. Accept the card, before installing anything

```bash
bash server_scripts/check_bf16_mma.sh
```

The script reads `compute_cap` and builds for the right architecture, so it
handles H200 (sm_90) on its own. **The prebuilt `tools/bf16_check_sm80` binary
will not run there** - it is compiled for A100. Let the script build.

`bf16` must say PASS. Any failure means reject the machine and take another; do
not start debugging prompts or models. Record the UUID and serial it prints.

If the image has no `nvcc`, the script falls back to a PyTorch-level check. That
is weaker evidence but still enough to reject a machine.

## 1. Environment

```bash
cd /root/ComfyUI/custom_nodes
git clone --depth 1 https://github.com/comfyanonymous/ComfyUI.git /root/ComfyUI_src   # if the image has no ComfyUI
git clone --depth 1 https://github.com/Larryvrh/ComfyUI-MiniMax-H3-Turbo.git
git clone --depth 1 https://github.com/Goldlionren/ComfyUI_JR_MiniMaxH3Node.git
git clone --depth 1 https://github.com/kijai/ComfyUI-KJNodes.git
pip install -r ComfyUI_JR_MiniMaxH3Node/requirements.txt
pip install -r ComfyUI-KJNodes/requirements.txt
```

**KJNodes is not optional.** `JR_H3_UnifiedAcceleration` does not implement Sage
attention itself; it delegates to `PathchSageAttentionKJ` from KJNodes and raises
`H3AccelerationCompatibilityError` at execution time if that node is not
registered. Found 2026-08-11 by losing three queued runs to it, five seconds each.

Sage attention also needs kernels, and **the PyPI package is not the one the node
wants**. `pip install sageattention` gives 1.x, which exports only `sageattn` and
`sageattn_varlen`; the node asks for `sageattn_qk_int8_pv_fp8_cuda`, a
SageAttention 2.x symbol that has to be built from source. Before spending time on
that build, check the architecture: **the fp8 modes need sm_89 or newer**, so on
an A100 (sm_80) they cannot run at all and the fp16 modes are the only candidates.
On Hopper the fp8 path is native, which is the case worth testing.

Models, about 60 GB, roughly ten minutes on a fast link:

```bash
hf download Comfy-Org/MiniMax-H3 \
  diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors \
  diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors \
  text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors \
  vae/minimax_h3_video_vae_fp16.safetensors \
  vae/minimax_h3_audio_vae_fp32.safetensors \
  --local-dir /root/ComfyUI/models
hf download larryvrh/MiniMax-H3-Turbo-Lora \
  minimax_h3_turbo_v4_step600_ema.safetensors --local-dir /root/ComfyUI/models/loras
```

Payload from this machine, instead of hand-copying files:

```bash
python make_payload.py --all
scp -P PORT payload_*.tar.gz root@HOST:/root/
ssh -p PORT root@HOST 'tar xzf /root/payload_*.tar.gz -C /root/ComfyUI'
```

Start ComfyUI and tunnel in:

```bash
ssh -p PORT root@HOST 'cd /root/ComfyUI && setsid nohup python main.py --listen 127.0.0.1 --port 8189 --lowvram > /root/comfyui.log 2>&1 < /dev/null &'
ssh -N -L 8189:127.0.0.1:8189 -p PORT root@HOST
```

## 2. Confirm the nodes registered

```bash
python h3_accel_runner.py --probe
```

Three things to read off it: the Turbo nodes are present, a sigma-shift node
exists and under what name, and `JR_H3_UnifiedAcceleration` is there. It also
prints each node's real input names. **The sigma-shift parameter is assumed to
be called `shift` and that is a guess**; if the probe shows another name, fix
the one line in `h3_accel_runner.py`.

Also worth checking now, for the BGM plan below:

```bash
python -c "
import json,urllib.request
obj=json.load(urllib.request.urlopen('http://127.0.0.1:8189/object_info',timeout=60))
print([n for n in obj if 'Audio' in n])
"
```

## 3. Re-baseline, 13 minutes

Timings from the A100 do not transfer; quality numbers do.

```bash
python h3_runner.py r2v \
  --prompt-file prompts/h3_3x5_1080/shuizhu_beef_roll_clip_01.md \
  --ref-image <the six beef refs, in sequence order> \
  --width 1088 --height 1920 --duration 5 --steps 8 --seed 202608090301 \
  --turbo --turbo-low-vram --no-audio --ref-image-size match --overwrite-upload \
  --prefix h200/baseline --output-dir outputs/h200_baseline
python check_clip_quality.py outputs/h200_baseline/*.mp4
```

A100 reference for the same clip: 83 s/step, 13 min, flip rate 2.5% overall and
5.0% in the opening third, no ghosting.

## 4. Listen to the audio, 13 minutes

Same clip, one variable: drop `--no-audio`. H3 has been sampling audio all along
and we have been discarding it, so this costs nothing extra and answers three
questions at once - room tone and foley, whether the `non_diegetic_music` section
produces usable score, and how they sit together.

**Do not add dialogue in this run.** The `<d>[Language] ...</d>` tag is untested
and mixing it in would make a bad result impossible to attribute. Dialogue gets
its own clip if the first one sounds promising.

Then decide the BGM route:

- **usable** - build the cheap BGM line: one 512x512, 15-second, 8-step pass per
  ad, harvested for its continuous score, laid under the three high-res clips.
  Steps cannot be reduced for this; undersampling damages audio the same way it
  ghosted video. Roughly 4 minutes and about $0.06 per ad on A100 pricing.
- **not usable** - keep H3's foley, take BGM from a library. Direction and BPM
  per dish are in this file's last section.

To keep audio through stitching, a sequence needs both:

```json
"defaults": { "no_audio": false },
"final":    { "keep_audio": true }
```

## 5. Acceleration experiments

Full design in `EXPERIMENT_PLAN_ACCELERATION.md`. One factor at a time, same
seed, same prompt, same references, one run at a time.

| # | Change | Question |
| --- | --- | --- |
| 1 | Sigma Shift only, 8 steps | does quality improve at fixed cost |
| 2 | Sage attention only | does s/it drop, does quality hold |
| 3 | full Unified chain | does the rest beat Sage alone |
| 4 | Sigma Shift + 6 steps | does it match the 8-step baseline |

Step 4 is the one worth money. We currently buy our way out of ghosting by
doubling steps; a schedule change that reaches 8-step quality at 6 saves a
quarter of every clip forever.

Judge each on s/it, `check_clip_quality.py`, and ghosting **by eye** on frames
40, 60, 75, 100. The gate cannot see ghosting; it passed a 4-step clip whose
cutting board was transparent.

## 6. Produce

Six dishes are configured and their reference bibles generated:

```
aoerliang_chicken_wings    thai_volcano_ribs      pepper_salt_prawns
japanese_pan_seared_steak  kungpao_chicken        minced_pork_eggplant
```

Per ad: three clips at whatever the experiments settle on, gate every clip,
look at frames for ghosting, then stitch. On A100 that was 39 minutes and $0.46;
H200 should be faster but nothing is measured yet.

## BGM direction, if the library route wins

Fifteen-second ads want a lift around the ten-second mark, landing on the hero
frame. The kelp soup ad already has that shape in picture.

| Dish | Feel | BPM | Instrumentation |
| --- | --- | ---: | --- |
| Thai volcano ribs | tropical, hot, punchy | 100-110 | hand drums, bamboo percussion, syncopated bass |
| Salt and pepper prawns | wok energy, sharp, professional | 110-120 | fast percussion, short string stabs on the sear |
| Chicken wings | young, easy, shared | 95-105 | lo-fi drums, electric piano, soft bass |
| Kung Pao chicken | homely, bright, Chinese | 85-95 | plucked strings, light percussion, pentatonic |
| Minced pork eggplant | warm, everyday, maternal | 70-80 | piano and low strings, slow, unhurried |
| Japanese steak | restrained, precise, solitary | 60-70 | solo piano or cello, lots of space, almost no drums |
