# MiniMax H3 prompt spec, distilled

Condensed from the official skill at `MiniMax-AI/MiniMax-H3`, directory
`skills/h3-prompt-writing` (`SKILL.md`, `references/base-en.txt`,
`references/ref-en.txt`), read 2026-08-10. This is a working summary in our own
words, not a copy. Go upstream if a detail here is not enough.

Kept locally because we lost a day once relying on an external resource that we
could not reach when we needed it.

This file covers **structure only** — what the model expects. What survives our
4-step... now 8-step distilled Turbo LoRA is a separate matter, and those rules
live in `MINIMAX_H3_3X5_NATIVE1080_WORKFLOW.md` under "House rules".

For cooking-commercial production, use
`prompts/COOKING_PROMPT_PRODUCTION_STANDARD.md` before writing any clip prompt.
That standard requires real recipe web research, `recipe_sources.md`,
`recipe_bible.md`, reference prompts, H3 prompts, and English Reels
caption/subtitle assets in the output package.

## Which mode maps to which runner command

| Official mode | `h3_runner.py` | What it conditions on |
| --- | --- | --- |
| T2VA | `t2v` | text only |
| I2VA | `i2v` | a first frame |
| FL2VA | `flf2v` | a first frame and a last frame |
| L2VA | (not wired) | a final frame only |
| **Ref2VA** | **`r2v`** | **up to 9 reference images. Our production route** |

## Section structure

Plain labeled sections in this exact order. No JSON, no XML wrapper.

**T2VA / I2VA / FL2VA / L2VA** use three:

```text
integrated_multimodal_description:
overall_soundscape:
non_diegetic_music:
```

**Ref2VA** uses six:

```text
subject_definitions:
summary:
retention_analysis:
detailed_description:
overall_soundscape:
non_diegetic_music:
```

`overall_soundscape` is ambient and physical sound across the whole clip.
`non_diegetic_music` is score the characters cannot hear. Keep both even when
generating silent video: H3 samples video and audio in one joint latent, so the
sound description still shapes motion and pacing. `--no-audio` only skips the
audio decode at save time.

## Shots, timing, camera, dialogue

Number shots `[Shot 1]`, `[Shot 2]`, `[Shot 3]`. The first shot carries no
timestamp; every later shot opens with its cut time as `At MM:SS.mmm,`. Timings
must add up to the requested duration.

Write camera as a sentence combining motion type, amplitude and speed, for
example `the camera pushes in with small amplitude at slow speed`. Do not stack
abbreviations or invent shorthand.

Dialogue goes in `<d>[Language] line text</d>`, original language and punctuation
kept verbatim inside the tag while the surrounding description stays English.
Speakers get stable IDs `(S1)`, `(S2)`, assigned in order of first vocal
appearance and kept consistent across shots.

Describe composition, subjects, environment, actions, camera and sound. Do not
write plot summary or motivation, and never leave a reference label unresolved.

## Ref2VA specifics

`subject_definitions` declares every label used later, one per line, anchoring
each to where it comes from:

```text
<Subject 1> is the professional chef in <Picture 1>, mid-thirties, dark chef coat.
<Picture 5> is the raw rolled beef product image on a dark wooden tray.
```

`summary` opens with the task type, then one paragraph on how the references
relate to the target clip. For our ads the task type is `reference generation`.

`retention_analysis` gives one line per reference stating how strongly it is
carried into the video:

| For visible references | For audio references |
| --- | --- |
| `fully_preserved` | `fully_copy` |
| `partially_preserved` | `partially_copy` |
| `attribute_transfer` | `reference` |
| `weak_reference` | `weak_reference` |

`detailed_description` is the shot-by-shot body, 350-500 words for a generation
task.

**Label binding is positional.** `h3_runner.py` maps the `ref_images` list onto
`ref_images.ref_image_0..8` in order, so `<Picture 1>` is the first entry.
Reordering the JSON without reordering the prompt silently rebinds everything.

**Clips using `use_previous_last_frame_as_ref` shift by one.**
`h3_sequence_runner.py` prepends the carried frame, so `<Picture 1>` is the
previous clip's final frame and every JSON reference moves down a slot. Declare
that carried frame explicitly as the continuity anchor.

## Mode-specific opening rules, for when we use the other routes

**T2VA** — establish overall style and initial composition up front, then scene,
character and action. Nothing is anchored, so the whole timeline is constructed
from text.

**I2VA** — `<Picture 1>` *is* the actual first frame at 0.00 seconds. Establish
identity, clothing, colours and spatial relationships from it, then develop
forward. The clip starts at the image moment.

**FL2VA** — `<Picture 1>` anchors 0.00 seconds and `<Picture 2>` anchors the
final moment; describe the motion path connecting them. The last frame must be
reached by the final shot. Interpolation favours a single shot.

**L2VA** — `<Picture 1>` is the final frame only and does not inherently belong
to Shot 1. Infer a plausible earlier state, then converge gradually so the clip
lands on the reference image.

## Validator

`prompts/validate_prompt.py` checks section presence and order, word count,
undeclared labels, shot numbering and timestamp format, and that the highest
`<Picture N>` matches the number of references the sequence JSON actually binds.
