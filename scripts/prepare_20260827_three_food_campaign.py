#!/usr/bin/env python3
"""Prepare three no-person cooking/video-reference packages for the 2026-08-27 batch."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEQUENCES = ROOT / "sequences"


PRODUCTS = [
    {
        "slug": "bacon_carbonara_spicy_ramen",
        "title": "培根奶油火鸡面",
        "en": "Bacon Carbonara Spicy Ramen",
        "asset_dir": "45_bacon_carbonara_buldak",
        "source_products": ["outputs/reference_assets/45_bacon_carbonara_buldak/source_products/k_spicy_carbonara_ramen.png"],
        "scene": "a cozy late-evening Korean apartment kitchen with matte charcoal lower cabinets, small square pale-pink ceramic backsplash tiles, a black speckled quartz counter, one compact stainless saucepan, a shallow charcoal sauté pan, soft warm under-cabinet light and a blurred rain-dark window",
        "food": "springy thick curled instant noodles in a creamy pale-orange carbonara sauce, real irregular bacon strips browned at their edges, finely grated pale cheese, a light dusting of dried green herbs and a soft egg yolk only as a final unbroken garnish",
        "logic": "Boil the noodles until springy, retain a small amount of noodle water, then drain. Render real bacon strips until their fat is glossy and their edges are browned, never dry or uniformly square. Warm the supplied spicy sauce with milk or cooking cream and the retained noodle water over low heat, fold in the noodles and carbonara seasoning until every curl is glossy pale orange. Finish with cheese; the yolk stays intact on the plated noodles and is not scrambled into the sauce. The dish must be creamy and substantial rather than a red soup, with no fake cheese pull or excessive chilli flakes.",
        "sources": [
            ("Buldak official: five ingredients for carbonara ramen", "https://buldak.com/us/blog/5-ingredients-for-how-to-make-buldak-carbonara/", "官方做法建议煮面、保留少量面汤，低火加入酱料、奶或奶油、蛋黄与奶酪；本片以培根补足香气。"),
            ("Rose Buldak carbonara ramen", "https://ivyskitchn.substack.com/p/rose-buldak-carbonara-ramen-with", "培根先煎香，再用奶油、面汤和调味粉形成浓滑酱汁。"),
        ],
        "states": {
            "scene_anchor": "Vertical no-person opening in this charcoal-and-pink Korean kitchen. The exact supplied pink noodle multipack stands upright and fully readable at the rear-left; it must not be redrawn or replaced. A small physical AGO tabletop tent card from Image 1 stands beside it. In front: one nest of uncooked curled noodles, short irregular bacon strips, a small glass jug of cream, grated pale cheese and a black saucepan of gently simmering water. Keep the package and tabletop card secondary to the ingredient action; no people.",
            "prep_state": "Top three-quarter no-person ingredient scene in the charcoal-and-pink Korean kitchen: thick curled noodles have just been drained in a small stainless colander, while irregular 2 to 5 cm bacon strips render in a shallow charcoal sauté pan. A small jug of cream, a cup of reserved clear noodle water, carbonara seasoning and finely grated pale cheese sit in distinct bowls. No package, sign, face, body or hands.",
            "cook_state": "Close no-person pan image: springy thick noodle curls are folded through a creamy pale-orange sauce in the shallow charcoal pan. Glossy irregular bacon strips with varied brown edges are dispersed naturally, not evenly repeated. A small amount of cheese softens into the sauce; it clings to the noodles and is never watery, red, or a cheese-pull spectacle. No package, sign, person or hand.",
            "hero_state": "Final no-person serving hero in the charcoal-and-pink Korean kitchen: a shallow matte-black bowl holds a loose natural mound of creamy pale-orange curled noodles, irregular browned bacon strips, a small amount of grated pale cheese and one intact golden egg yolk at the centre. The sauce is rich and glossy but not overly thick; no package, sign, people, face, body, chopsticks or invented garnishes.",
        },
        "titles": ["Cream, bacon and noodle setup", "Low-heat carbonara fold", "Creamy noodle bowl hero"],
        "shots": [
            [
                "A locked 45mm high three-quarter counter shot begins on one nest of uncooked curled noodles, irregular bacon strips, a small jug of cream, grated pale cheese and a compact saucepan of clear simmering water. No person or hand is visible. The pan and ingredients remain cleanly separated, ending with the noodle texture and real bacon cut easily readable.",
                "Cut to a 70mm saucepan-height insert, continuing from a colander already lifted clear of the pot and resting tipped against its rim. The cooked springy noodles sit drained inside it while the last clear noodle water drains back down in thin streams under gravity alone. No hand, arm or reflection is visible. End with the noodles drained but visibly moist.",
                "Cut to a 65mm shallow-pan side shot. The varied bacon strips quietly render in the charcoal pan until their edges turn naturally golden-brown and the rendered fat shines. The pieces stay irregular and meaty, never tiny perfect cubes. End before any cream enters the pan.",
            ],
            [
                "A locked 55mm pan-height shot begins on the browned irregular bacon strips in a shallow pan, with a small glass jug already tipped and propped at the pan's edge so cream and clear retained noodle water stream steadily from its spout into the pan under gravity alone, then the flow tapers off as the jug empties. No hand or person is visible. The sauce becomes a pale base; it is not red or soupy.",
                "Cut to an 80mm close insert. Springy drained noodle curls rest settled into the pale sauce, already turned and coated in one motion off-camera. The sauce reads creamy pale orange, evenly clinging to every curl with no splash marks. End with bacon still clearly visible between the coated noodles.",
                "Cut to a 65mm pan-side medium close shot. Finely grated pale cheese melts gently into the glossy noodle coating while heat stays low and controlled. The noodles remain distinct, bouncy and curled rather than swollen or mushy. End with an even creamy sauce and no cheese strings.",
            ],
            [
                "A locked 50mm three-quarter bowl shot begins on the finished creamy pale-orange noodle curls and naturally irregular bacon strips in the charcoal pan, with a single intact egg yolk already resting at the centre of the noodles, placed just before this shot begins. The yolk stays undisturbed and unbroken for the whole shot.",
                "Cut to an 85mm macro texture insert. Warm steam rises softly from glossy curls, browned bacon edges and the intact yolk while a light scattering of grated cheese rests on the sauce. Keep steam controlled so the food remains crisp and appetising. End with realistic creamy texture, not melted plastic.",
                "Cut to a calm 60mm final serving hero. A shallow matte-black bowl holds the loose finished noodle mound with bacon, light cheese and one intact yolk. Everything is still; no utensils, package, sign or human is visible. End on the bowl centred against the same charcoal, pink and warm-light kitchen.",
            ],
        ],
    },
    {
        "slug": "luncheon_meat_scrambled_eggs",
        "title": "午餐肉炒鸡蛋",
        "en": "Luncheon Meat Scrambled Eggs",
        "asset_dir": "46_korean_luncheon_meat_scrambled_eggs",
        "source_products": ["outputs/reference_assets/46_korean_luncheon_meat_scrambled_eggs/source_products/korean_luncheon_meat.png"],
        "scene": "a bright Korean breakfast kitchen with creamy ivory terrazzo worktops, cornflower-blue cabinet fronts, brushed nickel hardware, a low round pale-grey wok, a compact white gas burner, thin flax curtains and crisp early-morning sunlight",
        "food": "real pink luncheon meat cut into varied 1.5 cm chunky cubes with browned seared faces, soft glossy yellow egg curds, a few thin scallion rings and neutral cooking oil",
        "logic": "Cut the supplied luncheon meat into 1.5 cm irregular chunky cubes, pan-fry them first until a portion of the faces has a light golden-brown sear, then set them aside. Beat eggs with a small splash of milk or water and a few scallion rings. Cook over low-to-medium heat, folding only until soft glossy curds form; return the browned meat at the end so both ingredients stay distinct. Avoid a perfectly uniform dice, dry rubbery egg, burnt meat, breading, sauce puddles, rice, toast or unrelated breakfast dishes.",
        "sources": [
            ("Kikkoman: egg and luncheon meat stir-fry", "https://www.kikkoman.com/en/cookbook/recipe/00001334.html", "午餐肉可切成约 5mm 到小块并与鸡蛋快炒；本片采用更饱满的 1.5cm 块状以保留口感。"),
            ("Korean-style luncheon meat and egg comfort bowl", "https://www.myfreshdash.com/post/how-to-make-egg-spam-mayo-rice-bowl-easy-korean-comfort-food-recipe", "午餐肉先煎香，鸡蛋保持软嫩；本片去掉米饭与蛋黄酱，专注炒蛋主体。"),
        ],
        "states": {
            "scene_anchor": "Vertical no-person opening in this bright blue-and-terrazzo Korean breakfast kitchen. The exact supplied yellow-lidded luncheon-meat tin stands upright and fully readable at rear-left; it must not be redrawn, relabelled or replaced. A small physical AGO tabletop tent card from Image 1 stands beside it. In front are a few varied 1.5 cm pink luncheon-meat cubes on a pale ceramic dish, three brown eggs, a small bowl of thin scallion rings and a pale-grey wok warming on a compact burner. No people.",
            "prep_state": "Top three-quarter no-person preparation image in the blue-and-terrazzo Korean breakfast kitchen: varied 1.5 cm luncheon-meat cubes sit on a small plate; a clear bowl holds beaten eggs with a few scallion rings. A pale-grey wok with a thin sheen of oil heats nearby. Cubes are real meat with irregular corners and natural pink interior, not breaded or copy-pasted. No package, sign, face, body or hands.",
            "cook_state": "Close no-person wok image: lightly browned luncheon-meat cubes with varied seared faces sit beside soft glossy yellow egg curds in a pale-grey wok. The curds are different natural sizes, softly folded and moist rather than finely granulated or dry. A few scallion rings are visible; no sauce puddle, rice, toast, package, sign, person or hand.",
            "hero_state": "Final no-person breakfast hero in the blue-and-terrazzo kitchen: a small ivory oval plate holds an uneven, appetising mix of soft yellow egg curds and 1.5 cm browned luncheon-meat cubes, scattered with a few scallion rings. Meat edges have real variance and the eggs look softly set. No rice, toast, toast crumbs, ketchup, extra dishes, package, sign, people or utensils.",
        },
        "titles": ["Meat cube and egg setup", "Sear first, fold softly", "Soft-scramble breakfast hero"],
        "shots": [
            [
                "A locked 45mm high three-quarter countertop shot begins on varied 1.5 cm pink luncheon-meat cubes, three eggs, a small bowl of scallion rings and a pale-grey wok with a thin sheen of oil. The sunrise kitchen is empty and clean; no person or hand appears. End with the chunk size, irregular corners and separate egg ingredient clear.",
                "Cut to a 70mm wok-height insert. The real meat cubes are spread across the pale-grey wok and quietly sear in one layer. They remain chunky and non-uniform, not minced or breaded. End when a portion of the bottom faces becomes lightly golden-brown.",
                "Cut to a 65mm side close shot. Several cubes turn naturally to show mixed pink and lightly browned faces with glistening edges. Heat stays moderate, without black burn marks, sauce or smoke. End with the seared cubes ready to be combined.",
            ],
            [
                "A locked 55mm pan shot begins on the lightly browned meat cubes resting at one side of the pale-grey wok, with a bowl of beaten egg and scallion rings already tipped and propped at the wok's empty side so the egg streams in under gravity alone and settles into a thin even layer, then the flow stops as the bowl empties.",
                "Cut to an 80mm close insert. The eggs set from the edge inward into large soft yellow glossy curds, already folded once just before this shot begins, while the meat cubes remain distinct. End with moist curds, never dry crumbs.",
                "Cut to a 65mm wok-side medium close shot. The browned meat cubes tumble gently once through the soft egg curds and settle, leaving an uneven natural mixture. The dish has no sauce puddle and no unrelated ingredients. End on the final cooked texture.",
            ],
            [
                "A locked 50mm three-quarter wok hero begins on the finished soft egg curds and varied browned meat cubes, with a few scallion rings already scattered across the top just before this shot begins. Nothing else moves. End with a restrained fresh green accent.",
                "Cut to an 85mm macro texture insert. Light catches the moist folds of egg and the unevenly seared faces of the chunky meat cubes. Keep individual eggs and cubes readable and naturally varied, with no artificial repetition. End sharp and appetising.",
                "Cut to a calm 60mm final plate hero. The small ivory oval plate holds only the finished scrambled eggs, browned luncheon-meat cubes and a few scallion rings. No rice, toast, sauce, package, sign, utensils or human is visible. End centred in the same bright blue-and-terrazzo breakfast kitchen.",
            ],
        ],
    },
    {
        "slug": "seedless_cantaloupe_milk",
        "title": "无籽蜜瓜牛奶",
        "en": "Seedless Cantaloupe Milk",
        "asset_dir": "47_seedless_cantaloupe_milk",
        "source_products": ["outputs/reference_assets/47_seedless_cantaloupe_milk/source_products/cantaloupe_reference.png"],
        "scene": "a sunlit summer drinks kitchen with powder-blue checkerboard wall tile, pale birch cabinetry, a cool white stone island, a clear glass blender, a ribbed glass tumbler and long clean midday shadows from a nearby window",
        "food": "ripe orange cantaloupe flesh only, completely free of rind, green skin, seeds, seed cavity, fibrous membranes and strings, blended smooth with cold whole milk and a few transparent ice cubes into a pale melon-orange milk drink",
        "logic": "Use only ripe orange cantaloupe flesh. Before the first frame, remove the rind, every seed, the entire seed cavity and all fibrous pale membranes; none may be visible in any ingredient, blender, spill, reflection, garnish or background. Blend 250 g clean melon flesh with 250 ml cold milk and a few ice cubes until fully smooth. The colour should be a natural pale creamy melon-orange, not neon orange, green, grey, speckled, foamy or smoothie-thick. Serve simply, with a small clean seedless orange melon cube garnish if desired.",
        "sources": [
            ("Tucson CSA: Licuado de Melon", "https://tucsoncsa.org/recipe/licuado-de-melon-melon-smoothie/", "熟蜜瓜可与全脂牛奶或替代奶直接搅打成奶昔。"),
            ("Cantaloupe melon milk", "https://pinkmixers.wordpress.com/2010/09/02/cantaloupe-melon-milk/", "制作前需去皮、去籽；本片进一步要求去除籽瓤与纤维，只保留纯果肉。"),
        ],
        "states": {
            "scene_anchor": "Vertical no-person opening in this powder-blue summer drinks kitchen. A small physical AGO tabletop tent card from Image 1 sits far back on the white stone island. In front: one clear bowl of perfectly clean orange cantaloupe flesh cubes only, a small chilled glass milk bottle, several transparent ice cubes and an empty glass blender. There is no whole melon, rind, green skin, half melon, seed cavity, seed, fibrous membrane or string anywhere. No people.",
            "prep_state": "Top three-quarter no-person preparation scene in the powder-blue summer drinks kitchen: flawless clean orange cantaloupe cubes only are tipped inside a clear glass blender with cold white milk and a few transparent ice cubes. The visible fruit is pure flesh with smooth cut faces. No rind, green skin, seeds, seed cavity, fibrous membrane, spoon, package, sign, face, body or hands.",
            "cook_state": "Close no-person blend-state image: the clear blender contains a fully smooth pale creamy melon-orange milk drink with a gentle central vortex and tiny natural surface ripples. The liquid has no black specks, orange seeds, white strings, pulp clumps or green fragments. Milk and fruit are fully combined, not layered. No package, sign, person or hand.",
            "hero_state": "Final no-person drinks hero in the powder-blue summer kitchen: one ribbed clear glass is filled with cold pale creamy melon-orange milk, several transparent ice cubes and one small pristine orange melon-flesh cube on a short pick at the rim. The drink is smooth, clean and lightly glossy. No seeds, seed cavity, rind, green skin, membranes, strings, smoothie foam, package, sign, person or hand.",
        },
        "titles": ["Pure melon-flesh and milk setup", "Smooth seed-free blend", "Cold cantaloupe milk hero"],
        "shots": [
            [
                "A locked 45mm high three-quarter island shot begins on a clear bowl of pristine orange cantaloupe flesh cubes only, cold milk, transparent ice cubes and an empty clear blender. The sunlit powder-blue kitchen is empty. No melon rind, green skin, seed cavity, seed, membrane or string exists anywhere in the frame. End with the clean fruit flesh visibly simple and fresh.",
                "Cut to a 70mm blender-height insert, continuing from a bowl of clean orange fruit cubes already tipped and propped just above the clear blender jar so the cubes drop in under gravity alone, followed by a few transparent ice cubes sliding in the same way. End with fruit and ice cleanly separated in the jar.",
                "Cut to a 65mm side close shot, continuing from a chilled milk bottle already tipped and propped just above frame so cold milk pours in a single white ribbon under gravity alone and pools around the fruit cubes, then the flow stops as the bottle rights itself. End before blending begins, with only clean orange flesh, milk and clear ice in view.",
            ],
            [
                "A locked 55mm blender-side shot begins on the clear jar containing clean orange melon flesh, cold milk and ice. The blender activates with a controlled gentle motion, making the contents rotate smoothly. No person, reflection or hand appears and the background stays fixed.",
                "Cut to an 80mm close insert. The mixture transitions from visible cubes to a uniform pale creamy melon-orange liquid with a small central vortex. No seeds, dark specks, pale strings, fibrous fragments, foam crown or separated layers can appear. End with the drink fully smooth.",
                "Cut to a 65mm glass-height medium close shot. The blender stops and the smooth pale melon-orange milk settles with only subtle surface ripples. The clean white-stone counter and powder-blue tiles remain consistent. End ready for the serving pour.",
            ],
            [
                "A locked 50mm three-quarter serving shot begins on a ribbed clear glass with several transparent ice cubes, with the blender jar already tipped and propped just above frame so smooth pale creamy melon-orange milk pours in one unbroken stream under gravity alone. End when the glass is nearly full without overflow, and the jar rights itself as the pour finishes.",
                "Cut to an 85mm macro texture insert. A single pristine orange melon-flesh cube rests on a short pick at the rim while clear ice refracts the softly coloured drink. Keep the liquid perfectly smooth and natural-looking, with no seeds, strings, rind, green skin or heavy foam. End on cold condensation and clean fruit texture.",
                "Cut to a calm 60mm final glass hero. One ribbed clear glass of pale melon-orange milk sits centred on white stone under long midday shadows, with clear ice and the single clean orange flesh cube garnish. No package, sign, utensils, whole melon or human is visible. End with a simple fresh summer-drink finish.",
            ],
        ],
    },
]


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def reference_prompt(p: dict, kind: str) -> str:
    product_reference = ""
    if kind == "scene_anchor" and p["source_products"]:
        product_reference = "Image 2 is the approved supplied product pack; reproduce it faithfully only where the scene specifies it, with its package geometry and printing untouched. "
    return f"""Use case: ads-marketing
