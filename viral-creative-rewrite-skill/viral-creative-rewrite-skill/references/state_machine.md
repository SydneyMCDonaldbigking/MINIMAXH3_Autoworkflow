# State Machine

The skill is a frontstage state machine. Do not expose later-state actions before their state exists.

## START_OPENING

Entry command: `scripts/render_opening.py --ui-language zh|en`

Allowed output:

- What the skill does.
- Template video role.
- Product image and optional local H3 reference image roles.
- Default media previews.
- Similar category/use-scene guidance.
- Face/reference stability guidance.
- Grouped input request.
- H3 runtime readiness note.

Forbidden output:

- `确认生成`
- `confirm generation`
- `--confirmed-brief`
- Any request to approve final generation before a prepared brief exists.

## REHEARSAL_BRIEF

Entry command: `scripts/run_rewrite_video.py --rehearsal --prepare-only`

Allowed output:

- Rehearsal status.
- Compact brief.
- Detailed-analysis option.
- Edit option.
- Confirmation option for the rehearsal result only.

Forbidden output:

- Calling MiniMax H3.
- Claiming a new video was generated.
- Treating setup-only as the user-facing rehearsal.

## REAL_ANALYSIS_REQUESTED

Entry: user chooses real analysis/preview.

Allowed work:

- Extract local video frames with `scripts/extract_video_frames.py --with-audio`.
- Listen to audio if visible mouth movement may imply voiceover.
- Inspect the product image and optional references.
- Write prepared JSON outside the skill source.

Allowed frontstage output:

- Short progress only.

Forbidden frontstage output before `BRIEF_READY`:

- Raw prepared JSON.
- Full prompt payloads.
- Large command payloads.
- Detailed conclusions that should first appear in the rendered brief.

## BRIEF_READY

Entry command: `scripts/render_brief.py --prepared-input-json <prepared>`

Allowed output:

- Compact brief.
- Template structure.
- Product anchors.
- Generation direction.
- H3 defaults.
- Forbidden carryover.
- Risk controls.
- Natural-beat prompt preview.
- Options: view detailed analysis, edit, or confirm generation.

Only in this state may the frontstage include `确认生成` / `confirm generation`.

## DETAIL_VIEW

Entry command: `scripts/render_detailed_analysis.py --prepared-input-json <prepared>`

Output must include the full detailed-analysis body:

- Template basic facts.
- Template profile and reason.
- Audio/subtitle/voiceover state.
- Camera/editing.
- Every-five-second windows.
- Borrowable elements and forbidden carryover.
- Product-image analysis.
- Confirmed/unproven claims.
- Proposed generation script.
- H3 constraints.
- Next edit/confirm options.

Never answer with only "shown above", "same prepared brief", or a short recap.

## GENERATION_CONFIRMED

Entry command: `scripts/confirm_generation.py --prepared-input-json <prepared> --env-file .env --ui-language zh|en`

The command must:

1. Normalize the prepared artifact.
2. Run contract validation.
3. Run H3 preflight:
   - local workflow root exists;
   - `h3_sequence_runner.py` and `h3_runner.py` exist;
   - product/reference images are local files;
   - reference count fits H3's limit;
   - ComfyUI server is reachable unless `--h3-dry-run` / `H3_DRY_RUN=1`.
4. If blocked, render `MISSING_H3_RUNTIME_GUIDANCE`.
5. If ready, call `scripts/run_rewrite_video.py --confirmed-brief`.

Do not call `run_rewrite_video.py --confirmed-brief` directly from frontstage after user confirmation.

## MISSING_H3_RUNTIME_GUIDANCE

Entry command: `scripts/render_missing_key_guidance.py --prepared-input-json <prepared> --issue <issue>`

The filename is retained for compatibility; the content is H3 runtime guidance.

Output must:

- Show confirmed brief snapshot.
- State that MiniMax H3 was not submitted, no GPU time was used, and no new clips were generated.
- Show the concrete preflight issue.
- Explain H3 production target and defaults.
- Show setup steps for `H3_WORKFLOW_ROOT`, ComfyUI 8189, SSH tunnel, `H3_COMFYUI_SERVER`, local reference images, and `h3_sequence_runner.py run --no-concat`.

## GENERATION_DONE

Entry command: `scripts/render_generation_result.py --result-json <result>`

Output order:

1. Generated clips first.
2. H3 run ID.
3. Manifest path.
4. Result JSON path.
5. Manual review checklist.

Review checklist must cover product identity, template leakage, unwanted text/UI, clip 01 hook, clip 02 proof/texture/use mechanics, and clip 03 product-visible close.
