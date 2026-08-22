# Claude Handoff

Project: Freezer Shrimp Wonton Egg Drop Soup

Purpose: prepared material package for Australia / Instagram Reels H3 Ref2VA generation.

Revision: v3 material refresh. The frozen wonton action clearly starts from an open refrigerator/freezer. Early references show closed wrapped frozen wontons only; filling is allowed only after the wontons are cooking or in the final spoon-lift hero. Decorative green houseplants were removed from the Image2 reference stack. Food greens remain only as scallion garnish/ingredient.

## Start Here

- Full preview image:
  `C:\Users\uryuu\Desktop\comfyui_workflow\sequence_outputs\freezer_shrimp_wonton_egg_drop_soup\preproduction\preview\freezer_shrimp_wonton_full_material_preview.jpg`
- Preproduction package:
  `C:\Users\uryuu\Desktop\comfyui_workflow\sequence_outputs\freezer_shrimp_wonton_egg_drop_soup\preproduction`
- Curated Image2 reference images:
  `C:\Users\uryuu\Desktop\comfyui_workflow\outputs\reference_assets\19_freezer_shrimp_wonton_egg_drop_soup`
- H3 sequence JSON:
  `C:\Users\uryuu\Desktop\comfyui_workflow\sequences\freezer_shrimp_wonton_egg_drop_soup_3x5_1080.json`

## Important Files

- Recipe source notes:
  `sequence_outputs\freezer_shrimp_wonton_egg_drop_soup\preproduction\recipe_sources.md`
- Recipe bible:
  `sequence_outputs\freezer_shrimp_wonton_egg_drop_soup\preproduction\recipe_bible.md`
- H3 Ref2VA prompts:
  `sequence_outputs\freezer_shrimp_wonton_egg_drop_soup\preproduction\h3_prompts`
- Image2 prompts:
  `sequence_outputs\freezer_shrimp_wonton_egg_drop_soup\preproduction\reference_prompts`
- Image2 result notes:
  `sequence_outputs\freezer_shrimp_wonton_egg_drop_soup\preproduction\image2_generation_result.md`
- Social captions and cue files:
  `sequence_outputs\freezer_shrimp_wonton_egg_drop_soup\preproduction\social`

## Technical Status

- Image2 references were regenerated successfully with `openai/gpt-image-2`, `quality=high`.
- All curated reference images are `1080x1920`.
- H3 sequence prompt validation passed:
  `prompts\validate_prompt.py sequences\freezer_shrimp_wonton_egg_drop_soup_3x5_1080.json`
- Full repo check passed after adding this package:
  `check_repo.py`

## Notes

- The main dish is Freezer Shrimp Wonton Egg Drop Soup.
- Clip 01 should begin with the frozen shrimp wonton pack being taken directly from the refrigerator/freezer, then moved to the pot setup.
- Clip 01 must not use exposed filling as a visual reference; the sequence now relies on closed-pack and closed-prep Image2 references for early wonton identity.
- The user-provided wrapped/filling image is kept only as a product note/final filling cue, not as an early H3 clip reference.
- Chicken thigh was saved as a separate user-provided material reference, but it is not part of this soup sequence.
- Packaging should remain generic/unbranded with no readable text, barcode, price, or claims.
- AGO/UMALL may appear only as a small physical prop if needed; no floating logos or overlays.