Asset type: no-person MiniMax H3 R2V reference image for a vertical food commercial
Primary request: create the {kind.replace('_', ' ')} reference for {p['en']}.
Input image: Image 1 is the approved ASIAN GROCER ONLINE / powered by UMALL tabletop sign artwork; preserve it only where the scene asks for a physical tabletop card. {product_reference}
Scene/backdrop: {p['scene']}.
Subject: {p['states'][kind]}
Food authority: {p['food']}.
Style/medium: high-end photorealistic food-commercial still with real cookware, natural appetising texture and physically plausible condensation or controlled steam.
Composition/framing: vertical 9:16, one calm food state, no face, body, portrait, person or hands.
Lighting/mood: crisp directional food light with coherent shadows and clean highlight detail.
Constraints: {p['logic']} No fake labels, captions, price graphics, watermarks, invented products or extra dishes.
Avoid: warped utensils, melted food, excessive steam, clutter, fake app interface and any visible human.
"""


def h3_prompt(p: dict, clip_no: int) -> str:
    refs = {
        1: ["the no-person scene and dish-identity anchor", "the prepared ingredient state", "the cooking or blending state", "the finished serving-state target"],
        2: ["the exact final frame of clip 01", "the no-person scene and dish-identity anchor", "the prepared ingredient state", "the cooking or blending state", "the finished serving-state target"],
        3: ["the exact final frame of clip 02", "the no-person scene and dish-identity anchor", "the cooking or blending state", "the finished serving-state target"],
    }[clip_no]
    definitions = "\n".join(f"<Picture {i}> is {value}." for i, value in enumerate(refs, 1))
    cut_times = {1: "", 2: " At 00:01.600,", 3: " At 00:03.400,"}
    shot_lines = []
    for i, sentence in enumerate(p["shots"][clip_no - 1], 1):
        shot_lines.append(f"[Shot {i}]{cut_times[i]} {sentence}")
    shots = "\n\n".join(shot_lines)
    spatial_ref = 1 if clip_no == 1 else 2
    food_ref = 2 if clip_no == 1 else 3 if clip_no == 2 else 3
    return f"""subject_definitions:
