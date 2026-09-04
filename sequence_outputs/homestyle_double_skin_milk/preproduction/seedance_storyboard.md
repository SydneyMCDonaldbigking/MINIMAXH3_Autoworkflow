# Homestyle Double Skin Milk — Seedance 4×5s storyboard (2026-09-03 revision)

**Revision 2026-09-03 (v4): segment 2 split into 2a + 2b, and reference images
are now used sparingly.** The single 5s segment 2 tried to carry the egg
separation AND the mixing AND the wrapping AND the pot, and the real render
skipped the separation entirely - it poured whole yolks into the milk (visible
at ~1.5s of `seedance_test_milk_seg2.mp4`). Passing extra `input_references`
(`cracked_egg_state`, `egg_white_mix_state`) did not prevent it. User's rule
for Seedance: **少量参考图,多写 prompt** - keep only the first/last frame
anchors and put the detail in prose instead. So:

- Two new reference images were generated to anchor the two states no image
  had ever proven: `egg_separated_state` (glass bowl with egg white only,
  white bowl with both whole yolks) and `lid_off_film_on_state` (lid already
  off and set down, film still fully sealed).
- Segment 2a = the separation alone, ending on `egg_separated_state`.
- Segment 2b = pour white, sugar, whisk, sieve, wrap, into the lit pot,
  ending on `cook_state`.
- Segment 3 = lid off, then film off as a separate motion, cool, jam, hero.

# (superseded) Seedance 3×5s storyboard (2026-08-31 redo)

Replaces the MiniMax H3 3×5s chained-clip route for this dish, on Seedance
instead of H3, **keeping the 3-independent-segment structure** (user's call:
easier to control, redo one segment cheaply on a bad roll instead of the
whole 15s).

Applies tonight's clip-boundary lesson (`CURRENT_WORKFLOW.md` section 4c,
memory `clip1-inherits-finished-dish-reference`) directly to the Seedance
schema: **`hero_state` (the finished dish) is only ever a reference for
segment 3.** Segment 1 and segment 2 each end on their own real intermediate
state, never on a preview of the finished custard.

