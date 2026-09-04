# Iced Hainan Coconut Coffee — Seedance 3×5s storyboard (2026-08-31 v2)

Rewritten at the user's instruction to match a specific build order and a
more deliberate camera style than the first draft. Still 3 independent
Seedance segments (cheaper to redo one bad roll than the whole 15s), chained
by extracting each segment's real last frame with `ffmpeg` and feeding it
forward as the next segment's `first_frame`. `hero_state` is a reference only
for segment 3, per the same clip-boundary discipline as the H3 fix.

**Recipe order (user-specified 2026-08-31):** empty glass → add ice → add
coffee → pour coconut milk → **stir until the two colours blend together.**
This reverses the first draft's "never let the two liquids fully blend"
instruction - that was written for a *layered* presentation and is wrong for
what was actually asked. The drink now ends mixed, not layered.

**Camera style (user-specified 2026-08-31):** alternate close and wide shots
within and across segments rather than only tightening in; use more than one
angle per segment; include one committed, definite orbiting camera move (not
a hedge - see `CURRENT_WORKFLOW.md`'s "commit the camera or lock it off"
rule, the most stable third measured so far is also the one with the
*largest* camera motion); keep the lighting and materials premium throughout.

**Revision 2026-08-31 (v3): hands are now allowed**, same call as
`homestyle_double_skin_milk`'s storyboard - avoiding hands for pour/stir
actions is what made `milk_seg1`'s real Seedance render show a bowl tilted
and hovering in mid-air with nothing holding it (see that dish's Status
section and memory `no-person-unseen-actor-anti-pattern`). A hand and
forearm may now perform any pour or stir naturally; face, body, and any
human reflection or shadow stay out of frame.

## Segment 1 — empty glass, ice, coffee (~5s)

```json
{
  "model": "bytedance/seedance-2.0",
  "prompt": "<SEG1 PROMPT>",
  "duration": 5,
  "resolution": "1080p",
  "aspect_ratio": "9:16",
  "generate_audio": false,
  "frame_images": [
    { "type": "image_url", "image_url": { "url": "outputs/reference_assets/48_hainan_coconut_coffee/generated/hainan_coconut_coffee_scene_anchor-1.png" }, "frame_type": "first_frame" }
  ]
}
```

```text
A working Hainan coffee kitchen: sea-glass teal terrazzo prep counter, warm
weathered teak shelves, pale sand plaster, a brushed stainless espresso
machine, palm-filtered morning light. A home barista's hand and forearm may
enter frame to perform kitchen actions naturally; face, body, and any human
reflection or shadow stay out of frame throughout.

Wide three-quarter shot on the opening layout: the exact supplied
coconut-milk carton upright at left, one tall ribbed glass standing empty on
the terrazzo counter, clear ice cubes waiting in a small dish beside it, a
small glass beaker of dark espresso, the espresso machine behind. The glass
is the clear subject of the shot and is visibly empty.

Cut to a close glass-height insert: one hand tips the small dish and lets
clear ice cubes settle once into the empty glass, then withdraws; the ice
catches the morning light.

Cut to a wide three-quarter shot, a different angle than the opening: one
hand lifts the glass beaker and pours dark espresso in one controlled
stream into the glass, filling the space around the ice, then sets the
beaker back down. End held on this exact state - coffee and ice only, glass
roughly half full, no coconut milk anywhere yet.
```

## Segment 2 — coconut milk pour (~5s)

```json
{
  "frame_images": [
    { "type": "image_url", "image_url": { "url": "<last frame extracted from segment 1>" }, "frame_type": "first_frame" }
  ]
}
```

No `last_frame` set - the mixed-colour end state segment 3 needs does not
exist as an asset yet (the old `cook_state` shows an unmixed swirl, which
would contradict the new stir-to-blend ending). Let the prompt drive it.

```text
Same kitchen and glass, continuing exactly from the first frame: dark coffee
and ice, glass roughly half full. A home barista's hand and forearm may
enter frame to perform kitchen actions naturally; face, body, and any human
reflection or shadow stay out of frame throughout.

Close glass-height insert: one hand lifts the coconut-milk jug and pours a
steady narrow ribbon in, filling the glass to near the rim as it moves
through the dark coffee, blooming into feathery brown-and-cream swirls, then
sets the jug back down.

Cut to a wide three-quarter shot from a new angle: the full glass rests on
the terrazzo counter, the coffee-and-coconut layers still visibly distinct
and unmixed. End held on this exact state - full glass, layers not yet
stirred, ready for mixing in the next segment.
```

## Segment 3 — stir to blend, orbit, hero (~5s)

```json
{
  "frame_images": [
    { "type": "image_url", "image_url": { "url": "<last frame extracted from segment 2>" }, "frame_type": "first_frame" },
    { "type": "image_url", "image_url": { "url": "outputs/reference_assets/48_hainan_coconut_coffee/generated/hainan_coconut_coffee_hero_state-1.png" }, "frame_type": "last_frame" }
  ]
}
```

```text
Same kitchen and glass, continuing exactly from the first frame: the full
glass with distinct coffee and coconut layers. A home barista's hand and
forearm may enter frame to perform kitchen actions naturally; face, body,
and any human reflection or shadow stay out of frame throughout.

Close glass-height insert: one hand holds a thin cocktail stirrer and makes
two slow circles inside the glass, then withdraws; the two liquids turn
together into one even light-brown colour, glossy and cold, with no foam or
separation left.

Cut to a wide shot. The camera performs one committed slow orbit,
half-circling the glass on the terrazzo counter while the espresso machine
and shelving pass smoothly through the background - a definite, continuous
move, not a small drift.

Calm final hero, straight on: the tall iced coconut coffee sits centred on
the terrazzo counter, its colour now one even light brown throughout, with
one small saucer of espresso beans set aside and the espresso machine
softly blurred behind - matching the last frame exactly.
```

## Shared negative (all three segments)

Do not add a visible face, body, human reflection or human shadow; do not
add extra fingers, warped hands or more than one hand at a time. Do not add
captions, subtitles, watermarks, price graphics, straws left standing
unexplained, boba, whipped cream or café seating.

## Status

**All reference images ready.** `scene_anchor` (empty glass, everything
staged statically - no mid-pour or floating objects) and `hero_state`
(stirred, one even blended colour) were both regenerated 2026-08-31 with
`bytedance-seed/seedream-4.5`; two `openai/gpt-image-2` attempts at
`scene_anchor` were tried and rejected (filled the glass despite explicit
"empty" instructions, and once showed the coffee pitcher hovering mid-pour
with no visible support - see `CURRENT_WORKFLOW.md` and memory
`no-person-unseen-actor-anti-pattern` for the general lesson). Prompt text
revised to allow a hand for every pour/stir (see the milk dish's Status for
why). No Seedance video call has been made yet for this dish - no video cost
spent. Ready to run segment 1 as the first real test.
