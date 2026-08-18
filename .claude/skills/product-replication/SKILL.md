---
name: product-replication
description: Rebuild someone else's product commercial as an ad for our own single product - borrowing its staging and rhythm while replacing every trace of its brand, props and semantics. Use when working from a template video rather than shooting an original dish.
---

# Replicating a product commercial

This is not the cooking flow. A dish ad is built from scratch: we choose the cook,
the kitchen, the ingredient and the beats, and the reference images are generated
to match. A replication starts from **somebody else's finished film**, and almost
every problem comes from the same tension: borrow the structure, inherit none of
the content.

For original cooking ads see `dish-difficulty` instead. What the two share is only
the H3 prompt format (`prompts/H3_OFFICIAL_PROMPT_SPEC.md`), the validator, and the
runners.

## The split that has to hold

| Borrow from the template | Never inherit |
| --- | --- |
| set: backdrop sweep, surface, risers | their brand, logo, end card |
| camera grammar: locked-off, one small push, hard cuts | their product, and every variant of it |
| beat order: place, prove, land | their flavour semantics (their fruit, their tea, their claims) |
| the *technique* of dressing the base with raw material | the specific raw material they dressed with |

That last row is the one that gets half-applied. The template dressed the foot of
every shot with the raw material of that flavour - pears, limes, dry oolong leaves.
Excluding their pears is correct. Leaving the surface bare is not: **borrow the
technique and swap in our product's own raw material.** For a Ceylon straight tea
that is dry black tea leaves, which is also what the label claims.

## Get the reference images out of the template

This is where most of the quality comes from, and it is worth more than any amount
of prompt wording.

1. **Re-extract at native resolution.** The 1fps analysis frames are downscaled and
   too soft to bind. Pull the moment you want straight from the source with
   `ffmpeg -ss <t> -i source.mp4 -frames:v 1`.
2. **Crop the contamination out.** Nearly every template frame carries their
   product, their fruit, or burnt-in ad copy. Whatever stays in the crop gets
   rendered, because a reference image always beats the wording.
3. **Then say what fills the hole.** See the section below; this step is not
   optional.
4. **Bind with an explicit transfer scope**, never a generic one. See below.

## Write what transfers and what does not

A generic `attribute_transfer. Use only the relevant attributes` says nothing.
References vote against each other, and the vote is settled by weight of evidence,
not by which one you meant.

Clip 02 of the Kirin ad bound four references. A clean backdrop plate carried the
correct muted green; the ice reference carried its own brighter green. One vote
against three, and the green came out wrong.

Write both halves:

```text
<Picture 3>: attribute_transfer. How the stream holds together and folds over ice
transfers. Its framing and its darker colour do not; the tea in this clip is the
lighter transparent amber of <Picture 1>.
```

## An intensity adjective is a number you did not measure

`dish-difficulty` records that "pale" and "pink" break a dish, because each
carries a raw/cooked ambiguity. Replication has its own version of that trap and
it bites on colour, where 2026-08-18 gave the first measured case.

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

This is the same failure the cooking flow hit twice - the blue "TOM YUMS" placard
that appeared once the brand logo was unbound from clip 03, and the burner that
came back stamped "Mini Max H3". **Absence of a picture is not a statement.**
Three times now, across both flows, which is why it sits in both skills.

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


## What this skill does not cover

- The H3 prompt format itself: `prompts/H3_OFFICIAL_PROMPT_SPEC.md`, enforced by
  `prompts/validate_prompt.py`. Shared with the cooking flow.
- Which card to rent and what it costs: `docs/runbooks/GPU_CARD_REFERENCE.md`.
- Turning acceleration on for a sequence: `h3_accel_shim.py`.
- Original cooking ads, where the references are generated rather than cropped
  out of somebody else's film: `dish-difficulty`.
- Subtitle and caption copy: `reels-captions`. Note that a replication's product
  may carry a claim the copy must not overstate - the Kirin label reads
  `甘さすっきり 低カロリー`, which is low-calorie **sweetened** tea, not unsweetened.

## Where the worked example lives

`local_artifacts/kirin_straight_tea_rewrite/` - the prompts, the four cropped
template references, the product image, and `README_PROMPT_NOTES.md` recording
every change and why. The finished ad is `final/kirin_straight_tea_sage_1080x1920.mp4`.

Skill upgrades still outstanding are specified in
`docs/runbooks/SKILL_UPGRADE_HANDOFF.md`.
