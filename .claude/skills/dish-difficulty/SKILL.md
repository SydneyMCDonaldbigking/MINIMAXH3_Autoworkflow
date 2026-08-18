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

## An intensity adjective is a number you did not measure

"Pale" and "pink" break a dish because they carry a raw/cooked ambiguity. The
same trap works on colour, and 2026-08-18 gave the first measured case.

A studio set was described as a **"saturated green tabletop"**. The template's
green and the rendered green, sampled from the actual pixels:

| | R | G | B | |
| --- | ---: | ---: | ---: | --- |
| template | **181** | 213 | 147 | soft pistachio, almost celery |
| rendered | **51** | 209 | 116 | chroma-key green |

G and B landed within a few points. **The single word "saturated" cost 130 points
of red** and turned a muted studio surface into a green screen.

The lesson is not "avoid saturated". It is that **intensity adjectives - saturated,
deep, rich, vivid, bright, pale, soft - are numbers, and if you have not looked at
the number you are guessing.** Sampling the reference costs one line of Pillow.

### And the reference beats the adjective anyway

The deeper error came first. A clean backdrop plate had already been cropped out
of the template, then dropped, on the reasoning that *"colour is the kind of thing
words handle well enough; ice geometry and liquid turbulence are what words fail
at."*

That reasoning was wrong, and the render is the proof. Colour is exactly what
words fail at, because every colour word is an intensity adjective. The fix was to
bind the plate as its own reference and mark it `attribute_transfer` with the
transfer scope written out: **only the two background colours and the horizon
height carry over; its emptiness does not.**

Which restates the oldest rule on file, in the place it is easiest to forget it:
when a reference image exists, use it. Deciding a picture is unnecessary because
the wording feels adequate is the same mistake as arguing with a clip that has
already been bound.

## Cropping evidence out leaves a hole the model will fill

Clip 02 of the Kirin rewrite went through three versions on 2026-08-18 and the
third is the instructive one, because it fixed the stated problem and broke
something worse.

| | Change | Result |
| --- | --- | --- |
| v1 | `saturated green tabletop` | chroma-key green, R=51 against a target of 181 |
| v2 | bound an empty backdrop plate as a 4th reference | green still wrong: the ice reference carried its own brighter green and outvoted the plate 1-to-3. Two lemon halves appeared at the frame edges despite `avoid fruit slices, citrus` |
| v3 | **cropped the green band off the ice reference** so the plate was the only green in the set | green landed in the right family - and the model invented a **white framed signboard with Japanese text and a lemon illustration** standing behind the bottle |

Cropping worked on the colour and created a signboard, because the crop turned a
reference that used to show a tabletop into one that shows a plain blue field.
Nothing in the prompt said what stood in that space, so the model furnished it.

This is the same failure as the blue "TOM YUMS" placard that appeared when the
brand logo was unbound from clip 03, and the burner that came back stamped
"Mini Max H3". **Absence of a picture is not a statement.** Three times now.

So cropping is a two-step fix, and the second step is not optional:

1. Crop the contradicting thing out of the reference.
2. **In the same edit, write what now occupies that space**, positively. Not
   "no sign, no poster" - the negatives never work - but "behind them the pale
   blue sweep is unbroken to the top of frame, with nothing standing on the table
   behind."

Doing step 1 alone trades a small edge defect for a large central one. v2's
lemons sit at the frame edge and an editor can crop them; v3's signboard is
directly behind the hero product and cannot be cropped out. **The regression
shipped as the worse take, so the delivered cut kept v2.**
