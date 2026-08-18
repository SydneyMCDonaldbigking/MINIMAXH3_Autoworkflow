# Workflow

## Purpose

Rewrite a user's product image into a MiniMax H3 production package by borrowing only the creative pattern from a template video.

The full frontstage state contract lives in `references/state_machine.md`. Cross-layer prepared/prompt/execution requirements live in `references/chain_contract.md`.

## Conversational Flow

1. Bootstrap the skill runtime from the skill root:
   - Chinese: `python scripts/ensure_runtime.py --ui-language zh --print-python`
   - English: `python scripts/ensure_runtime.py --ui-language en --print-python`
   - Use the printed Python path for later skill scripts.
2. Open with `scripts/render_opening.py --ui-language zh|en` and forward stdout.
3. Explain the two core inputs and optional H3 references:
   - Template video supplies ad structure only.
   - Product image is the product truth.
   - Optional local H3 reference images may supply scene, character, hands, prep/product states, or final hero states.
4. Collect grouped inputs: flow, media, product/generation direction, optional H3 references, output defaults, and H3 runtime readiness.
5. For no-cost rehearsal, run the bundled rehearsal through brief, optional detailed analysis, confirmation gate, and sample result without calling MiniMax H3.
6. For real preparation, the host agent inspects media locally and writes prepared JSON outside the skill source. For local videos, use `scripts/extract_video_frames.py --with-audio`, sample at 1fps by default, and listen to audio when a visible mouth may indicate voiceover.
7. Classify the template profile before planning: `visual_product_texture`, `human_demo`, `human_voiceover`, `platform_cta`, or `mixed`.
8. Show the compact brief with `scripts/render_brief.py --prepared-input-json <prepared>`.
9. If requested, show full detailed analysis with `scripts/render_detailed_analysis.py --prepared-input-json <prepared>`.
10. Patch small edits with `scripts/apply_brief_patch.py`.
11. After explicit confirmation, run `scripts/confirm_generation.py --prepared-input-json <prepared> --env-file .env --ui-language zh|en`.
12. If H3 is not ready, the confirmation command prints the reusable-brief snapshot and H3 setup guidance. Do not hand-write a shorter setup reply.
13. If H3 is ready, the runner writes three prompt files and `sequence.json`, calls `h3_sequence_runner.py run --no-concat`, and returns generated clip paths plus manifest.
14. Render final results with `scripts/render_generation_result.py --result-json <result>`.

## H3 Runtime Defaults

- `H3_WORKFLOW_ROOT`: defaults to the parent workflow repo when this skill lives inside it.
- `H3_COMFYUI_SERVER`: defaults to `http://127.0.0.1:8189`.
- `H3_OUTPUT_ROOT`: defaults to `<workflow_root>/sequence_outputs`.
- `--h3-dry-run`: writes the package and runner command without submitting to ComfyUI.

Generation uses three independent `5s` clips, `1088x1920`, R2V/Ref2VA, Turbo LoRA, `8` steps, `turbo_low_vram`, `ref_image_size: match`, and `no_audio`.

## Implementation Notes

- The skill does not call any external remote video-generation API.
- Local product/reference images are passed as local file paths to the ComfyUI H3 runner. Remote image URLs must be downloaded by the user/agent first.
- Keep all generated request/prepared/result/package files outside the skill folder.
- The source package must not gain an `output/` directory during testing.
