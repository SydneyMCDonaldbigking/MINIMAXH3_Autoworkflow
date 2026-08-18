# Chain Contract

This skill works only if the conversation state, prepared artifact, renderers, prompt compiler, and H3 runtime stay aligned.

## Separation Of Layers

- UI language controls opening copy, brief, detailed analysis, blocked-runtime guidance, and review text.
- Template spoken language controls generated presenter/voiceover behavior only for `human_voiceover`.
- Product image and local H3 references control visual truth.
- H3 runtime controls generation mechanics; it does not analyze the media.

If any layer conflicts with another layer, surface the conflict before H3 submission.

## Prepared Artifact

Before display, patching, confirmation, or generation, normalize the prepared artifact with `normalize_prepared_for_generation`.

The prepared artifact must contain:

- `request`: local template/product choices and H3 defaults.
- `viral_analysis`: observed template facts.
- `source_analysis`: observed product-image facts.
- `rewrite_brief`: transfer policy and generation direction.
- `rewrite_plan`: storyboard and prompt package.
- `prompt_preview`: user-readable summary plus compiled prompt preview.

Do not trust stale prompt fragments in loaded JSON. Normalization must refresh the H3 prompt preview and generation prompt.

## Renderer Contract

- `render_opening.py`: opening only. No confirmation phrase.
- `render_brief.py`: compact decision brief and confirm/detail/edit options.
- `render_detailed_analysis.py`: full detailed analysis, never a recap.
- `apply_brief_patch.py`: save patched prepared JSON and re-render the brief.
- `confirm_generation.py`: only frontstage confirmed-generation entrypoint.
- `render_missing_key_guidance.py`: compatibility filename; renders MiniMax H3 runtime guidance.
- `render_generation_result.py`: generated clips first, then run metadata and review checklist.

## H3 Preflight

Before real submission, block when:

- `h3_sequence_runner.py` or `h3_runner.py` is missing;
- product image or configured H3 references are not local files;
- reference count exceeds `8` configured images including product image;
- ComfyUI is unreachable at `H3_COMFYUI_SERVER` / `request.h3_server`;
- human presenter audio classification or spoken language is unresolved.

`--h3-dry-run` and `H3_DRY_RUN=1` skip ComfyUI reachability but still validate local files and write the H3 package.

## H3 Output Contract

`h3_runtime.py` must write artifacts outside the skill folder:

- `clip-01_ref2va.md`
- `clip-02_ref2va.md`
- `clip-03_ref2va.md`
- `sequence.json`
- `h3_sequence_runner.log`
- `sequence-manifest.json`

The result JSON should include:

- `provider: minimax_h3`
- `h3_run_id`
- `h3_manifest_path`
- `h3_sequence_json_path`
- `h3_clip_paths`
- `artifact.prompt_files`
- `artifact.runner_log_path`

Do not emit legacy remote-provider task fields in H3 result JSON. Use `h3_run_id`, `h3_manifest_path`, and `h3_clip_paths` as the generation identifiers.

## Regression Checks

When changing this skill, test at least:

- opening render in Chinese or English;
- rehearsal brief render;
- detailed-analysis render;
- confirmed-generation blocked path with ComfyUI unavailable;
- `--h3-dry-run` package generation from prepared JSON.

After changes, run a stale-wording scan against user-facing files. Include prior remote provider names, old resolution defaults, and obsolete release-package labels in the scan pattern.