<Subject 1> is the dish and essential cookware only. No human person is a subject, visible actor, reflection or shadow.
{definitions}

summary:
reference generation. A five-second vertical no-person food commercial, clip {clip_no} of three, for {p['en']}. It advances exactly one real food state while retaining the same kitchen materials, lighting, cookware and dish identity from the local reference stack.

retention_analysis:
<Subject 1>: fully_preserved. Food, ingredient sizes, cookware, liquid behaviour and all no-person restrictions remain physically coherent.
<Picture {spatial_ref}>: fully_preserved. It anchors the unique kitchen, counter, vessel, camera height, light direction and empty-set treatment.
<Picture {food_ref}>: fully_preserved. It preserves the exact ingredients, cut size, colour, sheen and stage of preparation.
Food sequence: fully_preserved. {p['logic']}
Human visibility: fully_preserved. Never reveal a face, head, torso, arm, hand, reflection, shadow or portrait.

detailed_description:
{shots}

[Continuity guard] Treat <Picture {spatial_ref}> as the only spatial and lighting bible. Keep counter material, wall treatment, pan or blender, burner, bowl, glass and tableware identical throughout the clip. Treat <Picture {food_ref}> as the food-state authority: preserve its ingredients, cut size, colour, sheen and preparation stage exactly. No food may appear, disappear, melt, float or transform without the named motion. Keep every human entirely out of frame, including reflections in metal, glass, windows and polished surfaces. Hold each endpoint cleanly for the next clip to inherit.

