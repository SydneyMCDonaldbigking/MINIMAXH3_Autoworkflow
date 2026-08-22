# MiniMax H3 15s Storyboard Workflow

## A100 40G Native 1080 Update

A100 40G can run 15s at `768x1344`, but native vertical 1080-class `1088x1920` 15s R2V OOMs. For production on 40G, use `MINIMAX_H3_3X5_NATIVE1080_WORKFLOW.md`: three `5s` clips at `1088x1920`, then crop the stitched result to exact `1080x1920`. This is the current stable native-detail route.

Purpose: adapt the useful storyboard and first-frame method from
`viral-social-remix` to MiniMax H3. This workflow is intentionally simpler than
the Seedance three-clip route: write one strong 10s/15s storyboard, generate a
correct opening frame with Image2/OpenRouter, provide that opening frame plus
the source reference images to MiniMax H3, generate one video, save the finished
MP4 locally, and stop. The user reviews and does any second-pass editing.

## 1. Design Decision

Use `viral-social-remix` as the commercial director brain only:

- product hook and audience logic;
- timed storyboard structure;
- shot size, angle, lens, camera move, and endpoint language;
- action mechanics tied to hands, utensils, heat, product texture, packaging,
  logo prop, and scene continuity;
- negative constraints such as no face, no subtitles, no fake text, no extra
  logos, no product mutation.

Reuse the Image2 first-frame gate:

- generate the opening frame with OpenRouter Image API / `openai/gpt-image-2`;
- pass product, model/person, official logo/brand lockup, and scene images as
  actual image references;
- the opening frame must already have the correct product, logo/brand region,
  model/hands, scene, lighting, and first composition;
- if product identity, logo/sign, model, or scene is wrong, regenerate the
  opening frame before H3;
- do not fix a bad logo or product by local paste/composite/mask/overlay.

Do not copy the Seedance control flow:

- no three separate 6s clips by default;
- no clip-to-clip handoff review;
- no returned-last-frame transition-anchor loop;
- no ChatCut pass unless the user explicitly asks for it;
- no agent-owned final quality judgement. The user is the reviewer.

MiniMax H3 route:

```text
brief + reference images
-> 10s/15s commercial storyboard prompt
-> Image2/OpenRouter opening frame identity gate
-> MiniMax H3 R2V one-shot generation with opening frame + source references
-> download/save MP4 locally
-> stop for user review
```

## 2. Recommended H3 Mode

Use `r2v` for most commercial work because it accepts multiple reference
images.

Reference image set, up to 9 images:

1. Image2-generated opening frame;
2. model or hand/person reference, if used;
3. product image;
4. product plus company logo or brand lockup;
5. scene/kitchen/store/background reference;
6. optional cooked/served result reference;
7. optional packaging close-up;
8. optional style or lighting reference.

For simple prompt-only tests, use `t2v`. For one source photo that should become
the exact opening frame, use `i2v`. For brand/product commercials, prefer `r2v`
with the Image2 opening frame as reference image 1 plus the original source
references after it.

If a future H3 workflow supports both exact `first_frame` and multiple
references in one node, use the Image2 opening frame as the exact first frame
and still provide product/model/logo/scene as references. In the current runner,
the practical route is R2V with the opening frame as the strongest first
reference.

## 3. Duration and Resolution

`h3_runner.py --duration 10` becomes a MiniMax H3-compatible length of about
243 frames at 24fps, so the actual clip is about 10.13 seconds.

`h3_runner.py --duration 15` becomes about 362 frames at 24fps, so the actual
clip is about 15.08 seconds.

Recommended sizes:

- Fast batch: `1344x768`
- Native 1080-ish landscape: `1920x1088`
- Tested vertical social production: `768x1344`
- Native 1080-ish vertical: `1088x1920`, but A100 40G OOMed at sampler for
  15s R2V. Treat this as unsupported in the current env.

