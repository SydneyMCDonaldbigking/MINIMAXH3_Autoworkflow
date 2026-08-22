# Image2 Generation Plan

Use the bundled Codex Python:

```powershell
$py = "C:\Users\uryuu\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
```

Primary route requested: GPT Image 2 / Image2 API, high quality. This repo currently has an OpenRouter image key in `.env.local`; direct `OPENAI_API_KEY` is not present. If OpenRouter blocks `openai/gpt-image-2`, use the working high-quality image route already documented in this repo: `bytedance-seed/seedream-4.5`, `resolution=2K`, `aspect_ratio=9:16`, reframed to `1080x1920`.

Output root:

```text
outputs/reference_assets/_generated/freezer_shrimp_wonton_egg_drop_soup_<kind>/
```

## Commands

```powershell
& $py .\image2_first_frame.py --prompt-file .\sequence_outputs\freezer_shrimp_wonton_egg_drop_soup\preproduction\reference_prompts\egg_reference.md --out-dir .\outputs\reference_assets\_generated\freezer_shrimp_wonton_egg_drop_soup_egg_reference --stem freezer_shrimp_wonton_egg_reference --model openai/gpt-image-2 --quality high --aspect-ratio 9:16 --final-size 1080x1920

& $py .\image2_first_frame.py --prompt-file .\sequence_outputs\freezer_shrimp_wonton_egg_drop_soup\preproduction\reference_prompts\wonton_frozen_package.md --out-dir .\outputs\reference_assets\_generated\freezer_shrimp_wonton_egg_drop_soup_wonton_frozen_package --stem freezer_shrimp_wonton_frozen_package --model openai/gpt-image-2 --quality high --aspect-ratio 9:16 --final-size 1080x1920 --reference .\sequence_outputs\freezer_shrimp_wonton_egg_drop_soup\preproduction\product_references\wonton_cooked_reference.png

& $py .\image2_first_frame.py --prompt-file .\sequence_outputs\freezer_shrimp_wonton_egg_drop_soup\preproduction\reference_prompts\soup_seasoning_kit.md --out-dir .\outputs\reference_assets\_generated\freezer_shrimp_wonton_egg_drop_soup_soup_seasoning_kit --stem freezer_shrimp_wonton_soup_seasoning_kit --model openai/gpt-image-2 --quality high --aspect-ratio 9:16 --final-size 1080x1920

& $py .\image2_first_frame.py --prompt-file .\sequence_outputs\freezer_shrimp_wonton_egg_drop_soup\preproduction\reference_prompts\character_scene.md --out-dir .\outputs\reference_assets\_generated\freezer_shrimp_wonton_egg_drop_soup_character_scene --stem freezer_shrimp_wonton_character_scene --model openai/gpt-image-2 --quality high --aspect-ratio 9:16 --final-size 1080x1920 --reference .\outputs\reference_assets\_generated\freezer_shrimp_wonton_egg_drop_soup_wonton_frozen_package\generated\freezer_shrimp_wonton_frozen_package-1.png --reference .\outputs\reference_assets\_generated\freezer_shrimp_wonton_egg_drop_soup_egg_reference\generated\freezer_shrimp_wonton_egg_reference-1.png

& $py .\image2_first_frame.py --prompt-file .\sequence_outputs\freezer_shrimp_wonton_egg_drop_soup\preproduction\reference_prompts\prep_state.md --out-dir .\outputs\reference_assets\_generated\freezer_shrimp_wonton_egg_drop_soup_prep_state --stem freezer_shrimp_wonton_prep_state --model openai/gpt-image-2 --quality high --aspect-ratio 9:16 --final-size 1080x1920 --reference .\outputs\reference_assets\_generated\freezer_shrimp_wonton_egg_drop_soup_wonton_frozen_package\generated\freezer_shrimp_wonton_frozen_package-1.png --reference .\outputs\reference_assets\_generated\freezer_shrimp_wonton_egg_drop_soup_egg_reference\generated\freezer_shrimp_wonton_egg_reference-1.png --reference .\outputs\reference_assets\_generated\freezer_shrimp_wonton_egg_drop_soup_soup_seasoning_kit\generated\freezer_shrimp_wonton_soup_seasoning_kit-1.png

& $py .\image2_first_frame.py --prompt-file .\sequence_outputs\freezer_shrimp_wonton_egg_drop_soup\preproduction\reference_prompts\cook_state.md --out-dir .\outputs\reference_assets\_generated\freezer_shrimp_wonton_egg_drop_soup_cook_state --stem freezer_shrimp_wonton_cook_state --model openai/gpt-image-2 --quality high --aspect-ratio 9:16 --final-size 1080x1920 --reference .\sequence_outputs\freezer_shrimp_wonton_egg_drop_soup\preproduction\product_references\wonton_cooked_reference.png --reference .\outputs\reference_assets\_generated\freezer_shrimp_wonton_egg_drop_soup_prep_state\generated\freezer_shrimp_wonton_prep_state-1.png

& $py .\image2_first_frame.py --prompt-file .\sequence_outputs\freezer_shrimp_wonton_egg_drop_soup\preproduction\reference_prompts\hero_state.md --out-dir .\outputs\reference_assets\_generated\freezer_shrimp_wonton_egg_drop_soup_hero_state --stem freezer_shrimp_wonton_hero_state --model openai/gpt-image-2 --quality high --aspect-ratio 9:16 --final-size 1080x1920 --reference .\sequence_outputs\freezer_shrimp_wonton_egg_drop_soup\preproduction\product_references\wonton_cooked_reference.png --reference .\outputs\reference_assets\_generated\freezer_shrimp_wonton_egg_drop_soup_cook_state\generated\freezer_shrimp_wonton_cook_state-1.png
```

