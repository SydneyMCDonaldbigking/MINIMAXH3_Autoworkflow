#!/usr/bin/env python3
"""Create revision-2 preproduction packages for four distinct product commercials."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEQUENCES = ROOT / "sequences"

PRODUCTS = [
    {
        "slug": "assorted_mini_mooncakes", "title": "Assorted Mini Mooncakes", "cn": "缤纷迷你月饼", "asset_dir": "31_assorted_mini_mooncakes", "source": "product_references/assorted_mini_mooncakes_source.png",
        "talent": "Four fictional Asian adult friends: a butter-yellow linen-shirt woman, navy-overshirt man, coral-cardigan woman and cream-knit-polo man. They are dessert guests, not chefs.",
        "scene": "a late-afternoon outdoor garden terrace with a striped canvas umbrella, pale timber dessert table, ceramic tea ware and leafy garden bokeh",
        "food": "the supplied small pressed pastel mini mooncakes in yellow, ivory, pink, cocoa brown, charcoal grey and green, with dense red, orange or dark fillings only where cleanly cut",
        "pack_rule": "No retail package is supplied. Do not invent a carton, pouch or wrapper.",
        "states": {
            "character_scene": "Wide vertical outdoor lifestyle opening. All four friends are naturally gathered around the garden dessert table. A white platter of the supplied assorted mini mooncakes is centred with tea, grapes and strawberries. The exact AGO artwork from Image 2 is a small physical tent card resting at the far-right table edge, readable but secondary.",
            "prep_state": "Top three-quarter outdoor dessert-table layout: whole supplied mooncakes on a white platter with tea cups, grapes, strawberries and the small physical AGO table card at the far edge. No hands.",
            "cook_state": "Medium close lifestyle action. The butter-yellow-shirt friend halves one supplied yellow mini mooncake with a small dessert knife; the dense orange filling is visible and the other friends are softly out of focus. The AGO tabletop card remains a small prop in the far background.",
            "hero_state": "Final outdoor friends-and-dessert hero. The four friends share tea and reach for the supplied colourful mini mooncakes; whole and cleanly halved pieces are visible on the platter. Warm golden sun and no invented package.",
        },
        "titles": ["Garden-table welcome", "Shared filling reveal", "Four-friend tea-time finish"],
        "shots": [
            ["0.0–1.6s — Wide 35mm eye-level terrace shot. Begin on the settled garden dessert table as all four friends take their places; the butter-yellow-shirt woman slides the platter ten centimetres toward centre. Locked camera, tiny 4 cm push-in; end with each pastel pastry readable.", "1.6–3.4s — Cut to a 70mm table-height close insert. A coral-cardigan hand selects one intact yellow mooncake with a dessert fork while the navy-overshirt friend pours amber tea behind it. One clean action, shallow focus on the pressed pastry; end with the mooncake lifted above the plate.", "3.4–5.0s — Cut to a medium two-person reaction with the table foreground sharp. The yellow-shirt friend sets the selected mooncake beside a tea cup and the guests lean in naturally. End on the composed platter for the next beat."],
            ["0.0–1.6s — Medium 50mm table-side shot from the settled platter. The butter-yellow-shirt friend steadies one yellow mooncake and makes one controlled downward cut with a small dessert knife. Keep the other pastries undisturbed; end when the two halves separate.", "1.6–3.4s — Cut to an 85mm macro insert. Dense orange filling and thin patterned skin stay sharp as a tea cup is set down softly nearby. Locked-off camera; no new food enters; end on the glossy cut surface.", "3.4–5.0s — Cut to an over-table medium shot. The coral-cardigan friend accepts one half on a small plate and lifts it once toward the group, while the other guests remain in the terrace setting. End on the shared dessert-table arrangement."],
            ["0.0–1.6s — Wide 40mm terrace shot. Begin with all four friends continuing the same tea gathering around the open platter. The navy-overshirt friend pours one short stream of tea into a cup, then stops.", "1.6–3.4s — Cut to a 75mm close hero. A cream-knit-polo hand lifts one intact supplied mooncake above the platter while cut halves, tea and fruit remain softly visible. Tiny rack focus from cup to pastry; end with its pattern crisp.", "3.4–5.0s — Cut back to a medium group hero. The mooncake returns to the platter and the four friends bring their cups together once without blocking the food. Locked-off warm outdoor finish."],
        ],
        "food_logic": "These are ready-to-serve mini mooncakes. The story proves pressed pastry, colourful assortment and dense filling; it does not invent baking.",
    },
    {
        "slug": "sautao_knife_cut_noodles", "title": "Sau Tao Taiwanese Knife-Cut Noodles", "cn": "寿桃台湾刀削面", "asset_dir": "32_sautao_knife_cut_noodles", "source": "product_references/sautao_knife_cut_noodles_source.png",
        "talent": "A fictional Chinese male cook in his early thirties with short black hair, indigo cotton shirt and charcoal apron. He works with calm precise hands in one northern Chinese kitchen.",
        "scene": "a traditional northern Chinese home kitchen with charcoal-grey stone wall tiles, red-painted timber window frame, seasoned wood counter, black enamel stockpot over a blue gas flame and white serving bowl",
        "food": "the supplied Sau Tao wide, flat, wavy knife-cut wheat noodles, cooked as broad chewy ribbons rather than ramen, spaghetti or thin noodles",
        "pack_rule": "The exact supplied Sau Tao package from Image 1 is upright and front-facing on the counter in opening and ingredient references; preserve the real package design.",
        "states": {
            "character_scene": "Vertical opening in the northern Chinese kitchen. The indigo-shirt cook stands at the wood counter with the exact source noodle package upright beside a small physical AGO table card. A board holds flour, bok choy, spring onion, braised egg and minced-pork sauce; the black enamel stockpot waits over the blue flame.",
            "prep_state": "Top three-quarter ingredient layout: exact source package upright, dry wide wavy noodles, flour, bok choy, spring onion, braised egg, minced-pork sauce and a small physical AGO sign. Ingredients are separated; no hands.",
            "cook_state": "Close gas-hob reference. The indigo-shirt cook lifts cooked wide wavy noodles from the black enamel pot with long chopsticks; steam rises, blue flame remains visible and noodles stay broad flat ribbons. Source package is out of focus on rear counter.",
            "hero_state": "Final bowl on the wood counter: glossy wide wavy noodles with minced-pork sauce, bok choy, braised egg and spring onion. Chopsticks lift a small bundle; exact source package stays as a secondary upright rear-counter prop.",
        },
        "titles": ["Package and ingredient setup", "Boil and noodle lift", "Sauced-bowl finish"],
        "shots": [
            ["0.0–1.6s — Medium 45mm counter shot. Start on the indigo-shirt cook beside the exact source noodle pack, small tabletop card and ingredient board. He opens the top seal once and pulls out one compact bundle of broad dry noodles. Camera locked-off; end with the bundle over the board.", "1.6–3.4s — Cut to a 65mm overhead insert. The cook spreads the wide wavy noodles beside bok choy, scallion, braised egg and minced-pork sauce, then picks the bundle up once with chopsticks. The original pack stays rear-frame; end on dry ribbons ready to cook.", "3.4–5.0s — Cut to medium hob height. He lowers the compact bundle into clearly boiling water in the black enamel pot over the blue flame. One controlled lowering action; end at water entry under a small plume of steam."],
            ["0.0–1.6s — Close 55mm hob shot beginning at water entry. Broad ribbons loosen naturally in a rolling boil while the cook makes one gentle chopstick separation. Stable horizon; end with distinct wide ribbons moving in water.", "1.6–3.4s — Cut to an 80mm pot-height insert. The cook lifts one cooked portion above the pot; water drains back in thin streams while flat wavy edges remain visible. Tiny 3 cm push-in only; end with glossy bundle suspended.", "3.4–5.0s — Cut to medium counter transfer. He guides the lifted noodles into the waiting white bowl next to sauce and vegetables, stopping after one transfer. End on noodles settled in the bowl."],
            ["0.0–1.6s — Medium 50mm bowl shot. Begin on cooked noodles in the white bowl; the cook adds one spoonful of minced-pork sauce to centre without repetitive stirring. Bok choy and egg remain at the edge; end with sauce visible.", "1.6–3.4s — Cut to a 75mm close insert. Long chopsticks mix once and lift a small sauced bundle; glossy wide noodles remain recognisable and steam rises behind them. Locked camera, finish on texture.", "3.4–5.0s — Cut to a calm 60mm bowl hero. Lifted noodles return and the cook sets chopsticks across the rim in one final movement. Exact source pack remains secondary on rear counter; end on complete bowl."],
        ],
        "food_logic": "Show dry broad ribbons becoming cooked chewy wide noodles, then sauce them. Maintain knife-cut noodle identity throughout.",
    },
    {
        "slug": "chaopai_beef_bone_broth", "title": "Chaopai Premium Beef Bone Broth Hot Pot Base", "cn": "潮汕风味牛骨清汤火锅底料", "asset_dir": "33_chaopai_beef_bone_broth", "source": "product_references/chaopai_beef_bone_broth_source.png",
        "talent": "A fictional Chinese woman in her fifties with tied-back dark hair, deep forest-green linen blouse and beige apron. She is the only cook in a teal-tiled Chinese family kitchen.",
        "scene": "a Chinese family kitchen with deep teal ceramic wall tiles, dark wood counter, brass pot handles and a large black clay sandpot over a blue gas flame",
        "food": "clear golden Chaoshan-style beef-bone broth with beef bones and tender beef, white daikon rounds, tofu cubes, red jujubes and scallion, always clear rather than red or oily",
        "pack_rule": "The exact supplied beef-bone broth package from Image 1 is upright and front-facing beside the clay sandpot in opening and ingredient references; preserve its real design.",
        "states": {
            "character_scene": "Vertical opening in teal-tiled kitchen. The forest-green-blouse cook stands beside a large black clay sandpot over a visible blue flame. Exact source broth package is upright on wood counter beside a small physical AGO sign card. Daikon, tofu, jujubes, scallion and beef bones are neatly arranged.",
            "prep_state": "Top three-quarter counter layout: exact source package upright beside small AGO sign, black clay sandpot with clear water, beef bones, daikon rounds, tofu cubes, red jujubes and scallion. Cleanly separated; no hands.",
            "cook_state": "Close sandpot reference. The cook lifts black clay-sandpot lid to reveal clear golden broth gently simmering around beef bone, daikon, tofu, red jujubes and scallion. Steam is soft; broth is never red, cloudy or oily.",
            "hero_state": "Final clay-sandpot dinner hero on dark wood counter. Clear golden broth, beef bone, daikon, tofu, jujubes and scallion are visible; a ladle lifts clear broth once. Source package stays secondary at rear, never replaced.",
        },
        "titles": ["Broth-base and claypot setup", "Clear simmer proof", "Sandpot serving finish"],
        "shots": [
            ["0.0–1.6s — Medium 45mm counter shot. Begin on forest-green-blouse cook, exact source broth pack, tabletop card and empty black clay sandpot over blue flame. She places the pack upright once beside pot and reaches for one inner sachet. End with sachet held above counter.", "1.6–3.4s — Cut to 70mm ingredient-board insert. She tears open sachet in one deliberate pull while daikon, tofu, jujubes, scallion and beef bones remain arranged. Actual source pack stays rear-frame; end with opened sachet aimed toward pot.", "3.4–5.0s — Cut to medium claypot angle. She pours sachet contents into hot water in black sandpot and stops; liquid begins turning golden around blue flame. End on first clear golden swirl."],
            ["0.0–1.6s — Close 55mm sandpot shot. Begin on clear golden liquid as cook adds daikon and tofu in one calm motion, keeping broth transparent. Claypot remains centred; end when pieces settle.", "1.6–3.4s — Cut to 80mm surface insert. Beef bone, tender beef, red jujubes and scallion gently move in clear broth while lid opens just enough for controlled steam reveal. Locked-off camera; end with clean readable surface.", "3.4–5.0s — Cut to medium ladle action. Cook lifts one ladle of clear golden broth above claypot, holds once, then returns it toward pot. End on falling clear ripples."],
            ["0.0–1.6s — Medium 50mm claypot hero continuing from ripples. Cook places fresh scallion at pot edge in one finishing action; beef bone, daikon, tofu and jujubes remain visible.", "1.6–3.4s — Cut to 75mm close insert. Ladle lifts clear broth and one tender beef piece, holding above pot so texture and golden liquid remain sharp. Tiny 3 cm push-in; end with ladle level.", "3.4–5.0s — Cut to stable three-quarter final sandpot shot. Ladle returns and cook rests her hand beside pot, leaving exact source pack secondary on rear counter. End on clear steam and complete claypot."],
        ],
        "food_logic": "The story is package to claypot to clear simmer to serving. Keep broth transparent golden and sandpot physically central.",
    },
    {
        "slug": "xiaolongbao", "title": "Soup Dumplings (Xiaolongbao)", "cn": "灌汤小笼包", "asset_dir": "34_xiaolongbao", "source": "product_references/xiaolongbao_source.png",
        "talent": "A fictional Cantonese father in his early forties with short hair, warm mustard knit sweater and navy apron. He is a breakfast host in one bright Chinese kitchen; no person from the other campaigns appears.",
        "scene": "a bright Cantonese-style Chinese breakfast kitchen with light timber cabinets, warm cream wall tiles, bamboo steamer over a small steel pot, pale wood breakfast table and freshly poured soy milk",
        "food": "the supplied plump pale soup dumplings with neat pleated tops and thin translucent skins, served in bamboo steamer with ginger and black vinegar",
        "pack_rule": "No retail package is supplied. Do not invent a carton, pouch or wrapper.",
        "states": {
            "character_scene": "Vertical breakfast opening. Mustard-sweater father sets a bamboo steamer of supplied pleated soup dumplings on pale wood breakfast table beside two cups of fresh soy milk, black vinegar and ginger. Exact AGO artwork from Image 2 is a small physical tabletop card at far side. No invented package.",
            "prep_state": "Top three-quarter breakfast layout. Exactly six supplied pleated soup dumplings sit in bamboo steamer on parchment, with two soy-milk cups, ginger, black vinegar and a small physical AGO table card. Morning window light, no hands.",
            "cook_state": "Close steaming reference. Mustard-sweater father lifts bamboo lid to reveal exactly six glossy intact soup dumplings above boiling water. Controlled steam, wrappers not torn, soy milk waits on breakfast table behind.",
            "hero_state": "Final breakfast hero. Exactly six supplied pleated soup dumplings remain in steamer while one additional identical dumpling rests on white porcelain spoon with a small natural soup opening; two soy-milk cups, ginger and black vinegar complete table. No invented package.",
        },
        "titles": ["Breakfast-table steamer setup", "Steam reveal", "Soup dumpling and soy-milk finish"],
        "shots": [
            ["0.0–1.6s — Medium 40mm breakfast-table shot. Begin on mustard-sweater father setting bamboo steamer of exactly six supplied dumplings beside two soy-milk cups, ginger and black vinegar. Small tabletop card rests far edge. End after one careful placement.", "1.6–3.4s — Cut to 70mm top three-quarter insert. His hands straighten parchment beneath the six dumplings once, keeping pleated tops intact. Soy milk remains at side; end with steamer ready to cover.", "3.4–5.0s — Cut to medium pot height. He lowers bamboo lid over steamer above actively steaming water in one smooth motion. Locked-off; end on lid closing through controlled steam."],
            ["0.0–1.6s — Close 55mm steamer shot. Begin on closed bamboo lid as gentle condensation gathers. Father lifts lid once, ending as six dumplings become visible through clean steam.", "1.6–3.4s — Cut to 85mm macro inside open steamer. Exactly six glossy pleated dumplings sit intact on parchment; steam rises without hiding shape. Hold focus on one pleated top, then end on full six-dumpling arrangement.", "3.4–5.0s — Cut to medium breakfast-table angle. Open steamer moves from pot to table beside soy milk in one controlled placement. End with basket settled for serving beat."],
            ["0.0–1.6s — Medium 50mm table shot. Begin on open steamer with exactly six dumplings. Father slides white porcelain spoon beside it and sets a small dish of black vinegar and ginger in one deliberate movement.", "1.6–3.4s — Cut to 75mm close serving insert. Chopsticks lift one intact dumpling and set it gently onto spoon; wrapper has tiny natural opening with visible clear soup but does not collapse. End with spoon stable.", "3.4–5.0s — Cut to calm three-quarter breakfast hero. Spoon rests foreground, six dumplings remain in steamer behind, and two soy-milk cups frame table. Father withdraws hands; hold still on finished breakfast."],
        ],
        "food_logic": "The story is breakfast setup to steam to careful spoon serving. Retain six dumplings in basket and one on spoon only in final state.",
    },
]

def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")

def reference_prompt(p: dict, kind: str) -> str:
    return f"""Use case: ads-marketing
