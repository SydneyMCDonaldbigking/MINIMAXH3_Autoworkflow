# Preproduction Package Template

Copy this template into:

```text
sequence_outputs/<dish_slug>/preproduction/
```

Then replace every `TODO` before video generation. Real output packages remain
ignored by git; this template is the tracked source for the package shape.

Required checks before generation:

- `recipe_sources.md` records at least two recipe sources, plus a safety source
  for poultry, meat, seafood, egg, or reheating.
- `recipe_bible.md` converts recipe facts into visual states and clip beats.
- `h3_prompts/clip_01_ref2va.md`, `clip_02_ref2va.md`, and
  `clip_03_ref2va.md` pass `prompts/validate_prompt.py`.
- `analysis/caption-cues/*.json` parses as JSON.
- Video prompts forbid generated subtitles, title cards, labels, overlays,
  watermarks, and floating logos.
