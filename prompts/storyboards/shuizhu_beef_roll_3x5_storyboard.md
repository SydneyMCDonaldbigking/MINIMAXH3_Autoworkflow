# 水煮肥牛卷 3x5s Native 1080 Storyboard

Product asset:

- `sample_pictures/AGO_水煮牛肉卷(辣的）/肥牛卷.png`
- Brand/logo: `company_logo/AGO.png`
- Visible brand rule: ASIAN GROCER ONLINE / POWERED BY UMALL may appear only as real packaging, a small counter card, or a printed bag. Do not ask H3 to generate subtitles or floating logos.

Production route:

- Generate reference images first with Image2/Seedream high quality.
- Run MiniMax H3 Turbo LoRA as three independent 5s R2V clips.
- Native render size: `1088x1920`, 4 steps, crop final review copies to exact `1080x1920` with `crop=1080:1920:4:0`.
- Each 5s clip uses exactly three stable shots: `0.0-1.6`, `1.6-3.4`, `3.4-5.0`.

## Reference Images To Generate

1. `shuizhu_beef_roll_chef_character_scene`
   Chinese-style renovated kitchen, professional chef, raw beef rolls, napa cabbage, small AGO tabletop card.
2. `shuizhu_beef_roll_cabbage_prep_state`
   Chef hands cutting napa cabbage, raw beef rolls arranged nearby.
3. `shuizhu_beef_roll_spicy_broth_state`
   Red chili broth boiling in wok or deep pot, cabbage entering, beef rolls ready.
4. `shuizhu_beef_roll_finished_hero_state_v2`
   Finished spicy beef rolls and napa cabbage in red broth, chef/table hero, AGO physical brand cue.

## 15s Story

Clip 01: chef and ingredients.

- Shot 1: Chinese-style kitchen establishes premium chef context, raw beef rolls and napa cabbage visible.
- Shot 2: close-up of chef cutting napa cabbage into broad pieces; beef rolls sit clearly on a wooden tray.
- Shot 3: chef turns on the stove and brings a red spicy broth to active heat.

Clip 02: ingredients hit the spicy pot.

- Shot 1: cabbage goes into boiling red chili broth.
- Shot 2: beef rolls are laid into the broth and begin to unfurl.
- Shot 3: red broth bubbles around cabbage and beef; steam and chili oil sell heat.

Clip 03: serve and hero.

- Shot 1: chef lifts cooked beef rolls and cabbage into a deep bowl.
- Shot 2: red broth pours over the bowl; garnish lands cleanly.
- Shot 3: finished spicy beef bowl hero shot with chef in background and a small real AGO brand cue.

Simple subtitle options:

- "Real beef rolls"
- "Napa cabbage, spicy broth"
- "Boil, serve, enjoy"
- "Hot, tender, ready"
