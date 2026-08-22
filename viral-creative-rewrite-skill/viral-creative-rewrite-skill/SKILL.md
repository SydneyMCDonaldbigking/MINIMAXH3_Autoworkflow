---
name: viral-creative-rewrite-skill
description: Guide a user through rewriting a template ad video into a MiniMax H3 / ComfyUI production package from a local product image and optional local H3 reference images. Use for viral ad template analysis, product-image-to-H3 rewrite planning, three-by-five-second Ref2VA prompt packages, ComfyUI H3 sequence submission, dry-runs, and reviewable independent clip handoff.
---

# Viral Creative Rewrite For MiniMax H3

## Purpose

Use this skill to turn a reference ad video into a MiniMax H3 production plan for a different product.

- Template video: borrow hook, pacing, shot order, camera language, satisfaction mechanics, and CTA function.
- Product image: preserve the product identity, shape, packaging, color, visible ingredients, and confirmed selling points.
- Optional H3 reference images: preserve local scene, character, hand, product-state, prep-state, or final-state references.
- Final output: three independent H3 clips for manual editing, not a finished concatenated edit unless the user explicitly asks.

Do not call external provider media analysis or remote video-generation APIs. The host agent performs video understanding and rewrite planning; MiniMax H3 through the local ComfyUI workflow is used only after the prepared brief is confirmed.

## Reference Loading

- Read `references/state_machine.md` when changing frontstage states, gates, opening copy, detailed-analysis behavior, confirmation, or blocked-runtime guidance.
- Read `references/workflow.md` when changing setup, prepare, execute, dry-run, local product-image handling, H3 sequence output, or review behavior.
- Read `references/prompt_alignment.md` when changing analysis schemas, rewrite planning, H3 prompt package structure, or Ref2VA prompt compilation.
- Read `references/chain_contract.md` when changing cross-layer behavior: prepared artifacts, renderers, prompt compiler, H3 preflight, sequence runner, bilingual parity, or regression coverage.

## H3 Production Defaults

Use the repo's MiniMax H3 defaults unless the user explicitly overrides them:

- Produce three independent `5s` vertical clips.
- Run `r2v` / Ref2VA at `1088x1920`, then crop accepted footage to exact `1080x1920` when needed.
- Use MiniMax H3 Turbo LoRA, `steps: 8`, `turbo_low_vram: true`, `ref_image_size: match`.
- Keep exported audio off by default: `no_audio: true`.
- Use `--no-concat` by default. The user usually wants to do the final edit manually.
- Keep the local reference stack at or below `8` images including the product image, because clips 02 and 03 prepend the previous clip's last frame and H3 supports at most `9` references.

Never store SSH passwords, API keys, signed URLs, raw provider responses, or base64 payloads in skill files, repo docs, logs, or final notes.

## Frontstage Flow

1. At startup, run `scripts/ensure_runtime.py --ui-language zh|en --print-python` from the skill root and use the printed Python for later skill scripts.
2. Show the opening by running `scripts/render_opening.py --ui-language zh|en` and forwarding the complete stdout.
3. Collect the grouped inputs: flow choice, template video, product image, optional local H3 references, product identity, audience, goal, constraints, and output defaults.
4. If the user chooses no-cost rehearsal, run `scripts/run_rewrite_video.py --rehearsal --prepare-only`; only show the example result after the user confirms.
5. For real preparation, inspect the selected template video and product image locally. For local videos, use `scripts/extract_video_frames.py --with-audio` at 1fps by default, then listen to audio when a visible mouth may indicate voiceover.
6. Write request, prepared, patch, result, cache, and test artifacts outside the skill folder.
7. Render the compact brief with `scripts/render_brief.py --prepared-input-json <prepared>` and forward the complete stdout.
8. If the user asks for details, run `scripts/render_detailed_analysis.py --prepared-input-json <prepared>` and forward the complete stdout.
9. Apply small direction edits with `scripts/apply_brief_patch.py --prepared-input-json <prepared> --patch-json <patch> --prepared-json <patched>` and forward the refreshed brief.
10. After explicit confirmation, run `scripts/confirm_generation.py --prepared-input-json <prepared> --env-file .env --ui-language zh|en`.

The confirmation step checks the prepared contract, local product/reference files, H3 workflow root, and ComfyUI reachability. If H3 is not ready, it prints a reusable-brief snapshot plus MiniMax H3 setup guidance; do not replace that with a short manual answer.

## Analysis Rules

Classify the template before writing the rewrite:

- `visual_product_texture`: product, food, drink, static material, ingredient, or texture ads. Borrow shot order, camera pacing, product-state changes, texture/satisfaction points, scene mood, and music mood. Do not invent voiceover or lip sync.
- `human_demo`: visible human demonstration, try-on, hand-use, or presenter action without strong speech. Borrow human framing, action sequence, expression/eye-contact when structurally important, product-human relationship, and real scene context.
- `human_voiceover`: presenter or creator with spoken explanation. Borrow broad person/market visual context, template spoken language, voiceover rhythm, mouth/gesture synchronization, real scene, and action order. Generate a new non-identical person and original wording.
- `platform_cta`: platform, account, search, or CTA pages. Borrow only the closing function; do not inherit platform UI, account, watermark, captions, or blank ending.
- `mixed`: use only when several mechanisms are equally central, then expose the active transfer slots before confirmation.

If demo versus voiceover is ambiguous, block confirmation until the audio track has been inspected or the user chooses the route.

## H3 Prompt Rules

Write prompts as physical commercial direction, not generic cinematic prose.

For each five-second clip, use three planned shots by default:

- `0.0-1.6s`: establish action and spatial context.
- `1.6-3.4s`: one close-up or medium close-up action insert.
- `3.4-5.0s`: endpoint shot with a clean handoff.

Each H3 Ref2VA prompt must use the official six plain labeled sections:

```text
subject_definitions:
summary:
retention_analysis:
detailed_description:
overall_soundscape:
non_diegetic_music:
```

Bind `<Picture N>` labels positionally to `ref_images`. Clips 02 and 03 shift by one because the previous clip's last frame is prepended as `<Picture 1>`.

Prefer stable camera language: `locked-off`, `slow push-in 4 cm`, `short downward tilt`, `tiny rack focus`, or `gentle pull-back 10 cm`. Avoid stacking pan, tilt, dolly, and rack focus in one shot. Use one actor and one physical action per shot. Avoid tight close-ups of hands working tools.

## Execution Outputs

`scripts/h3_runtime.py` writes:

- three `clip-*_ref2va.md` prompt files;
- `sequence.json`;
- `h3_sequence_runner.log`;
- `sequence-manifest.json`;
- generated clip paths when ComfyUI generation succeeds.

Use `--h3-dry-run` to build and validate the H3 package without submitting to ComfyUI.

After real generation, render the result with `scripts/render_generation_result.py --result-json <result>` and show the generated clips first, followed by H3 run ID, manifest path, and a short manual review checklist.
