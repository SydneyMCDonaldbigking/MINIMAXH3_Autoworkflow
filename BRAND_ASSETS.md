# Brand and Local Asset Memory

Scanned on 2026-08-09 from:

- MiniMax workflow repo: `C:\Users\uryuu\Desktop\comfyui_workflow`
- Viral Social Remix skill: `C:\Users\uryuu\Desktop\sns_skill\viral-social-remix`

This file is the local brand memory for MiniMax H3 jobs. Use it before writing
Image2 opening-frame prompts, MiniMax H3 R2V prompts, or `jobs.yaml`.

## Default Brand Rule

Default target for company ads is English-region unless the user explicitly
asks for Chinese-region output.

For English-region output, use:

- Visible brand: `ASIAN GROCER ONLINE`
- Lockup text: `ASIAN GROCER ONLINE`, with `POWERED BY UMALL`
- Local logo file: `company_logo/AGO.png`
- Canonical skill logo file:
  `C:\Users\uryuu\Desktop\sns_skill\viral-social-remix\umall_logo\asian-grocer-online-powered-by-umall.png`

For Chinese-region or explicit UMALL mother-brand output, use:

- Visible brand: `UMALL`
- Local logo file: `company_logo/UMALL.png`
- Canonical skill logo file:
  `C:\Users\uryuu\Desktop\sns_skill\viral-social-remix\umall_logo\umall_logo.png`

Do not use `UMALL.png` as the default English-region logo. Use `AGO.png`.

## Local Logo Assets

| Asset | Size | Meaning | Default Use |
| --- | ---: | --- | --- |
| `company_logo/AGO.png` | 586x105 | English lockup: `ASIAN GROCER ONLINE` + `POWERED BY UMALL` | Default logo for English ads, Image2 opening frames, product commercials |
| `company_logo/UMALL.png` | 258x106 | UMALL mother-brand logo | Use only when the user asks for UMALL/Chinese-region/mother-brand output |

Visual inspection:

- `AGO.png` is a horizontal English-region lockup. It reads `ASIAN GROCER
  ONLINE` on the left and `POWERED BY UMALL` on the right.
- `UMALL.png` is the standalone red/orange UMALL wordmark.

## Sample Product Assets Found

These are local sample/product references, not default logos.

| Asset | Size | Observed Content | Suggested Job Role |
| --- | ---: | --- | --- |
| `sample_pictures/AGO_ducksoup/duck.png` | 951x922 | raw duck breast/duck piece on a wooden tray with herbs/spices | product or ingredient reference for AGO duck/duck soup cooking ad |
| `sample_pictures/Umall_trat/trat_pic.png` | 1057x1065 | close-up egg tarts/custard tarts with flaky pastry and glossy filling | product/texture reference for egg tart bakery ad |

## Image2 Opening Frame Usage

For MiniMax H3 one-shot 10s/15s video generation, the Image2 opening frame is
the identity gate.

Recommended reference order for Image2:

1. product image;
2. `company_logo/AGO.png` for English-region output, or `company_logo/UMALL.png`
   only for explicit UMALL/Chinese-region output;
3. model/person/hands reference, if provided;
4. scene/kitchen/store/background reference, if provided.

The Image2 opening frame must already have:

- correct product family and package/product shape;
- correct brand region and logo;
- correct scene style and lighting;
- usable opening composition for the 10s/15s story.

If the logo, product, model, or scene is wrong, regenerate the Image2 opening
frame before running MiniMax H3. Do not paste, composite, mask, track, or
overlay the logo locally to fix a bad frame.

## MiniMax H3 R2V Reference Order

For `h3_runner.py r2v`, pass references in this order:

1. Image2-generated opening frame;
2. model/person/hands reference, if any;
3. product image;
4. company logo or product+logo image;
5. scene/kitchen/store/background reference;
6. optional cooked/served result or texture close-up.

Example:

```powershell
python h3_runner.py r2v `
  --server http://127.0.0.1:8189 `
  --prompt "<10s or 15s storyboard prompt>" `
  --ref-image C:\path\image2-opening-frame.png `
  --ref-image C:\Users\uryuu\Desktop\comfyui_workflow\sample_pictures\AGO_ducksoup\duck.png `
  --ref-image C:\Users\uryuu\Desktop\comfyui_workflow\company_logo\AGO.png `
  --width 1344 --height 768 `
  --duration 15 `
  --steps 4 `
  --turbo `
  --output-dir server_outputs\minimax15
```

## Prompt Rule

When the user says "company logo" without more detail, use `AGO.png` and write
the brand as `ASIAN GROCER ONLINE / POWERED BY UMALL` for English-region ads.

Do not invent prices, fake UI, fake store claims, fake app screenshots, or fake
availability. Logo text may appear only as a real printed package/sign/prop in
the Image2 opening frame or as part of real supplied product packaging.

The user reviews final videos. The agent should generate, save locally, and
handoff the MP4 path without doing second-pass editing unless asked.