[Frame discipline] Keep the food as the central subject in every frame, with one vessel and one action readable. Do not introduce decorative props that obscure the ingredient state. Maintain believable gravity, liquid level, utensil contact when invisible, cooking heat and condensation. Preserve clean negative space and avoid sudden changes in time of day, colour temperature or table layout. The camera is rigid within each shot and every movement is small, deliberate and physically motivated.

Across all shots retain {p['food']}. Use cuts only at 00:01.600 and 00:03.400, with one physical action per shot and a stable camera. Keep cookware rigid, steam controlled and food texture coherent at every moment. Do not add people, faces, bodies, hands, shadows, reflections, captions, subtitles, title cards, price graphics, watermarks, fake labels, shopping UI, camera shake, scene jumps, warped tools, extra fingers, different cuisine or different dish identity. Avoid blank product-free endings and excessive close-ups of any non-food object.

overall_soundscape:
Natural food-preparation ambience only: gentle simmer, bacon sizzle, low pan crackle, blender hum, soft liquid pour, ice clink and ceramic placement as physically appropriate. No dialogue.

non_diegetic_music:
Restrained warm food-commercial instrumental with a clean three-shot cadence and no vocals.
"""


def sequence(p: dict) -> dict:
    base = f"../sequence_outputs/{p['slug']}/preproduction"
    assets = f"../outputs/reference_assets/{p['asset_dir']}/generated"
    refs = [f"{assets}/{p['slug']}_{kind}-1.png" for kind in ["scene_anchor", "prep_state", "cook_state", "hero_state"]]
    return {
        "sequence_id": f"{p['slug']}_3x5_native1080",
        "server": "http://127.0.0.1:8189",
        "defaults": {"mode": "r2v", "width": 1088, "height": 1920, "duration": 5.0, "steps": 8, "turbo": True, "turbo_low_vram": True, "no_audio": True, "ref_image_size": "match", "poll": 10, "timeout": 10800},
        "clips": [
            {"id": "clip-01-prep-hook", "prompt_file": f"{base}/h3_prompts/clip_01_ref2va.md", "ref_images": refs, "seed": 202608270101, "prefix": f"sequence/{p['slug']}_3x5_native1080/clip-01"},
            {"id": "clip-02-cook-proof", "prompt_file": f"{base}/h3_prompts/clip_02_ref2va.md", "use_previous_last_frame_as_ref": True, "ref_images": refs, "seed": 202608270102, "prefix": f"sequence/{p['slug']}_3x5_native1080/clip-02"},
            {"id": "clip-03-serving-hero", "prompt_file": f"{base}/h3_prompts/clip_03_ref2va.md", "use_previous_last_frame_as_ref": True, "ref_images": [refs[0], refs[2], refs[3]], "seed": 202608270103, "prefix": f"sequence/{p['slug']}_3x5_native1080/clip-03"},
        ],
        "final": {"filename": f"{p['slug']}_3x5_native_1080x1920.mp4", "concat_mode": "both", "crop": {"width": 1080, "height": 1920, "x": 4, "y": 0}, "crf": 16, "preset": "medium", "keep_audio": False},
    }


def package(p: dict) -> None:
    pre = ROOT / "sequence_outputs" / p["slug"] / "preproduction"
    write(pre / "recipe_bible.md", f"""# {p['title']} — 无真人制作圣经

