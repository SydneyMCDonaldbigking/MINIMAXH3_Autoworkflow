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

Write each clip as one physical commercial beat:

1. Clip 01: product hook and first action.
2. Clip 02: cooking/texture/share transformation.
3. Clip 03: serving/family/product hero.

Each 5s prompt uses:

- `0-1.6s`: establish the action and spatial context.
- `1.6-3.3s`: close-up insert, heat/steam/texture, or object movement.
- `3.3-5.0s`: endpoint and transition handle.

Always name shot size, angle, lens/focus feel, start frame, camera move, end frame, physical hand/tool/food motion, and the handoff mechanism. Keep it silent, no subtitles, no generated overlays. People are allowed when they are fictional commercial characters and are supplied as character references; preserve them deliberately instead of cropping all faces by default.

For cooking videos, do not trust H3 to invent ingredient processing. If the story includes cutting, peeling, washing, marinating, soaking, blanching, or portioning, generate a dedicated prep-state reference first. The prep-state image should show the exact cut size, tool, hand position, cutting board, and already-processed ingredients. Then write clip 01 as `prep/cut -> gather -> pot/pan`, not as a vague "prepare ingredients" beat.

## Soup Reference Lesson

For cooked dishes like old duck soup, add four Seedream/Image2 reference images before H3 when time allows:

- ingredient prep/cut state with knife, cutting board, duck pieces, daikon chunks, ginger slices, scallion sections;
- opening/down-to-pot state;
- mid-cooking state with flame, pot, steam, ingredients;
- finished hero state with clear golden broth, cooked duck, translucent daikon, steam.

The finished reference matters. Without it, H3 may make the soup muddy or undercooked even at native resolution.
