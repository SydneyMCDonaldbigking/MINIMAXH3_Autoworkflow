# MiniMax H3 3x5s Native 1080 Workflow

Use this route when a 40GB A100 cannot hold one native vertical 15s MiniMax H3 job.

## Core Decision

- Do not generate one `15s` native vertical job on A100 40G; it OOMs at `1088x1920`.
- Generate three `5s` clips at `1088x1920`, 4-step Turbo, silent/no-audio.
- Extract each clip's last frame and prepend it as the next clip's first reference.
- Concatenate the three clips.
- Crop `1088x1920` to exact `1080x1920` with `crop=1080:1920:4:0`.

This is native-detail generation plus a tiny side crop. It is not an upscale.

MiniMax H3's 5s request becomes 124 frames, about 5.17s at 24 fps, so three clips land around 15.5s before editorial trimming.

## Expected Speed

On A100-PCIE-40GB, based on the successful 5s 1080-class R2V tests:

- One `1088x1920`, 5s, 4-step Turbo clip: about 8-9 minutes.
- Three sequential clips: about 25-30 minutes plus ffmpeg stitching.

If using multiple servers, run different ads on different machines. For one ad, keep its three clips on one machine unless you are deliberately accepting weaker continuity.

## Commands

Generate director reference assets first:

```powershell
.\generate_reference_assets.ps1
```

Print the planned Image2/Seedream commands without spending API credits:

```powershell
.\generate_reference_assets.ps1 -PrintOnly
```

Start ComfyUI on the server:

```bash
cd /root/ComfyUI
source /home/node/anaconda3/etc/profile.d/conda.sh
conda activate comfy_h3_torch29_cu126
python main.py --listen 127.0.0.1 --port 8189 --lowvram
```

Run duck soup:

```bash
python h3_sequence_runner.py run \
  --sequence sequences/duck_soup_3x5_1080.json \
  --server http://127.0.0.1:8189 \
  --output-root sequence_outputs
```

Run egg tart family afternoon tea:

```bash
python h3_sequence_runner.py run \
  --sequence sequences/egg_tart_family_3x5_1080.json \
  --server http://127.0.0.1:8189 \
  --output-root sequence_outputs
```

The final path is recorded in:

```text
sequence_outputs/<sequence_id>/<run_id>/sequence-manifest.json
```

## Config Rules

- `width`: `1088`
- `height`: `1920`
- `duration`: `5.0`
- `steps`: `4`
- `turbo`: `true`
- `turbo_low_vram`: `true`
- `no_audio`: `true`
- `use_previous_last_frame_as_ref`: `true` on clips 2 and 3
- final crop:

```json
{
  "crop": {
    "width": 1080,
    "height": 1920,
    "x": 4,
    "y": 0
  }
}
```

## Multi-Image Reference Stack

Do not run H3 from product/logo references alone. Each 3x5s ad uses a production reference stack:

- protagonist/person bible: stable fictional cook or family character reference for H3 character continuity;
- hands/action bible: close hand references are still useful for cutting, serving, pouring, and product interaction;
- scene bible: fixed kitchen/stove or family afternoon-tea table;
- ingredient prep/cut-state keyframe: chopped, sliced, peeled, marinated, soaked, or otherwise processed ingredients plus the tool that proves the action;
- opening/action keyframe: the composed starting state for the first clip;
- mid-state keyframe: cooking, steam, texture, or sharing state;
- final-state keyframe: finished soup or final egg-tart table hero;
- product reference: supplied product image;
- official brand reference: `company_logo/AGO.png`, clip 1 only unless naturally needed.

MiniMax H3 supports up to 9 image references. Use that capacity deliberately: character reference, scene reference, action state, product, finished state, and brand. The sequence JSONs are wired so missing protagonist/scene/state references block the run; generate those assets before spending A100 time.

Current required generated reference outputs:

```text
outputs/seedream_reference_assets/duck_soup_cook_character_scene/generated/duck_soup_cook_character_scene-1.png
outputs/seedream_reference_assets/duck_soup_actor_hands_scene/generated/duck_soup_actor_hands_scene-1.png
outputs/seedream_reference_assets/duck_soup_prep_cut_state/generated/duck_soup_prep_cut_state-1.png
outputs/seedream_reference_assets/duck_soup_kitchen_opening_clean/generated/duck_soup_kitchen_opening_clean-1.png
outputs/seedream_reference_assets/duck_soup_mid_cooking_state/generated/duck_soup_mid_cooking_state-1.png
outputs/seedream_reference_assets/duck_soup_finished_hero_state/generated/duck_soup_finished_hero_state-1.png
outputs/seedream_reference_assets/egg_tart_family_people_character_scene/generated/egg_tart_family_people_character_scene-1.png
outputs/seedream_reference_assets/egg_tart_family_protagonist_hands/generated/egg_tart_family_protagonist_hands-1.png
outputs/seedream_reference_assets/egg_tart_family_table_scene_clean/generated/egg_tart_family_table_scene_clean-1.png
outputs/seedream_reference_assets/egg_tart_family_afternoon_tea_hands_only/generated/egg_tart_family_afternoon_tea_hands_only-1.png
outputs/seedream_reference_assets/egg_tart_family_final_hero_state/generated/egg_tart_family_final_hero_state-1.png
outputs/seedream_reference_assets/egg_tart_family_people_final_hero/generated/egg_tart_family_people_final_hero-1.png
```