Asset type: revision-2 MiniMax H3 R2V reference image for a vertical grocery commercial
Primary request: create the {kind.replace('_', ' ')} reference image for {p['title']}.
Input images: Image 1 is the exact advertised product identity and any supplied retail package; Image 2 is the approved ASIAN GROCER ONLINE / powered by UMALL tabletop sign artwork. Preserve both supplied references faithfully.
Scene/backdrop: {p['scene']}.
Subject: {p['states'][kind]}
Talent and casting: {p['talent']}
Product integrity: {p['food']}.
Packaging instruction: {p['pack_rule']}
Physical sign instruction: when called for, Image 2 is a real small tabletop tent card or flat display card resting on the table or counter. Keep its original lettering, green-and-orange colours and proportions intact; it is physical, never a floating overlay.
Style/medium: high-end photorealistic retail food commercial still; real human anatomy, believable cookware and natural food texture.
Composition/framing: vertical 9:16; use the shot composition stated in the subject description and one coherent location for this product only.
Lighting/mood: natural purposeful light appropriate to the scene, clean highlights and realistic shadow direction.
Constraints: distinct cast and location from other products; supplied product family only; preserve supplied package; no invented package if absent; no extra fingers, warped utensils, unreadable faux text, captions, price graphics or watermarks.
Avoid: changing product to a different noodle, pastry, dumpling, soup or package; generic western kitchen; melted food; clutter; fake app interface.
"""

def h3_prompt(p: dict, clip_no: int) -> str:
    refs = {1: ["the opening scene key visual", "the exact supplied advertised product", "the prepared starting state", "the active cooking or serving state", "the finished serving state"], 2: ["the exact final frame of clip 01", "the opening scene key visual", "the prepared starting state", "the active cooking or serving state", "the finished serving state", "the exact supplied advertised product"], 3: ["the exact final frame of clip 02", "the opening scene key visual", "the active cooking or serving state", "the finished serving state", "the exact supplied advertised product"]}[clip_no]
    defs = "\n".join(f"<Picture {i}> is {value}." for i, value in enumerate(refs, 1))
    cut_times = {1: "", 2: " At 00:01.600,", 3: " At 00:03.400,"}
    shot_lines = []
    for i, value in enumerate(p["shots"][clip_no - 1], 1):
        for prefix in ("0.0–1.6s — ", "1.6–3.4s — ", "3.4–5.0s — "):
            value = value.removeprefix(prefix)
        shot_lines.append(f"[Shot {i}]{cut_times[i]} {value}")
    shots = "\n\n".join(shot_lines)
    loc = 1 if clip_no == 1 else 2
    source = 2 if clip_no == 1 else 6 if clip_no == 2 else 5
    return f"""subject_definitions:
<Subject 1> is {p['talent']}
{defs}

summary:
reference generation. A five-second vertical grocery-commercial clip {clip_no} of three for {p['title']}. This is a real physical scene progression, not a montage. Cast, location, product identity and food state remain consistent with supplied references.

retention_analysis:
<Subject 1>: fully_preserved. Wardrobe, age, role and natural body mechanics remain consistent inside this product setting.
<Picture {loc}>: fully_preserved. It anchors the unique location, table/counter materials and spatial layout.
<Picture {source}>: fully_preserved. The exact advertised food family and, where supplied, the source package remain unchanged.
Food state: fully_preserved. {p['food_logic']}
No cast member, location, cookware or food family from another campaign may appear.

detailed_description:
{shots}

[Continuity guard] Treat <Picture {loc}> as the sole location and cast bible for this clip. Keep its counter or table height, wall materials, tableware, light direction and background depth stable from the opening to the final shot. Treat <Picture {source}> as the sole product-identity authority: preserve its real colour, proportions, surface, contents and supplied retail format. Do not replace it with a generic alternative. The transition from the prior shot must occur only through the stated hand, utensil, pot, steamer, plate or cup movement. Hold each endpoint still long enough for the next clip to inherit a clean frame. Keep the supplied food appetising but physically believable; no liquid should float, no steam should hide the action, and no ingredient may appear or disappear without the named movement.

