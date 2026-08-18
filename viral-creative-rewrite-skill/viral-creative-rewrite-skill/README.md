# Viral Creative Rewrite Skill For MiniMax H3

This skill rewrites a template ad video into a MiniMax H3 / ComfyUI production package for a new product image.

Default production output:

- three independent five-second vertical clips;
- MiniMax H3 Ref2VA / R2V;
- `1088x1920` native generation, crop-ready to `1080x1920`;
- Turbo LoRA, `8` steps, `turbo_low_vram`;
- no exported audio;
- no concatenation unless requested.

## Runtime

Prepare the local skill runtime:

```powershell
python scripts/ensure_runtime.py --ui-language zh --print-python
```

Use the printed Python path for later commands.

Configure H3 locally with `.env` if needed:

```text
H3_COMFYUI_SERVER=http://127.0.0.1:8189
H3_WORKFLOW_ROOT=../..
H3_OUTPUT_ROOT=
H3_DRY_RUN=0
OUTPUT_DIR=../output
```

`H3_WORKFLOW_ROOT` should point at the outer repo containing `h3_sequence_runner.py` and `h3_runner.py`.

## Main Commands

Opening:

```powershell
python scripts/render_opening.py --ui-language zh
```

No-cost rehearsal:

```powershell
python scripts/run_rewrite_video.py --rehearsal --prepare-only --ui-language zh
```

Show detailed rehearsal analysis:

```powershell
python scripts/run_rewrite_video.py --rehearsal --prepare-only --show-detailed-analysis --ui-language zh
```

Render a prepared brief:

```powershell
python scripts/render_brief.py --prepared-input-json C:\path\to\prepared.json
```

Confirmed generation:

```powershell
python scripts/confirm_generation.py --prepared-input-json C:\path\to\prepared.json --env-file .env --ui-language zh
```

Dry-run H3 package creation:

```powershell
python scripts/confirm_generation.py --prepared-input-json C:\path\to\prepared.json --env-file .env --ui-language zh --h3-dry-run
```

## H3 Reference Images

The request can include local reference images:

```json
{
  "source_image": "C:/path/product.jpg",
  "h3_reference_images": [
    "C:/path/scene.png",
    "C:/path/character.png",
    "C:/path/product_state.png"
  ]
}
```

Remote image URLs are not accepted by the local H3 runner. Download them first.

Keep configured references at or below eight images including the product image. Clips 02 and 03 prepend the previous clip's final frame, bringing the runtime total to nine.

## Outputs

The H3 runtime writes package files outside the skill folder:

- three `clip-*_ref2va.md` prompt files;
- `sequence.json`;
- `h3_sequence_runner.log`;
- `sequence-manifest.json`;
- generated clip paths when ComfyUI generation succeeds.

Final review should inspect the independent clips before manual editing.