## Director Prompt Pattern

Clip prompts follow the official MiniMax H3 `Ref2VA` prompt format from
`MiniMax-AI/MiniMax-H3`, directory `skills/h3-prompt-writing`. Our production
route is `r2v`, which is Ref2VA, so every clip prompt is a full-reference prompt
and uses all six sections, in this exact order, as plain labeled sections. No
JSON, no XML wrapper:

```text
subject_definitions:
summary:
retention_analysis:
detailed_description:
overall_soundscape:
non_diegetic_music:
```

### Bind labels to our reference stack

`<Picture N>` must be declared in the same order the sequence JSON lists
`ref_images`. `h3_runner.py` maps that list positionally onto
`ref_images.ref_image_0..8`, so `<Picture 1>` is the first entry of
`ref_images`, `<Picture 2>` the second, and so on. Reorder the JSON without
reordering the prompt and every reference in the prompt silently re-binds to the
wrong image.

Clips with `use_previous_last_frame_as_ref` shift by one. `h3_sequence_runner.py`
*prepends* the carried-over last frame with `refs.insert(0, previous_last_frame)`,
so on clips 02 and 03 `<Picture 1>` is the last frame of the previous clip and
everything listed in that clip's `ref_images` moves down one slot:

```text
clip 01   <Picture 1> = ref_images[0]
clip 02   <Picture 1> = last frame of clip 01,  <Picture 2> = ref_images[0]
clip 03   <Picture 1> = last frame of clip 02,  <Picture 2> = ref_images[0]
```

Declare that carried frame explicitly, because it is the continuity anchor:

```text
<Picture 1> is the final frame of the previous clip, showing the red chili broth
at a full simmer with steam rising.
```

Declare each recurring person as `<Subject N>` and anchor them to the picture
they come from, then use that label everywhere instead of re-describing them:

```text
<Subject 1> is the professional chef in <Picture 1>, mid-thirties, black chef
coat, short dark hair.
<Picture 5> is the raw rolled beef product image on a dark wooden tray.
```

A label means the same thing in all six sections. Never introduce a label in
`detailed_description` that was not declared in `subject_definitions`.

### Section rules

- `summary`: open with the task type, then one paragraph on how the references
  relate to the target clip. For our ads the task type is `reference generation`.
- `retention_analysis`: one line per reference, stating how strongly it is
  carried into the video. Allowed markers for visible references are
  `fully_preserved`, `partially_preserved`, `attribute_transfer`, and
  `weak_reference`. Use `fully_preserved` for the protagonist and the product,
  `attribute_transfer` for scene and lighting bibles, `weak_reference` for the
  brand cue.
- `detailed_description`: the shot-by-shot body, 350-500 words for a generation
  task. Number shots `[Shot 1]`, `[Shot 2]`, `[Shot 3]`. The first shot carries
  no timestamp; every later shot opens with its cut time as
  `At MM:SS.mmm,`. Timings must add up to the requested duration.
- `overall_soundscape`: ambient and physical sound across the whole clip.
- `non_diegetic_music`: score the characters cannot hear.

Keep both audio sections even though production runs pass `--no-audio`. H3
samples video and audio in one joint latent, so the sound description still
shapes motion, pacing, and impact timing. `--no-audio` only skips the audio
decode when saving the file, it does not remove audio from sampling.

### Camera and dialogue

Write camera as a sentence combining motion type, amplitude, and speed, for
example `the camera pushes in with small amplitude at slow speed`. Do not stack
abbreviations or invent shorthand.

Our food ads are silent, so normally there is no dialogue. If a clip ever needs
a line, wrap it as `<d>[Language] line text</d>`, keep the original language and
punctuation verbatim inside the tag while all description around it stays
English, and give each speaker a stable ID `(S1)`, `(S2)` assigned in order of
first vocal appearance.

### Use 8 steps, not 4

Production runs at `steps: 8`. Four steps is not usable and the difference is not
subtle. Measured on 2026-08-10 on a verified-healthy A100, same seed, same
prompt, same references, step count the only variable:

| | 4 steps | 8 steps |
| --- | ---: | ---: |
| Camera flip rate, overall | 7.4% | **1.6%** |
| Camera flip rate, opening third | 17.5% | **2.5%** |
| Sampling time | 5:30 | 11:08 |
| Clip wall time | 7.4 min | 13 min |

The visible defect at 4 steps is worse than the numbers suggest. Whole objects
render semi-transparent and doubled: in the beef clip the cutting board, the
beef tray and the brand card were all ghosted at once, and you could see the
tray through the board. At 8 steps the same frame is solid.

`check_clip_quality.py` passed the 4-step clip. It gates on constant frames and
camera jitter and has no ghosting detector, so a PASS is necessary but not
sufficient - still look at frames.