Across all three shots retain {p['food']}. Match person and location to <Picture {loc}> and match advertised product exactly to <Picture {source}>. Use cuts only at 00:01.600 and 00:03.400. Every shot has one physical action and no repeated gesture. Keep hands anatomically correct, cookware rigid, steam controlled and food texture visibly coherent at every precise moment. Do not add captions, subtitles, title cards, price graphics, watermarks, fake app UI, camera shake, scene jumps, extra people, warped tools or a different food or package family. Avoid any unrelated cuisine, fictional package artwork, unreadable small print, excessive lens distortion, unstable focus, duplicated tableware or artificial looking human expressions.

overall_soundscape:
Natural location sound only: soft garden tea-table ambience for the terrace; restrained kitchen room tone, gas flame, boiling water, claypot-lid or bamboo-steamer sounds where physically present. No dialogue.

non_diegetic_music:
Warm restrained food-commercial music with a clean beat supporting the three timed shots without overpowering physical action.
"""

def sequence(p: dict) -> dict:
    base = f"../sequence_outputs/{p['slug']}/preproduction"
    assets = f"../outputs/reference_assets/{p['asset_dir']}/generated"
    refs = [f"{assets}/{p['slug']}_{kind}-1.png" for kind in ["character_scene", "prep_state", "cook_state", "hero_state"]]
    source = f"{base}/{p['source']}"
    return {"sequence_id": f"{p['slug']}_3x5_native1080", "server": "http://127.0.0.1:8189", "defaults": {"mode": "r2v", "width": 1088, "height": 1920, "duration": 5.0, "steps": 8, "turbo": True, "turbo_low_vram": True, "no_audio": True, "ref_image_size": "match", "poll": 10, "timeout": 10800}, "clips": [{"id": "clip-01-product-hook", "prompt_file": f"{base}/h3_prompts/clip_01_ref2va.md", "ref_images": [refs[0], source, refs[1], refs[2], refs[3]], "seed": 202608240201, "prefix": f"sequence/{p['slug']}_3x5_native1080/clip-01"}, {"id": "clip-02-transformation", "prompt_file": f"{base}/h3_prompts/clip_02_ref2va.md", "use_previous_last_frame_as_ref": True, "ref_images": [refs[0], refs[1], refs[2], refs[3], source], "seed": 202608240202, "prefix": f"sequence/{p['slug']}_3x5_native1080/clip-02"}, {"id": "clip-03-serving-hero", "prompt_file": f"{base}/h3_prompts/clip_03_ref2va.md", "use_previous_last_frame_as_ref": True, "ref_images": [refs[0], refs[2], refs[3], source], "seed": 202608240203, "prefix": f"sequence/{p['slug']}_3x5_native1080/clip-03"}], "final": {"filename": f"{p['slug']}_3x5_native_1080x1920.mp4", "concat_mode": "both", "crop": {"width": 1080, "height": 1920, "x": 4, "y": 0}, "crf": 16, "preset": "medium", "keep_audio": False}}

def package(p: dict) -> None:
    pre = ROOT / "sequence_outputs" / p["slug"] / "preproduction"
    write(pre / "recipe_bible.md", f"""# {p['title']} — Revision 2 Production Bible

