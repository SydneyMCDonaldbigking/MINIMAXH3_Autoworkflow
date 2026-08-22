# Prompt Alignment

## Layers

Keep these layers separate:

- Template analysis: what is observed in the reference ad.
- Product/reference analysis: what the product image and local H3 references prove.
- Rewrite brief: what to borrow, what to preserve, and what to forbid.
- Prompt preview: user-readable decision summary.
- H3 prompt package: three Ref2VA clip prompts plus `sequence.json`.

The user-facing language may be Chinese or English. H3 clip prompts should be concrete physical commercial direction; English is acceptable even in a Chinese UI when it improves H3 prompt clarity.

## H3 Clip Shape

Default output is three independent five-second clips:

1. Clip 01: opening hook and product identity.
2. Clip 02: product proof, texture, transformation, or use mechanics.
3. Clip 03: satisfaction close and product-visible CTA.

Each clip should contain exactly three planned shots:

- Shot 1: 0.0-1.6s, establish action and spatial context.
- Shot 2: 1.6-3.4s, one close or medium-close action insert.
- Shot 3: 3.4-5.0s, endpoint and handoff.

Use one physical action per shot. Prefer locked-off or one small camera move. Avoid stacked camera moves, vague "dynamic camera" language, and tight tool/hand close-ups.

## Ref2VA Format

Every clip prompt must use these sections in order:

```text
subject_definitions:
summary:
retention_analysis:
detailed_description:
overall_soundscape:
non_diegetic_music:
```

Do not wrap the prompt in JSON or XML. `detailed_description` should use `[Shot 1]`, `[Shot 2] At 00:01.600,`, and `[Shot 3] At 00:03.400,`.

## Reference Binding

`<Picture N>` labels bind positionally to `ref_images`.

Clip 01:

- `<Picture 1>` is `ref_images[0]`.
- The product image should be declared as the product identity truth.

Clips 02 and 03:

- `<Picture 1>` is the previous clip's final frame.
- The configured `ref_images` shift down by one.

The runtime limits configured local references to `8` images including the product image, because carried frames make the total `9`.

## Compilation Guardrails

The final prompt package must forbid:

- template product leakage;
- fake labels or small invented text;
- subtitles, captions, watermarks, price tags, shopping UI, platform UI;
- blank/product-free endings;
- product identity drift across clips;
- human voiceover or lip-sync constraints in `visual_product_texture` templates.

For `human_voiceover`, keep the original template spoken language and block generation when the language or audio-track status is unconfirmed.