For the current A100 40G server, `768x1344` 15s vertical R2V is the practical
one-shot ad route, but it is not a native 1080p route. Upscaling/reframing a
stable `768x1344` output can create a `1080x1920` delivery file, but it is only
a proxy and may look softer than real 1080p generation. Native 1080p should be
retested only on a larger/faster setup such as 80G VRAM or a proven 5090-class
local workflow.

## 4. Image2 Opening Frame

Before generating video, create a single ad-ready opening frame. This is the
identity anchor for MiniMax H3.

The Image2 prompt should use the same commercial grammar as
`viral-social-remix`:

- exact product identity and package shape;
- official logo/brand region as a real object or prop, not a floating overlay;
- model/person/hands identity when supplied;
- scene/kitchen/store/background;
- shot size, angle, lens/focus, lighting, action start, and endpoint;
- negative constraints for wrong product, wrong logo, fake UI/text, face, hands,
  and watermark.

Opening-frame template:

```text
Create a 1080x1920 opening reference frame for a premium social commercial.

REFERENCE USE:
[Image 1] is the model/person/hands reference.
[Image 2] is the product/package reference.
[Image 3] is the official company logo or product+logo reference.
[Image 4] is the scene/kitchen/store/background reference.
Use these references as actual identity anchors. Preserve product family,
package shape, logo/brand region, model/hands style, scene, lighting, and color
grade.

FRAME:
[Medium close-up / wide / close-up] shot, [camera angle], [lens/focus feel].
Start composition: [where product, model/hands, logo prop, and scene sit in the
frame]. The opening moment begins with [specific action about to happen].
Lighting is [source, direction, softness, contrast, color grade].

BRAND:
If a brand/logo is required, render it as a real printed package, tabletop sign,
store sign, or product prop with correct perspective, lighting, shadow, and
occlusion. Do not make it a floating overlay or caption.

QUALITY:
Photorealistic premium grocery/product commercial, sharp product texture,
realistic hands/tools/props, coherent scene, ad-ready composition.

NEGATIVE:
wrong product, mutated package, misspelled logo, wrong brand region, fake UI,
fake prices, floating logo, captions, subtitles, title cards, watermark, face,
deformed hands, extra fingers, scene mismatch.
```

If the generated opening frame is wrong, regenerate it. Do not continue to H3
with a damaged identity anchor.

## 5. Storyboard Writing Rules

Write the storyboard as timed beats inside a single MiniMax prompt. The prompt
should be useful to a video model, not a vague ad concept. Reuse the
`viral-social-remix` prompt discipline, but collapse it into one 10s or 15s
video instead of three separate clips.

Each beat should include:

- time range;
- shot size and camera angle;
- lens/focus feel;
- starting composition;
- action mechanics;
- camera movement;
- ending composition;
- continuity object or transition logic.

For a 10s commercial, use five compact beats:

```text
0-2s: product/brand hook and scene setup
2-4s: first use or preparation action
4-6s: transformation, heat, pour, steam, texture, or product proof
6-8s: macro payoff or lifestyle serving beat
8-10s: final hero endpoint
```

For a 15s commercial, use five roomier beats:

```text
0-3s: product/brand hook and scene setup
3-6s: first use or preparation action
6-9s: transformation, heat, pour, steam, texture, or product proof
9-12s: macro payoff or lifestyle serving beat
12-15s: final hero endpoint
```

For cooking or food:

- show physical cause and effect;
- include hands, utensils, packaging, cookware, heat, steam, pour, sauce,
  plating, or texture;
- avoid keeping the entire video on one flat tabletop when cooking is implied;
- keep product family stable across the whole clip;
- use package/logo strongly at the opening, then let food/action carry the rest.

## 6. MiniMax Prompt Template

Use this as the internal storyboard template before submitting to MiniMax H3:

```text
Create one [10/15]-second photorealistic premium grocery commercial.

REFERENCE USE:
[Image 1] is the Image2-generated opening frame and strongest composition
anchor.
[Image 2] is the model/person/hands reference.
[Image 3] is the product and packaging reference.
[Image 4] is the product plus company logo or official brand lockup reference.
[Image 5] is the scene/kitchen/store/background reference.
Use the references to preserve product identity, package shape, brand region,
scene style, hand/clothing style, lighting, and color grade. Do not invent a
different product, package, brand, store, or kitchen.

VISUAL STYLE:
Photorealistic premium food/product commercial, natural believable motion,
sharp product texture, coherent warm commercial lighting, no face, no subtitles,
no title cards, no lower thirds, no watermarks, no extra logos.

STORYBOARD:
[Use either the 10s or 15s timed beat structure.]

CONTINUITY:
Begin from the visual logic of [Image 1]. Preserve the same product, package
shape, ingredient identity, model/hands, scene, cookware/table layout, lighting
direction, color grade, and brand region. The logo/package must be readable in
the opening shot when present, but do not force it into every later shot if the
action naturally moves away from it.

NEGATIVE:
No face, no deformed hands, no extra fingers, no product mutation, no invented
fake prices, no fake UI, no misspelled logo, no subtitles, no captions, no
floating logo overlays, no title cards, no watermark, no scene teleporting.
```

## 7. Baozi / Food Ad Example Prompt

This is a MiniMax-style one-shot 15s prompt, not a Seedance three-clip prompt:

```text
Create one 15-second photorealistic premium grocery food commercial.

REFERENCE USE:
[Image 1] is the Image2-generated opening frame and strongest composition
anchor.
[Image 2] is the chef hands / model reference.
[Image 3] is the steamed bun product and packaging reference.
[Image 4] is the product plus company logo / official brand lockup reference.
[Image 5] is the warm kitchen scene reference.
Use the references to preserve the steamed bun identity, soft white dough,
package/product shape, brand region, chef-hand style, kitchen lighting, and
premium grocery color grade.

VISUAL STYLE:
Photorealistic premium food commercial, warm restaurant-kitchen light, realistic
flour, dough, steam, cookware, and hand motion. No face, no subtitles, no title
cards, no watermarks, no extra logos.

STORYBOARD:
0-3s: Medium close-up hook shot on chef hands shaping soft white steamed bun
dough on a floured stainless counter, with the product/package and official
brand prop visible near the edge of the frame. Slow controlled dolly-in from a
natural 50mm product angle, ending on the bun shape and flour texture.
3-6s: Hands lift the finished bun and move it toward a real stovetop steamer.
Camera follows the bun gently from counter to steamer, preserving the same warm
kitchen background and chef sleeves. End as the bun lands inside the steamer.
6-9s: Close-up heat proof: the steamer lid lowers, condensation forms, then
steam curls around the lid edge. Camera pushes into the steam and rack-focuses
from lid condensation to the bun shape inside.
9-12s: The lid opens and steam reveals plump glossy buns. A hand lifts one bun
with tongs or fingers, showing soft surface texture and appetizing heat. End on
a clean close-up of the bun being placed onto a plate.
12-15s: Final hero on the same kitchen counter: plated steamed buns with soft
steam, warm highlights, and the product/package naturally returning in the
background if composition allows. Slow premium push-in, ending on an ad-ready
food hero frame.

CONTINUITY:
Keep the product as steamed buns across all shots; do not turn them into soup
dumplings, meat buns, tangyuan, or unrelated pastries. Preserve the same
kitchen, hands, white chef sleeves, warm lighting, table layout, and product
identity. The brand/package must read in the opening shot, but later stove and
steam shots may focus naturally on cooking and texture.

NEGATIVE:
No face, no deformed hands, no extra fingers, no fake prices, no fake app UI,
no misspelled logo, no floating logo overlay, no subtitles, no captions, no
title card, no watermark, no sudden new kitchen, no product mutation.
```

## 8. 10s Compact Prompt Structure

Use this when the user wants speed or a shorter ad:

```text
Create one 10-second photorealistic premium product commercial.

REFERENCE USE:
[Image 1] is the Image2-generated opening frame and strongest composition
anchor.
[Image 2] is the model/person/hands reference.
[Image 3] is the product and packaging reference.
[Image 4] is the product plus company logo or official brand lockup reference.
[Image 5] is the scene/kitchen/store/background reference.

STORYBOARD:
0-2s: Opening product/brand hook begins from the visual logic of [Image 1].
Camera [shot size, angle, lens, movement] and ends on [specific product/action
state].
2-4s: Hands/model/product action proves use or convenience. Specify which
object moves, speed, direction, and endpoint.
4-6s: Transformation/proof beat: steam, pour, texture, package opening, product
detail, or use result. Include a close-up or rack-focus insert.
6-8s: Lifestyle or serving payoff in the same scene, preserving product and
brand identity.
8-10s: Final hero frame with the product/result in a clean premium composition.

CONTINUITY:
Preserve the product, package, model/hands, scene, lighting, color grade, and
brand region. Opening logo/package readability matters; later shots should not
force logo continuity if the action naturally moves away.

NEGATIVE:
No face, no deformed hands, no extra fingers, no product mutation, no fake
prices, no fake UI, no misspelled logo, no subtitles, no captions, no floating
logo overlays, no title cards, no watermark, no scene teleporting.
```

## 9. Local Save Workflow

Best path: keep ComfyUI running on the server, open an SSH tunnel, then run the
local `h3_runner.py` from this PC. The finished MP4 downloads directly into the
local workspace.

Open tunnel from Windows:

```powershell
ssh -N -L 8189:127.0.0.1:8189 -p <ssh_port> root@<server_ip>
```

Run a 15s R2V job locally:

```powershell
python h3_runner.py r2v `
  --server http://127.0.0.1:8189 `
  --prompt "<paste the 15s storyboard prompt>" `
  --ref-image C:\path\image2-opening-frame.png `
  --ref-image C:\path\model-or-hands.png `
  --ref-image C:\path\product.png `
  --ref-image C:\path\product-logo.png `
  --ref-image C:\path\scene.png `
  --width 768 --height 1344 `
  --duration 15 `
  --steps 4 `
  --seed 2026080901 `
  --prefix minimax15/baozi_15s_r2v `
  --output-dir server_outputs\minimax15 `
  --overwrite-upload `
  --turbo `
  --poll 10 `
  --timeout 21600
```

For 1080-ish landscape:

```powershell
python h3_runner.py r2v `
  --server http://127.0.0.1:8189 `
  --prompt "<paste the 15s storyboard prompt>" `
  --ref-image C:\path\image2-opening-frame.png `
  --ref-image C:\path\model-or-hands.png `
  --ref-image C:\path\product.png `
  --ref-image C:\path\product-logo.png `
  --ref-image C:\path\scene.png `
  --width 1920 --height 1088 `
  --duration 15 `
  --steps 4 `
  --seed 2026080902 `
  --prefix minimax15/baozi_15s_r2v_1080 `
  --output-dir server_outputs\minimax15 `
  --overwrite-upload `
  --turbo `
  --turbo-low-vram `
  --poll 10 `
  --timeout 21600
```

Fallback path: run `h3_runner.py` on the server and then `scp` the MP4 back:

```powershell
scp -P <ssh_port> root@<server_ip>:/root/ComfyUI/test_outputs/<file>.mp4 server_outputs\minimax15\
```

## 10. Agent Stop Rule

After the MP4 exists locally, stop and report the path. Do not judge the shot,
do not extract proof frames, do not enter ChatCut, and do not do second-pass
editing unless the user explicitly asks.

The handoff format should be short:

```text
Generated and saved locally:
C:\Users\uryuu\Desktop\comfyui_workflow\server_outputs\minimax15\<file>.mp4

Prompt/storyboard used:
<brief summary or linked .txt/.md file>
```

The user reviews the output and decides whether to reroll or edit.
