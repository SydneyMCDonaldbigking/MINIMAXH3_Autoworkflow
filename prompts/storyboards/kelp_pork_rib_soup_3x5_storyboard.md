# 海带排骨汤 3x5s Native 1080 Storyboard

Product asset:

- `sample_pictures/Umall海带排骨汤/排骨.png`
- Brand/logo: `company_logo/UMALL.png`
- Visible brand rule: UMALL may appear only as a real product package, small kitchen card, or table prop. If this becomes an English-region ad, swap to `company_logo/AGO.png`.

Production route:

- Generate reference images first with Image2/Seedream high quality.
- Run MiniMax H3 Turbo LoRA as three independent 5s R2V clips.
- Native render size: `1088x1920`, 8 steps, crop final review copies to exact `1080x1920` with `crop=1080:1920:4:0`.
- Each 5s clip uses exactly three stable shots: `0.0-1.6`, `1.6-3.4`, `3.4-5.0`.

## Reference Images To Generate

1. `kelp_pork_rib_soup_mom_family_scene`
   Warm home kitchen/dining room, mother as protagonist, elderly parent at table, clay pot visible.
2. `kelp_pork_rib_soup_prep_state`
   Mother's hands preparing pork ribs, soaked kelp squares, ginger slices, scallion, clay pot nearby.
3. `kelp_pork_rib_soup_simmer_state`
   Clay pot over flame, clear soup simmering with pork ribs and kelp visible.
4. `kelp_pork_rib_soup_family_hero_state`
   Mother serves soup to elderly parent at the family table, warm finished soup hero.

## 15s Story

Clip 01: clean prep and pot setup.

- Shot 1: mother sets pork ribs, soaked kelp, ginger, and scallion on the counter; elderly parent is softly visible in the dining area.
- Shot 2: close-up of hands cutting soaked kelp into squares and arranging blanched ribs.
- Shot 3: ribs, kelp, ginger, and water go into a clay pot on the stove.

Clip 02: teach the simmer.

- Shot 1: clay pot sits over a low blue flame with lid on; steam begins.
- Shot 2: mother opens the lid and gently skims or stirs; soup remains clear.
- Shot 3: ribs and kelp visibly turn tender in a gentle simmer.

Clip 03: family serving.

- Shot 1: mother ladles hot kelp pork rib soup into small bowls.
- Shot 2: she brings the soup to the dining table where the elderly parent waits warmly.
- Shot 3: elderly parent tastes the soup; mother sits nearby, clay pot and bowls make the final hero.

Simple subtitle options:

- "Ribs, kelp, ginger"
- "Slow simmer"
- "Clear broth, tender ribs"
- "A warm bowl for family"
