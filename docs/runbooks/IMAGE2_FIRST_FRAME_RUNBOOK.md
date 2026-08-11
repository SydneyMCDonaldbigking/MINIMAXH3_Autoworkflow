# Image2 First Frame Runbook

Use this for MiniMax H3 10s/15s one-shot video opening frames.

## Setup

Copy `.env.example` to `.env.local` and fill:

```text
OPENROUTER_API_KEY=...
```

Do not commit `.env.local`.

Default working provider settings:

```text
VSR_IMAGE_PROVIDER=openrouter
VSR_IMAGE_API_MODEL=bytedance-seed/seedream-4.5
VSR_IMAGE_QUALITY=high
VSR_IMAGE_ENDPOINT=https://openrouter.ai/api/v1/images
H3_OPENROUTER_ASPECT_RATIO=9:16
H3_OPENROUTER_RESOLUTION=2K
H3_FIRST_FRAME_PROVIDER_SIZE=1024x1536
H3_FIRST_FRAME_FINAL_SIZE=1080x1920
```

2026-08-09 provider note:

- The local script and `.env.local` path are wired correctly.
- OpenRouter image model metadata confirms `openai/gpt-image-2` exists and
  supports `aspect_ratio`, `quality=high`, and `input_references`.
- The script was updated to send `aspect_ratio=9:16` to OpenRouter GPT Image 2
  instead of relying on provider `size`.
- OpenRouter still returns HTTP 403 for `openai/gpt-image-2` and
  `openai/gpt-image-1-mini`, even with a minimal no-reference prompt:
  `The request is prohibited due to a violation of provider Terms Of Service.`
- The same OpenRouter key successfully generated an image with
  `bytedance-seed/seedream-4.5`, so the key, balance, network, and Image API
  endpoint are working. The block is specific to OpenAI provider access through
  this OpenRouter account/request.
- Current decision: use Seedream through OpenRouter for cheap, fast director
  reference frames. Do not ask Seedream to generate exact logo text. Generate
  clean scene/person/action frames with no readable text, then pass the official
  `company_logo/AGO.png` separately to MiniMax H3 as the brand reference.
- For true GPT Image 2, use an OpenRouter account allowed for OpenAI image
  models, or switch to the direct OpenAI route below with an OpenAI API key from
  an organization allowed to use image generation.

## Direct OpenAI GPT Image 2 Route

Set `.env.local`:

```text
VSR_IMAGE_PROVIDER=openai
OPENAI_API_KEY=...
OPENAI_IMAGE_MODEL=gpt-image-2
OPENAI_BASE_URL=https://api.openai.com/v1
VSR_IMAGE_QUALITY=high
H3_FIRST_FRAME_PROVIDER_SIZE=1024x1536
H3_FIRST_FRAME_FINAL_SIZE=1080x1920
```

Then run:

```powershell
& "C:\Users\uryuu\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" .\image2_first_frame.py `
  --provider openai `
  --prompt-file .\prompts\first_frames\egg_tart_opening_frame.md `
  --out-dir .\outputs\image2_first_frames\egg_tart `
  --stem egg_tart_opening `
  --reference .\sample_pictures\Umall_trat\trat_pic.png `
  --reference .\company_logo\AGO.png
```

With references, the script uses direct OpenAI `/v1/images/edits`. Without
references, it uses `/v1/images/generations`.

## OpenRouter Seedream Route

This is the current working route for first-frame save/reframe generation:

```powershell
& "C:\Users\uryuu\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" .\image2_first_frame.py `
  --prompt-file .\prompts\first_frames\egg_tart_opening_frame.md `
  --out-dir .\outputs\api_probe\seedream_script_probe `
  --stem egg_tart_seedream_script_probe `
  --model bytedance-seed/seedream-4.5 `
  --resolution 2K `
  --aspect-ratio 9:16 `
  --reference .\sample_pictures\Umall_trat\trat_pic.png `
  --reference .\company_logo\AGO.png
```

Verified output:

```text
outputs/api_probe/seedream_script_probe/generated-original-size/egg_tart_seedream_script_probe-1.png  # 1440x2560
outputs/api_probe/seedream_script_probe/generated/egg_tart_seedream_script_probe-1.png                # 1080x1920
```

Current 1080p H3 reference assets:

```text
outputs/seedream_reference_assets/duck_soup_kitchen_opening_clean/generated/duck_soup_kitchen_opening_clean-1.png
outputs/seedream_reference_assets/egg_tart_family_afternoon_tea_hands_only/generated/egg_tart_family_afternoon_tea_hands_only-1.png
```

## Generate Production Reference Stack

For the 3x5s native-1080 H3 route, generate more than one first frame. The
production stack needs protagonist/hands, scene, mid-state, and final-state
references before H3:

```powershell
.\generate_reference_assets.ps1
```

This generates:

```text
duck_soup_actor_hands_scene
duck_soup_cook_character_scene
duck_soup_prep_cut_state
duck_soup_kitchen_opening_clean
duck_soup_mid_cooking_state
duck_soup_finished_hero_state
egg_tart_family_protagonist_hands
egg_tart_family_people_character_scene
egg_tart_family_table_scene_clean
egg_tart_family_afternoon_tea_hands_only
egg_tart_family_final_hero_state
egg_tart_family_people_final_hero
```

Use `-PrintOnly` to inspect the commands without calling the API.

Use the bundled Codex Python on this PC:

```powershell
C:\Users\uryuu\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe
```

## Dry Run

```powershell
& "C:\Users\uryuu\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" .\image2_first_frame.py `
  --prompt-file .\prompts\first_frames\egg_tart_opening_frame.md `
  --out-dir .\outputs\image2_first_frames\egg_tart `
  --stem egg_tart_opening `
  --reference .\sample_pictures\Umall_trat\trat_pic.png `
  --reference .\company_logo\AGO.png `
  --dry-run
```

## Generate Two Opening Frames

Egg tart:

```powershell
& "C:\Users\uryuu\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" .\image2_first_frame.py `
  --prompt-file .\prompts\first_frames\egg_tart_opening_frame.md `
  --out-dir .\outputs\image2_first_frames\egg_tart `
  --stem egg_tart_opening `
  --reference .\sample_pictures\Umall_trat\trat_pic.png `
  --reference .\company_logo\AGO.png
```

Baozi:

```powershell
& "C:\Users\uryuu\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" .\image2_first_frame.py `
  --prompt-file .\prompts\first_frames\baozi_opening_frame.md `
  --out-dir .\outputs\image2_first_frames\baozi `
  --stem baozi_opening `
  --reference "C:\Users\uryuu\AppData\Local\Temp\codex-clipboard-57afe3f2-a6f7-4399-8acc-5d563c90ca35.png" `
  --reference .\company_logo\AGO.png
```

Outputs:

```text
outputs/image2_first_frames/<job>/generated-original-size/*.png
outputs/image2_first_frames/<job>/generated/*.png
outputs/image2_first_frames/<job>/metadata/*.json
```

The `generated/` PNG is reframed to `1080x1920` when Pillow is available. The
original provider image remains in `generated-original-size/`.

## MiniMax H3 Usage

For a one-shot 10s/15s MiniMax H3 ad, pass the generated opening frame first in
the R2V reference list, then product/logo/scene references:

```powershell
python h3_runner.py r2v `
  --prompt "<10s or 15s storyboard prompt>" `
  --ref-image .\outputs\image2_first_frames\egg_tart\generated\egg_tart_opening-1.png `
  --ref-image .\sample_pictures\Umall_trat\trat_pic.png `
  --ref-image .\company_logo\AGO.png `
  --duration 15 --steps 4 --turbo
```
