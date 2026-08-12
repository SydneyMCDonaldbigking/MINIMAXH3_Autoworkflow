---
name: dish-difficulty
description: Judge before rendering whether a dish will come out clean, and what it needs written explicitly. Use when adding a dish, when a config is drafted, or when deciding what to spend GPU time on next.
---

# How hard is this dish going to be

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

1. **A beat with no reference image.** If an action happens in a clip and no
   reference shows that action, it will not happen. Tom yum's prawns go in during
   clip 03, whose only cooking anchor was the finished bowl, so the ad tipped raw
   prawns into a plated soup. A fifth reference of prawns dropping into the pot
   fixed it in one pass. See `extra_subject` in the dish config.
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
- List every action that happens in clip 03. If any of them is a cooking action
  rather than a plating action, the dish needs an `extra_subject` reference.
- Grep the config for `pale`, `pink`, `light`, `soft`, `golden` and check each one
  cannot be read as undercooked.
- For every ingredient whose size matters, check it is described relative to
  another thing in the same frame, not in absolute units alone.

Two minutes here against 24 minutes of GPU time plus a review round trip.
