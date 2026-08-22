# Cooking Prompt Production Standard

Use this standard whenever writing prompts for a cooking commercial, especially
MiniMax H3 Ref2VA clips and the matching Instagram Reels deliverables.

This is the production layer above `H3_OFFICIAL_PROMPT_SPEC.md`. The official
spec defines the prompt container. This file defines what must be researched,
distilled, written, and saved before video generation.

## Non-Negotiable Rule

For every new dish, search the web for real recipes before writing prompts.
Do not rely on memory for ingredient order, cooking method, temperature, time,
texture, or doneness.

Use at least:

- two real recipe sources for the dish or a very close cooking method;
- one safety or authority source when raw poultry, meat, seafood, egg, or
  reheating is involved;
- the supplied product image as the product identity source.

Record source URLs and the extracted production facts in `recipe_sources.md`.
Paraphrase. Do not copy a full recipe or long source passages.

## Distillation Steps

1. Identify the dish, product form, target region, and cooking appliance.
2. Search real recipes and extract only production-useful facts:
   ingredients, cut/prep state, marinade/resting needs, cooking sequence,
   equipment, heat source, temperature, timing, doneness, garnish, and final
   texture.
3. Convert recipe facts into visible food states:
   product state, prep state, cooking state, intermediate transformation,
   final hero state.
4. Convert those states into the clip story:
   clip 01 product hook and first preparation action, clip 02 cooking or heat
   transformation, clip 03 finish, serve, and hero.
5. Write reference prompts first, then H3 clip prompts, then Reels caption and
   editable subtitle cues.

## Required Output Package

Save preproduction assets under the real output tree, even before video exists:

```text
sequence_outputs/<dish_slug>/preproduction/
  product_reference.<ext>
  recipe_bible.md
  recipe_sources.md
  reference_prompts/
    character_scene.md
    prep_state.md
    cook_state.md
    hero_state.md
  h3_prompts/
    clip_01_ref2va.md
    clip_02_ref2va.md
    clip_03_ref2va.md
  social/
    ig_reel_caption.txt
    reels_subtitles.srt
    reels_caption_cues.md
  analysis/
    caption-cues/
      clip-01.json
      clip-02.json
      clip-03.json
```

Add extra reference prompts when the recipe needs a specific process state:
`oven_tray_state.md`, `steamer_state.md`, `simmer_state.md`,
`frying_state.md`, `sauce_state.md`, or similar.

When a real run directory exists, copy or regenerate the social files into that
run directory as well, so the MP4s, prompt notes, caption, subtitles, and source
notes travel together.

## Recipe Bible

`recipe_bible.md` must contain:

- production use;
- real recipe basis;
- source list;
- concise original recipe plan;
- visual food states;
- commercial beat chain.

The recipe plan is for direction and review. The H3 prompt should not become a
recipe paragraph. It should become physical commercial action.

## Reference Prompts

Reference prompts should teach H3 what it cannot infer reliably:

- character or no-face cook and fixed kitchen;
- product identity from the supplied image;
- exact prep/cut/marinade state;
- active cooking state with the correct appliance or heat source;
- finished hero state.

For cooking process references, describe exact physical state: cut size,
marinade thickness, flame, tray/rack, steam, bubbling sauce, doneness, garnish,
and colour. Avoid vague words like `delicious`, `perfect`, or `cinematic`
without physical proof.

Do not place brand text in generic process-state references. Use the official
logo only as an actual brand reference or physical sign when the video route
requires it.

## H3 Ref2VA Prompt Requirements

Every H3 cooking clip prompt must remain in English and use the six-section
Ref2VA container:

```text
subject_definitions:
summary:
retention_analysis:
detailed_description:
overall_soundscape:
non_diegetic_music:
```

The clip body must follow local H3 rules:

- exactly three shots by default;
- `[Shot 1]` has no timestamp;
- `[Shot 2]` starts with `At 00:01.600,`;
- `[Shot 3]` starts with `At 00:03.400,`;
- each shot names shot size, angle, lens/focus, start frame, action mechanics,
  camera move or explicit lock-off, ending frame, and handoff;
- every beat is a directional action that completes inside its window;
- one action and one actor per shot;
- no tight close-up of a hand working a tool;
- ingredient identity is described inside the shot text, including what it is
  not when confusion is likely;
- no subtitles, captions, title cards, labels, lower-thirds, watermarks, or
  floating logos inside generated video.

Keep `overall_soundscape` and `non_diegetic_music` even for silent output; they
shape motion and pacing, but native audio remains off unless explicitly chosen.

For motion wording, apply the local keyword guide in
`prompts/H3_MOTION_KEYWORDS.md`. In short 5s clips, fewer actions and smaller
amplitude are more reliable. Prefer `locked-off`, `one controlled low
movement`, `two slow broad pushes only`, `one slow folding sweep`, `pause so
the texture stays readable`, and `hold still for the final half-second`. Avoid
`quick`, `rapid`, `tosses through`, `wok shaking`, `airborne food`, repeated
tool strokes, and layered camera movement during busy food motion.

## Reels Deliverables

Write these with the prompts, not after the edit:

- `social/ig_reel_caption.txt`: natural English caption, short hook, recipe
  logic, safe CTA, and relevant hashtags;
- `social/reels_subtitles.srt`: full-timeline subtitle draft for quick preview;
- `analysis/caption-cues/clip-XX.json`: clip-relative editable caption cues.

Caption cue text must be 2-6 words, tied to visible action, and free of prices,
availability claims, fake UI, or unsupported health claims. Captions are external
editing data only. The video generation prompt must still forbid generated
subtitles and overlays.

## Validation Checklist

Before video generation:

- `recipe_sources.md` exists and records the recipe and safety sources used;
- `recipe_bible.md` maps recipe facts into visual states and clip beats;
- all generation prompts are English;
- H3 prompts pass `prompts/validate_prompt.py`;
- caption cue JSON parses;
- if a sequence JSON exists, validate prompts through that sequence so
  `<Picture N>` count includes `use_previous_last_frame_as_ref`;
- every prompt keeps brand/logo as a physical prop or reference only, never a
  floating overlay;
- social caption and subtitles live in the same output package as the prompts.