Cost: a three-clip ad goes from about 22 to about 39 minutes, roughly $0.26 to
$0.46 of A100 time. That is the cheapest quality fix available here.

An earlier conclusion in this file was wrong and is retracted: the opening
camera shake was blamed on the model being unable to execute a smooth push, with
"lock the camera off" proposed as the fix. It executes the push fine at 8 steps.
The shake was undersampling.

### House rules the official skill does not cover

The official format governs structure. It says nothing about what survives a
4-step distilled Turbo LoRA at 1088x1920, which is a far thinner sampling budget
than the full-step inference it was written for. These rules come from measuring
our own output on 2026-08-10 with `check_clip_quality.py`.

**Every beat must be a directional action that completes inside its window.**
Never end a shot on a state to hold. The first Ref2VA beef clip closed on "the
camera tilts down, the broth bubbles and steam rises" - a state, not an action.
The hand stalled above the wok for the last 1.5 seconds and the model filled 40
frames of nothing with noise: 45% of frames in that third reversed direction.
The egg tart clip, which closes on a real move, fell to 7.5%.

**One action, one actor, per shot.** That same beat asked for two simultaneous
hand actions in 1.6 seconds, carrying cabbage and stirring with a ladle. The
model performed neither and hovered instead.

**Commit the camera or lock it off.** Write a definite move, or write that the
camera does not move and say it explicitly. Hedged instructions like "tilts down
with small amplitude at slow speed" invite micro-drift. Counter-intuitively the
most stable third we have measured is also the one with the *largest* camera
motion - ambiguity destabilises, movement does not.

**Do not ask for a tight close-up of a hand working a tool.** This is the
highest-value rule we have. In the first Ref2VA beef clip every object-level
defect landed in one shot, the 85mm close-up of a knife cutting cabbage:

- the vegetable changed species, a round green cabbage instead of the napa
  cabbage the reference clearly shows;
- the knife broke into two blade fragments with no plausible cut plane;
- the fingertips lay flat in the blade path instead of the knuckle guard the
  prompt asked for.

The wide establishing shot and the drop-into-the-wok shot in the same clip were
clean. At 4 steps the model handles wide framing and bulk material well, and
fails at close-range rigid tool geometry interacting with hands. Shoot prep at
medium distance with the forearms in frame, or skip the cutting action entirely
and show the already-cut result, letting the Seedream prep-state reference prove
that the processing happened. That reference exists precisely so H3 does not
have to perform the cut on camera.

**Name the distinguishing features of an ingredient in the shot text.** Marking
a reference `fully_preserved` in `retention_analysis` did not stop the cabbage
substitution. Where two ingredients could be confused, describe the one you want
inside `detailed_description` and rule out the other explicitly.

**Gate every clip before assembling a sequence:**

```bash
python check_clip_quality.py sequence_outputs/<id>/<run>/clip-01/*.mp4
```

It fails a clip on a constant frame (the NaN signature) or on camera jitter
above 20% overall / 25% in the last third. Do not gate on sharpness: the clip
judged bad measured *sharper* per frame than the clip judged good, so per-frame
sharpness does not separate the cases.

### Story shape

Write each clip as one physical commercial beat:

1. Clip 01: product hook and first action.
2. Clip 02: cooking/texture/share transformation.
3. Clip 03: serving/family/product hero.

Inside a 5s clip use three shots:

- `[Shot 1]` 0-1.6s: establish the action and spatial context.
- `[Shot 2]` from about 00:01.600: close-up insert, heat/steam/texture, or
  object movement.
- `[Shot 3]` from about 00:03.400: endpoint and transition handle into the next
  clip.

Always name shot size, angle, lens/focus feel, start state, camera move, end
state, physical hand/tool/food motion, and the handoff mechanism. Describe
composition, subjects, environment, actions, camera, and sound. Do not write
plot summary or motivation, and do not leave a reference unresolved.

No subtitles, no generated overlays, no floating logo. People are allowed when
they are fictional commercial characters supplied as character references;
preserve them deliberately instead of cropping all faces by default.

For cooking videos, do not trust H3 to invent ingredient processing. If the story includes cutting, peeling, washing, marinating, soaking, blanching, or portioning, generate a dedicated prep-state reference first. The prep-state image should show the exact cut size, tool, hand position, cutting board, and already-processed ingredients. Then write clip 01 as `prep/cut -> gather -> pot/pan`, not as a vague "prepare ingredients" beat.

Worked example in the new format:
`prompts/h3_3x5_1080/shuizhu_beef_roll_clip_01.md`.

## Soup Reference Lesson

For cooked dishes like old duck soup, add four Seedream/Image2 reference images before H3 when time allows:

- ingredient prep/cut state with knife, cutting board, duck pieces, daikon chunks, ginger slices, scallion sections;
- opening/down-to-pot state;
- mid-cooking state with flame, pot, steam, ingredients;
- finished hero state with clear golden broth, cooked duck, translucent daikon, steam.

The finished reference matters. Without it, H3 may make the soup muddy or undercooked even at native resolution.