## Creative route

{p['scene']}. {p['talent']}

## Product and food rules

{p['food_logic']} The user-supplied source is the product authority. {p['pack_rule']}

## Reference-image rule

The opening reference visibly includes the supplied product/package where one exists, plus the approved physical tabletop sign. The H3 direction itself does not name that sign.

## States

1. Opening — {p['states']['character_scene']}
2. Prep — {p['states']['prep_state']}
3. Process — {p['states']['cook_state']}
4. Finish — {p['states']['hero_state']}
""")
    ref_dir = pre / "reference_prompts"
    for kind in ["character_scene", "prep_state", "cook_state", "hero_state"]:
        write(ref_dir / f"{kind}.md", reference_prompt(p, kind))
    board = [f"# {p['title']} — Revision 2 Storyboard", "", "Three independent 5-second vertical H3 R2V clips. Each has three timed shots and uses the supplied source as product authority.", ""]
    for n, (title, shots) in enumerate(zip(p["titles"], p["shots"]), 1):
        board += [f"## Clip {n}: {title}", "", *[f"- {shot}" for shot in shots], ""]
    write(pre / "storyboard.md", "\n".join(board))
    for n in range(1, 4):
        write(pre / "h3_prompts" / f"clip_{n:02d}_ref2va.md", h3_prompt(p, n))
    manifest = {"revision": 2, "product": p["title"], "source_product_reference": p["source"], "physical_sign_reference": "../../../company_logo/AGO.png", "assets": {kind: f"outputs/reference_assets/{p['asset_dir']}/generated/{p['slug']}_{kind}-1.png" for kind in ["character_scene", "prep_state", "cook_state", "hero_state"]}, "generation_order": ["character_scene", "prep_state", "cook_state", "hero_state"]}
    write(pre / "reference_manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    write(SEQUENCES / f"{p['slug']}_3x5_1080.json", json.dumps(sequence(p), ensure_ascii=False, indent=2))

def main() -> None:
    for p in PRODUCTS:
        package(p)
        print(f"prepared revision 2: {p['slug']}")

if __name__ == "__main__":
    main()