**Revision 2026-08-31 (v3): hands are now allowed.** Segment 1's first real
render described the milk pour with no actor ("the milk pours slowly from
one side of the bowl") and Seedance rendered the celadon bowl itself tilted
and hovering in mid-air with nothing holding it, for the last ~1.5s of a real
$1.87 clip - the same law as `no-person-unseen-actor-anti-pattern`, now
confirmed in an actual Seedance render, not just H3 or a static image. User's
call: stop avoiding hands for actions that need one. A hand and forearm may
now perform any hand-typical action (pouring, tipping, dabbing, lifting);
face, body, and any human reflection or shadow are still out of frame.

Chaining between segments works the same way `h3_sequence_runner.py` already
does it for H3: generate a segment, download it, `ffmpeg`-extract its actual
last frame, and hand that frame to the next segment as its `first_frame`.
Seedance-2.0 does not expose a `return_last_frame` passthrough (only
seedance-2.0-mini does), so this extraction step is required, not optional.

## Segment 1 — milk skin and drain (~5s)

```json
{
  "model": "bytedance/seedance-2.0",
  "prompt": "<SEG1 PROMPT>",
  "duration": 5,
  "resolution": "1080p",
  "aspect_ratio": "9:16",
  "generate_audio": false,
  "frame_images": [
    { "type": "image_url", "image_url": { "url": "outputs/reference_assets/53_homestyle_double_skin_milk/generated/homestyle_double_skin_milk_scene_anchor-1.png" }, "frame_type": "first_frame" }
  ]
}
```

No `last_frame` set here on purpose - there is no existing reference image of
"milk already drained, skin floating, nothing else changed," and reusing any
more-advanced asset (egg, wrap, hero) as a fake stand-in would reintroduce
tonight's exact bug. Let the prompt's own ending description drive it instead.

```text
A quiet Shunde home dessert kitchen, honey-oak counter, pale celadon
porcelain bowls, brushed brass shelf rail, a small stainless steaming pot,
soft rain-lit afternoon light. A home cook's hand and forearm may enter
frame to perform kitchen actions naturally; the cook's face, body, and any
human reflection or shadow stay out of frame throughout.

Locked wide shot on the opening layout: one small stainless saucepan of
steaming full-fat milk, two matching pale celadon bowls, a glass bowl of
separated clear egg white only, white sugar, a fine sieve, a small wire
whisk, clear cling film and the steaming pot. No whole egg or yolk exists
anywhere in this segment.

Cut to a bowl-height insert: warm milk rests in one celadon bowl and cools
until a delicate translucent first skin forms across its surface.

Cut to a side close shot: one hand tilts the celadon bowl gently and steadily
from one side, pouring the milk out slowly from beneath the intact skin into
a clear glass mixing bowl held or resting just below; the skin stays behind,
floating undisturbed in the celadon bowl. The hand's grip and the bowl's tilt
are natural and physically grounded throughout - the bowl is never
unsupported or airborne. End held on this exact state - drained milk in the
clear bowl, skin intact and floating in the celadon bowl. Do not let the
custard appear set or finished anywhere in this segment.
```

## Segment 2 — egg white, strain, wrap and steam (~5s)

```json
{
  "frame_images": [
    { "type": "image_url", "image_url": { "url": "<last frame extracted from segment 1>" }, "frame_type": "first_frame" },
    { "type": "image_url", "image_url": { "url": "outputs/reference_assets/53_homestyle_double_skin_milk/generated/homestyle_double_skin_milk_cook_state-1.png" }, "frame_type": "last_frame" }
  ],
  "input_references": [
    { "type": "image_url", "image_url": { "url": "outputs/reference_assets/53_homestyle_double_skin_milk/generated/homestyle_double_skin_milk_cracked_egg_state-1.png" } },
    { "type": "image_url", "image_url": { "url": "outputs/reference_assets/53_homestyle_double_skin_milk/generated/homestyle_double_skin_milk_egg_white_mix_state-1.png" } }
  ]
}
```

```text
Same kitchen, same bowl, same pot, continuing exactly from the first frame:
drained milk with its skin floating in the celadon bowl. A home cook's hand
and forearm may enter frame to perform kitchen actions naturally; face,
body, and any human reflection or shadow stay out of frame throughout.

Cut to a countertop close shot: two eggs already cracked into a glass bowl,
intact yolks in translucent pale-yellow white, an empty clean white bowl
waiting beside it - a settled state.

Hard cut to the already-separated state: pale-yellow egg white alone in one
glass bowl, the two intact yolks in the separate white bowl. One hand lifts
the egg-white bowl and tips it steadily, pouring the egg white cleanly into
the drained milk; the yolks stay untouched in their own bowl and are not
seen again. The hand's grip is natural and grounded - the bowl is never
unsupported or airborne.

A small wire whisk makes two slow circles in the milk-and-egg-white mixture
with sugar; it turns evenly ivory and silky, no foam or bubbles. The mixture
passes through a fine sieve and returns along the inner wall of the original
bowl, beneath the first skin, which rises back to the surface intact.

One hand stretches a clear sheet of cling film tightly over the bowl rim and
presses it flat, then pricks two or three tiny pinholes with a toothpick;
the wrapped bowl settles into the same stainless pot with visible steam. End
held on this exact state - wrapped, steaming, not yet set, not yet unwrapped.
Do not show the finished custard or remove the film in this segment.
```

## Segment 3 — steam reveal, cool and jam finish (~5s)

```json
{
  "frame_images": [
    { "type": "image_url", "image_url": { "url": "<last frame extracted from segment 2>" }, "frame_type": "first_frame" },
    { "type": "image_url", "image_url": { "url": "outputs/reference_assets/53_homestyle_double_skin_milk/generated/homestyle_double_skin_milk_hero_state-1.png" }, "frame_type": "last_frame" }
  ]
}
```

```text
Same kitchen and pot, continuing exactly from the first frame: the wrapped
bowl steaming inside the pot. A home cook's hand and forearm may enter frame
to perform kitchen actions naturally; face, body, and any human reflection
or shadow stay out of frame throughout.

Cut to a macro insert on the pot: gentle steam rises, then one hand lifts
the lid away and peels back the cling film in one steady motion, revealing
an ivory custard with an unbroken second skin - no bubbles, cracks or water
droplets. The bowl rests untouched and visibly cools; the steam thins and
stops.

Cut to a bowl-height close shot: one hand holds a small spoon and dabs one
small spoonful of jam onto the centre of the cooled skin, spreading it into
a thin neat dab, then withdraws. The jam stays a restrained single accent -
it does not cover the skin, pool at the rim or run down the side.

Calm final hero: the bowl of double-skin milk sits on the honey-oak counter
with its jam dab visible at centre and a small white porcelain spoon beside
it, matching the last frame. One jam accent only - no red bean, boba or
cream.
```

Recipe change 2026-08-31, at the user's instruction and confirmed against two
real "果酱双皮奶" sources (see `recipe_bible.md`/`recipe_sources.md`): this
dish is finished with a small jam dab after cooling, not served plain. This
reverses the earlier "no fruit... jelly" rule from the original H3 storyboard
- that rule is now wrong and superseded.

## Shared negative (all three segments)

Do not add a visible face, body, human reflection or human shadow; do not
add extra fingers, warped hands or more than one hand at a time. Do not add
captions, subtitles, watermarks, fake labels, price graphics, or a different
dish identity.

## Status

**All reference images ready.** `scene_anchor`, `cook_state` and `hero_state`
were all regenerated 2026-08-31 (jam garnish, gas-hob steaming, corrected
bowl size and colour - see `CURRENT_WORKFLOW.md` and the dish's own
`recipe_bible.md`/`recipe_sources.md` for the full history). `cook_state` and
the final `hero_state` were generated with `openai/gpt-image-2`; the rest
with `bytedance-seed/seedream-4.5`.

**Segment 1 test-rendered once already** (`bytedance/seedance-2.0`, 2026-08-31,
$1.87, saved at `local_artifacts/retake_frames/seedance_test_milk_seg1.mp4`)
under the old no-hand wording - the celadon bowl rendered tilted and hovering
in mid-air with nothing holding it for the last ~1.5s. Prompt rewritten
(this revision) to show a hand performing the pour naturally instead. Not
yet re-rendered with the fix - segment 1 should be run again before segment
2, same as any first test.
