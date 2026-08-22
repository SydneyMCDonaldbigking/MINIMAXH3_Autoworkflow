---
name: dish-difficulty
description: Judge before rendering whether a dish will come out clean, and what it needs written explicitly. Use when adding a dish, when a config is drafted, or when deciding what to spend GPU time on next.
---

# How hard is this dish going to be

**This is the original cooking flow only** - a dish we stage ourselves, whose four
or five reference images are generated to match. Rebuilding somebody else's
commercial from a template video is a different job with different failure modes,
and lives in `product-replication`. What the two share is the H3 prompt format,
the validator, and the runners; nothing else transfers cleanly.

## The question that predicts failure

Look at the `cook_state` reference and ask: **how many things in this frame must
the viewer be able to tell apart?**

Not how many ingredients the recipe has. How many must be individually legible.

| Distinguishable things | What to expect |
| --- | --- |
| 1-2 | Renders clean first try |
| 4-5 | Works, but every size, colour and order must be written explicitly |
| 8+ | Change the dish |

## Why it is not ingredient count

Ingredient count predicts nothing. Two counter-examples from 2026-08-12:

- **Salmon ochazuke** has the fewest ingredients in the set and still failed,
  because the salmon rendered as raw sashimi. One ingredient, one wrong state.
- **Kung pao chicken** has the most - chicken, carrot, cucumber, peanuts, dried
  chillies, Sichuan pepper, aromatics, a pre-mixed sauce - and rendered clean.

The braised drumsticks are the clearest case. The pot holds ginger, spring onion,
star anise, cassia, bay, black cardamom, peppercorns and soy, which is eight
ingredients, and it was the cleanest ad of the day. **None of them has to be
recognised.** They sit in dark braising liquid as background. The only thing in
that frame that must read is the drumstick.

Kung pao is the inverse: five things in the wok, all of which must be seen and
told apart, each entering at a different moment. It took three passes.

## The three things that actually break a dish

1. **A beat assigned to the wrong clip.** A clip has an identity, and its whole
   reference set votes on what that identity is. An action that contradicts it
   will not render there, however many references you add or how plainly you word
   it. This is the strongest rule on the page and it was learned the expensive
   way; the section below is the whole story.
2. **An adjective with a raw/cooked ambiguity.** "Pale" is accurate for simmered
   pork and rendered it pink. "Pink" is accurate for cooked salmon and rendered
   sashimi. Both times the fix was a positive statement of the cooked state -
   "opaque grey-brown, fibres separating, no pink anywhere" - plus an explicit
   denial of the raw reading.
3. **Sizes and order that only exist in the text.** Kimchi came back as whole
   leaves while the beef beside it came back correctly diced, because the upstream
   reference showed whole leaves. Anything that must be a particular size has to
   be stated against something else in the same frame: "chopped smaller than the
   beef dice", "the rice is clearly the largest quantity".

## Use it before spending money

When a config is drafted, before generating references:

- Count the distinguishable things in the planned `cook_state`. If it is over
  five, simplify the dish or split the beat.
- List every action in each clip and check it against that clip's reference set.
  A cooking action in clip 03 is not fixed by adding a reference; **move it into
  clip 02**. See the section below.
- Grep the config for `pale`, `pink`, `light`, `soft`, `golden` and check each one
  cannot be read as undercooked.
- For every ingredient whose size matters, check it is described relative to
  another thing in the same frame, not in absolute units alone.

Two minutes here against 24 minutes of GPU time plus a review round trip.


## Move the beat, do not out-argue the clip

Tom yum took three renders. The first two failed the same way and the second is
the useful one, because it did exactly what this page used to recommend and still
failed.

| | Change | Result |
| --- | --- | --- |
| v1 | - | Prawns never entered the pot; clip 03 tipped raw prawns into a finished bowl |
| v2 | Added an `extra_state` reference of prawns dropping into the pot, bound it into clip 03, rewrote the beat to say "into the boiling pot" | **Still tipped them into the bowl.** The pot appeared only in the second shot |
| v3 | Moved the prawns into clip 02. Added nothing | Correct throughout |

Clip 03 binds character, working-state, hero bowl and product. Those four
together say *this is the end*. Dropping one contrary picture into that set is
one vote against three, and the model resolved it the way the majority pointed:
it plated first, then grudgingly showed the pot. The reference was not ignored,
it was outvoted.

Clip 02 binds nothing but pot and heat. The same action costs nothing there.

**So the diagnostic is not "does this beat have a reference" but "does this beat
belong to this clip".** Read each clip's reference list and name what stage of
cooking it depicts. If a beat names a different stage, the beat is in the wrong
clip. Adding pictures cannot fix that; moving the beat costs nothing.

The same run showed the other half of the split. Clip 01 was running the chilli
paste, which is clip 02's job, so every later stage shifted one beat late and the
prawns were squeezed out of the cooking clips entirely. **A beat that arrives too
early in clip 01 pushes the dish's real subject out of the far end.** Check both
ends of the split, not just the one that failed.

### And the leftover

Removing a reference is not the same as excluding a thing. With the brand logo
unbound from clip 03, the model invented its own signboard - a blue "TOM YUMS"
placard - in the final frame. Absence of a picture is not a statement. The clip
now says what the frame contains: the dish, its vessel, the table, the cook. That
is the same fix as the burner that came back stamped "Mini Max H3", and it is the
same fix every time.


## Not covered here

- Working from a template video instead of staging our own shoot:
  `product-replication`. Colour sampled off a template, cropping other people's
  products out of borrowed frames, and per-reference transfer scope all live there.
- The prompt format: `prompts/H3_OFFICIAL_PROMPT_SPEC.md`, checked by
  `prompts/validate_prompt.py`.
- Caption copy: `reels-captions`.