## Recipe logic

{p['logic']}

## Visual rule

No visible person, hands, reflection or human shadow. The first reference frame uses the physical AGO tabletop card. For supplied packaged products, that first reference frame also preserves the exact approved source packaging. H3 video prompts deliberately use neither a company name nor a logo instruction.

## Reference states

1. Opening — {p['states']['scene_anchor']}
2. Prep — {p['states']['prep_state']}
3. Cook / blend — {p['states']['cook_state']}
4. Hero — {p['states']['hero_state']}
""")
    write(pre / "recipe_sources.md", "# Recipe Sources\n\n" + "\n".join(f"- [{name}]({url}) — {note}" for name, url, note in p["sources"]))
    for kind in ["scene_anchor", "prep_state", "cook_state", "hero_state"]:
        write(pre / "reference_prompts" / f"{kind}.md", reference_prompt(p, kind))
    lines = [f"# {p['title']} — 无真人 3×5s 分镜", "", "三个独立的 5 秒 H3 R2V 片段。所有镜头均无真人、无手、无倒影。", ""]
    for n, (title, shots) in enumerate(zip(p["titles"], p["shots"]), 1):
        lines += [f"## Clip {n}: {title}", "", *[f"- {shot}" for shot in shots], ""]
    write(pre / "storyboard.md", "\n".join(lines))
    for n in range(1, 4):
        write(pre / "h3_prompts" / f"clip_{n:02d}_ref2va.md", h3_prompt(p, n))
    manifest = {
        "product": p["title"],
        "dish_identity": p["food"],
        "physical_sign_reference": "../../../company_logo/AGO.png",
        "source_product_images": p["source_products"],
        "assets": {kind: f"outputs/reference_assets/{p['asset_dir']}/generated/{p['slug']}_{kind}-1.png" for kind in ["scene_anchor", "prep_state", "cook_state", "hero_state"]},
        "generation_order": ["scene_anchor", "prep_state", "cook_state", "hero_state"],
    }
    write(pre / "reference_manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    write(SEQUENCES / f"{p['slug']}_3x5_1080.json", json.dumps(sequence(p), ensure_ascii=False, indent=2))


def main() -> None:
    for product in PRODUCTS:
        package(product)
        print(f"prepared {product['slug']}")


if __name__ == "__main__":
    main()
