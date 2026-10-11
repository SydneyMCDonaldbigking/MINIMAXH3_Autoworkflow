#!/usr/bin/env python3
"""Create four no-person food-commercial reference and MiniMax H3 packages."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEQUENCES = ROOT / "sequences"

PRODUCTS = [
    {
        "slug": "chive_egg_boiled_dumplings", "title": "Chive and Egg Boiled Dumplings", "cn": "韭菜鸡蛋水饺", "asset_dir": "41_chive_egg_boiled_dumplings",
        "scene": "a bright rustic northern Chinese family kitchen with warm ochre hand-glazed square tiles, a dark elm butcher-block worktable, blue-rim ceramic bowls, bamboo tools, a black stockpot on a blue gas flame and cool late-morning window light",
        "food": "thin wheat-wrapper crescent dumplings filled only with finely chopped Chinese chives and fluffy scrambled egg, cooked until plump and glossy",
        "logic": "Chop dry Chinese chives, scramble egg into small soft curds, season and mix immediately before wrapping. Fill and crimp thin dough rounds into crescents, then cook in actively boiling water until the dumplings float and look plump before lifting them out.",
        "sources": [("韭菜鸡蛋水饺", "https://home.meishichina.com/recipe-523045.html", "韭菜鸡蛋馅调味后包制，水烧开下饺子，煮至成熟捞出。"), ("韭菜鸡蛋水饺技巧", "https://www.dachu.co/zh-cn/recipe/141758", "韭菜应在擀好皮后再加盐拌馅，减少出水。")],
        "states": {
            "scene_anchor": "Vertical kitchen opening with no people. A white ceramic bowl of pale wheat dough rounds, dry chopped Chinese chives, soft yellow scrambled egg curds, a small bowl of filling, a wooden rolling pin and a bamboo board sit on the dark elm butcher-block table against warm ochre hand-glazed square tile. A black stockpot of water is ready over a blue gas flame. The exact AGO sign from Image 1 is a small physical tabletop tent card at the far table edge.",
            "prep_state": "Top three-quarter no-person preparation image in the rustic northern Chinese kitchen: finely chopped green chives and fluffy scrambled egg curds are combined in one blue-rim ceramic bowl; thin round wrappers, wooden rolling pin and a small spoon sit beside the filling. Several raw crescent dumplings are neatly spaced on a floured bamboo board. No face or body.",
            "cook_state": "Close no-person cooking image in the rustic northern Chinese kitchen: a long-handled slotted spoon rests across the black stockpot and lifts several plump boiled chive-and-egg dumplings from clear rolling water. Warm ochre glazed tiles and dark elm worktop remain visible; steam rises; dumplings are intact, pale and glossy.",
            "hero_state": "Final no-person table hero in the rustic northern Chinese kitchen: a blue-rim shallow ceramic plate holds plump boiled chive-and-egg dumplings, one cut open to reveal vivid green chives and soft yellow egg. A small dish of black vinegar and chilli oil sits nearby on dark elm; no other dumpling fillings or people.",
        },
        "titles": ["Fresh filling and wrapper setup", "Crimped dumpling proof", "Rolling-boil to plated finish"],
        "shots": [
            ["Locked 45mm high three-quarter table shot. Begin on dry chopped chives, fluffy scrambled egg, thin wrappers and rolling pin in the bright northern kitchen. An anonymous hand cropped at the wrist folds the chives and egg together once with a wooden spoon, then leaves the glossy filling settled in the bowl. End with filling and wrappers clearly separated.", "Cut to a 70mm overhead insert. A small spoon places one measured portion of the green-and-yellow filling at the centre of a thin wheat wrapper. The spoon withdraws and the wrapper remains flat, with no other fillings entering frame. End ready for the crimping action.", "Cut to a 65mm board-level medium close shot. Two cropped anonymous hands fold the wrapper into one clean crescent and press a neat pleated seam, then release it onto the floured bamboo board. End on one intact raw dumpling among a few matching crescents."],
            ["Locked 60mm board-level shot. Begin with several identical raw crescent dumplings neatly spaced on a floured bamboo board. Cropped anonymous hands lift one dumpling by the seam and set it down once, confirming the thin wrapper and sealed edge without tearing it.", "Cut to an 85mm macro insert. The pleated crescent seam and faint green-and-yellow filling silhouette stay crisp while a light dusting of flour settles on the board. No hands cross the frame after placement. End on the sealed dumpling texture.", "Cut to a medium pot-height shot. A slotted spoon lowers three raw dumplings together into clear rolling water in the black pot over blue flame. The dumplings enter once and the spoon stops; end at water entry under controlled steam."],
            ["Locked 55mm pot shot. Begin on the clear rolling boil as pale dumplings float gently and become plump. A slotted spoon makes one slow lift beneath three dumplings, without breaking the water surface yet.", "Cut to an 80mm close insert. The spoon rises above the pot holding glossy intact dumplings while clear water drains back in thin streams. Steam stays behind the dumplings and does not obscure their crescent forms. End with the spoon held level.", "Cut to a calm 65mm plate hero. The spoon places the dumplings onto a shallow white plate beside black vinegar and chilli oil; one dumpling is already cut cleanly to show chives and egg. End with the plated dumplings sharp and appetising."],
        ],
    },
    {
        "slug": "classic_wagyu_sukiyaki", "title": "Classic Wagyu Sukiyaki", "cn": "经典和牛寿喜烧", "asset_dir": "42_classic_wagyu_sukiyaki",
        "scene": "a calm Japanese dining-kitchen with dark walnut table, indigo ceramic tiles, a shallow black cast-iron sukiyaki pan on a compact tabletop burner and warm evening side light",
        "food": "real 1 mm paper-thin Wagyu sukiyaki slices with fine natural marbling, tofu, napa cabbage, shiitake, enoki, Japanese long onion and shirataki noodles in clear shallow sweet-savoury warishita",
        "logic": "For a classic Kansai-style visual route, use loosely folded, irregular 1 mm Wagyu slices rather than thick rectangular slabs or steak. Sear the thin beef, add sugar and the soy-sake-mirin sauce, then simmer until every visible beef surface is fully cooked warm chestnut-brown with no pink or red remaining; keep it thin and tender rather than dry. Simmer tofu, mushrooms, napa cabbage, long onion and shirataki gently. The sauce must remain a clear, shallow glossy brown warishita, never a broth-heavy hotpot.",
        "sources": [("Taste of Japan: Sukiyaki guide", "https://japan-food.jetro.go.jp/en/recipe/104.html", "寿喜烧的甜咸汁以酱油、糖、清酒和味醂构成，通常在浅铁锅中煮制。"), ("Wagyu sukiyaki", "https://www.greatbritishchefs.com/recipes/wagyu-sukiyaki-recipe", "和牛寿喜烧搭配豆腐、香菇和蔬菜，酱汁由酱油、味醂、清酒和糖调制。")],
        "states": {
            "scene_anchor": "Vertical no-person Japanese-table opening. A shallow black cast-iron sukiyaki pan sits on a compact burner over dark walnut. Around it are separate, irregular 1 mm Wagyu slices that are soft pink-red and naturally fine-marbled rather than thick steak-like slabs, with tofu, napa cabbage, shiitake, enoki, Japanese long onion, shirataki and a small ceramic pitcher of dark sweet-savoury sauce. The exact AGO sign from Image 1 is a small physical tent card far back on the table.",
            "prep_state": "Top three-quarter no-person ingredient layout: real 1 mm Wagyu slices overlap loosely like delicate shabu-shabu ribbons on a plate, with small natural flecks of fat rather than exaggerated white lattice marbling; tofu blocks, napa cabbage, shiitake with decorative cuts, enoki, long onion, shirataki and a small bowl of soy-sugar-mirin-sake sauce. Shallow iron pan is empty and ready; no faces or bodies.",
            "cook_state": "Close no-person shallow-pan image: a few 1 mm Wagyu slices curl naturally at their edges and are fully cooked through in clear, shallow glossy brown warishita. Each visible surface is warm chestnut-brown with natural folded ripples and no pink or red remaining; never thick blocks, grey slabs or a pile of meat. Tofu, shiitake, long onion and napa cabbage simmer around it in distinct zones; sauce is transparent and reduced, never a red soup.",
            "hero_state": "Final no-person dinner hero: shallow iron pan contains a small number of fully cooked loosely folded 1 mm Wagyu ribbons, uniformly warm chestnut-brown but still tender, with tofu, shiitake, napa cabbage, long onion and shirataki in distinct zones of shallow sweet-savoury glaze. No chopstick lift, no people and no unrelated hotpot ingredients.",
        },
        "titles": ["Wagyu and shallow-pan setup", "Sweet-soy Wagyu sear", "Glazed sukiyaki finish"],
        "shots": [
            ["Locked 45mm table-height shot. Begin on the empty shallow cast-iron pan and separate irregular 1 mm Wagyu slices, tofu, napa cabbage, shiitake, enoki, long onion and shirataki around it. One cropped hand tilts a small ceramic pitcher and pours a controlled stream of dark sweet-savoury sauce into the pan, then withdraws out of frame. End with a shallow glossy pool, not a full soup.", "Cut to a 70mm overhead insert. A few paper-thin Wagyu slices settle naturally into the shallow sauce, folded at their soft edges. They remain pink-red and translucent at the starting moment and no vegetables are moved. End as the slices begin to warm in the pan.", "Cut to a 65mm side close shot. The same 1 mm Wagyu slices develop delicate edge curls and a thin cooked sheen while the sauce clings in a shallow layer. No thick slabs or exaggerated white marbling. The burner flame stays stable. End with the beef ready for ingredients."],
            ["Locked 55mm pan-height shot. Begin with the thin glossy Wagyu at one side of the shallow pan. Tofu and shiitake sit in the remaining sauce in clean distinct zones; no person or hand is visible.", "Cut to an 80mm close insert. Napa cabbage, long onion, enoki and shirataki settle in around the beef, then the sauce makes a gentle shallow simmer. No ingredient splashes or floats. End with the shiitake and fully cooked thin folded Wagyu surfaces glossy.", "Cut to a 65mm medium close shot. One small fully cooked Wagyu ribbon rests above the clear brown glaze on the pan edge, showing real delicate layers, chestnut-brown colour all the way through and a tender curl with no pink centre. End steady for the finishing hero."],
            ["Locked 50mm three-quarter pan shot. Begin on settled thin Wagyu, tofu, mushrooms, napa cabbage, long onion and shirataki in shallow warishita. One cropped hand holds a small ladle and adds one spoonful of sauce at the pan edge, then withdraws, leaving the food untouched.", "Cut to an 85mm macro texture insert. Steam lifts from the naturally folded thin Wagyu and shiitake while the reduced soy-mirin glaze catches warm light. Keep the sauce thin and clear, not cloudy or excessive. End on believable beef texture.", "Cut to a calm 60mm final hero. The pan stays still: a few loosely folded Wagyu ribbons sit in their sauce with vegetables and tofu in distinct sections. No utensil lift and no human visible. End on the complete classic sukiyaki pan."],
        ],
    },
    {
        "slug": "green_pepper_chicken_breast_stir_fry", "title": "Green Pepper Chicken Breast Stir-Fry", "cn": "青椒炒鸡胸肉", "asset_dir": "43_green_pepper_chicken_breast_stir_fry",
        "scene": "a clean contemporary Chinese wok kitchen with pale concrete counter, sage-green tiled splashback, black carbon-steel wok over a blue gas flame and strong daylight from the left",
        "food": "tender unbreaded irregular thin cross-grain chicken-breast slices of naturally varied sizes, crisp medium-cut bright-green bell-pepper chunks, garlic, ginger and a light glossy savoury sauce",
        "logic": "Cut green bell pepper into 3 cm irregular medium diamond-shaped chunks, never thin strips. Slice chicken breast thinly across the grain into intentionally varied 2 to 5 cm tapered pieces—some narrow and some wider, with irregular natural edges—so it never reads as identical copied pieces. It must remain visibly plain chicken with no breadcrumb, flour, batter, crust or deep-fried texture. Stir-fry the pepper chunks first until just softened with light browning, add garlic and ginger briefly, then chicken until opaque; finish with a light sauce and toss only until glazed.",
        "sources": [("AP / Milk Street chicken and bell pepper stir-fry", "https://apnews.com/article/chicken-stirfry-recipe-milk-street-7f8c58cb2825d5c25298aeaa878acdec", "先炒甜椒至软并轻微上色，再加入蒜姜；鸡胸肉横切薄片并炒至完全不透明，最后加入酱汁略收。")],
        "states": {
            "scene_anchor": "Vertical no-person wok-kitchen opening. On pale concrete counter are plain unbreaded thin cross-grain chicken-breast slices of visibly varied 2 to 5 cm natural tapered shapes, vivid green bell pepper cut into 3 cm irregular medium diamond-shaped chunks, minced garlic, grated ginger and a small bowl of light brown sauce. A black carbon-steel wok heats over a blue flame; the exact AGO sign from Image 1 is a small physical card far back on the counter.",
            "prep_state": "Top three-quarter no-person layout: plain chicken breast sliced with deliberately varied natural widths and tapered irregular ends, visible natural muscle grain, medium green bell-pepper chunks, garlic, ginger and a small bowl of light soy sauce. Carbon-steel wok is dry and heating at rear; no people or faces. No breadcrumb, flour, batter or fried coating anywhere.",
            "cook_state": "Close no-person wok image: opaque, tender, plain chicken-breast slices of mixed natural shapes and thicknesses sit with bright green 3 cm pepper chunks, garlic and ginger. A few chicken pieces carry gentle pale-gold edge colour while others remain lighter, so the dish has real wok variation. Sauce is light and glossy, never a dark heavy stew. Chicken is stir-fried, not breaded, battered, deep-fried or crunchy.",
            "hero_state": "Final no-person plated hero: an intentionally irregular mix of tender glossy unbreaded chicken-breast pieces—varied 2 to 5 cm tapered slices, different widths, occasional pale-gold wok-kissed edges—sits with bright medium green pepper chunks on a white oval plate. A light sauce sheen and sparse scallion; no rice mound, no extra meats, no people, no breadcrumb or fried crust.",
        },
        "titles": ["Chicken and green pepper prep", "Fast wok transformation", "Glossy plated stir-fry"],
        "shots": [
            ["Locked 45mm high three-quarter counter shot. Begin on plain unbreaded thin cross-grain chicken slices of clearly varied taper and width, bright green 3 cm pepper chunks, garlic, ginger and a small bowl of light sauce. The ingredients and hot black wok are static; no person or hand is visible. End with the medium pepper cut and non-uniform chicken shapes clearly readable.", "Cut to a 70mm wok-height insert. Medium pepper chunks are already in shimmering oil and spread across the wok surface. The wok remains stable over blue flame; no chicken enters yet. End with peppers bright green and starting to soften.", "Cut to a 65mm close shot. Pepper chunks cook with minced garlic and ginger, producing a light glossy surface rather than charred or soggy vegetables. End with the aromatics fragrant-looking and the medium-cut peppers crisp."],
            ["Locked 55mm wok shot. Begin with medium pepper chunks and aromatics at one side. One cropped hand tips a plate and slides the thin plain chicken-breast slices of varied size into the empty side of the wok, then withdraws, keeping the raw-to-cooked transition understandable.", "Cut to an 80mm close insert. Chicken changes to opaque white with a few gentle pale-gold edges while the pepper chunks remain vivid green. Keep varied natural widths, tapered ends and uneven sear, never identical copied pieces. Chicken retains smooth natural meat texture: no bread crumb, flour, batter, deep-frying, crisp crust or thick sauce. End with chicken and peppers separate but cooked.", "Cut to a 65mm pan-side shot. Light savoury sauce appears once around the wok edge and lightly coats chicken and pepper chunks. End on a thin glossy coating clinging to both ingredients."],
            ["Locked 50mm three-quarter wok hero. Begin with fully opaque tender unbreaded chicken pieces of varied natural size and a few pale-gold wok-kissed edges, plus bright medium pepper chunks in the glossy wok. Ingredients settle naturally with no person or hand visible.", "Cut to an 85mm macro insert. Thin sauce glazes naturally varied smooth chicken pieces and medium pepper chunks with visible garlic and ginger, while a small controlled steam plume rises. Keep the dish light, fresh and not soupy. End on crisp pepper and tender chicken texture.", "Cut to a calm 60mm plate hero. A white oval plate already holds the finished irregular stir-fry: assorted tapered chicken pieces mixed naturally with pepper chunks, not evenly repeated or symmetrical, and a few sliced scallions. No utensil or human is visible. End with the finished stir-fry centred and sharp."],
        ],
    },
    {
        "slug": "silky_steamed_egg_custard", "title": "Silky Steamed Egg Custard", "cn": "生抽温水蒸鸡蛋", "asset_dir": "44_silky_steamed_egg_custard",
        "scene": "a quiet Cantonese breakfast kitchen with creamy limewashed plaster, a honey-coloured travertine counter, woven rattan cabinet fronts, a bamboo steamer over a low pot, a white heatproof bowl and soft early-morning side light",
        "food": "a smooth pale-golden Chinese steamed egg custard made from whisked egg, warm water and light soy sauce, finished with a few drops of sesame oil and scallion",
        "logic": "Whisk eggs with light soy sauce, slowly add warm water while stirring, strain and remove foam for a smooth texture, cover the heatproof bowl and steam gently. Finish the set custard with light soy sauce, sesame oil and scallion; it must have a mirror-smooth surface without bubbles.",
        "sources": [("Panasonic Steamed Eggs", "https://www.panasonic.hk/usm.ashx/e/7zt1rwYXAiWEX1X3Hkyy9Cs~wG~6ihEZ25GRDuBb2ZhJMTaZa5sNp5p_ghu20gGLi5Jr07TSqzOBTH6JMPLdl1NtOBa44i8hy9Tjiau-hyaFU5TGuS26lzrmR28O4lq6GhlTiieNI1_IX7Mpqht1-Xu7SjfcFO82CHV53S6YO5yZUcQSEpMRX6dvBt3ZeTgD/F000BCS80HP_NUSC280W_Cookbook_EN-20221123_small-size.pdf", "3 个鸡蛋加入约 40°C 温水和生抽，搅拌过滤后覆盖并蒸制，出锅滴香油。")],
        "states": {
            "scene_anchor": "Vertical no-person breakfast-kitchen opening. Three cracked eggs in a clear bowl, a small white pitcher of warm water, light soy sauce in a tiny ceramic pourer, fine sieve and white heatproof bowl sit on honey-coloured travertine beneath creamy limewashed plaster and rattan cabinets. A bamboo steamer warms over a low pot. The exact AGO sign from Image 1 is a small physical card far back on the counter.",
            "prep_state": "Top three-quarter no-person preparation image in the Cantonese breakfast kitchen: pale golden egg mixture is being strained through a fine sieve into a white heatproof bowl; warm water pitcher and light soy sauce pourer remain visible on honey-coloured travertine. Surface is bubble-free and smooth; no face or body.",
            "cook_state": "Close no-person steam-state image in the Cantonese breakfast kitchen: a white covered heatproof bowl sits inside bamboo steamer above gentle steam. The lid is set to one side, revealing a fully set, smooth pale-golden egg custard with no bubbles or cracks. Creamy plaster and rattan details remain softly behind it.",
            "hero_state": "Final no-person breakfast hero in the Cantonese breakfast kitchen: silky mirror-smooth steamed egg custard in white bowl, finished with a small spoonful of light soy sauce, sesame oil sheen and finely sliced scallion. White porcelain spoon rests beside it on honey-coloured travertine; no people or other dishes.",
        },
        "titles": ["Egg, warm-water and soy setup", "Strain, cover and steam", "Silky custard finish"],
        "shots": [
            ["Locked 45mm high three-quarter counter shot. Begin on cracked eggs in a clear bowl, warm water pitcher, light soy sauce pourer, fine sieve and white heatproof bowl. A cropped anonymous hand whisks the eggs once until the yolk and white combine, then leaves the whisk still.", "Cut to a 70mm close side insert. Warm water pours in a single thin stream while the whisk makes one slow circle, keeping the liquid pale golden and even. The light soy sauce pourer remains in view. End with smooth diluted egg mixture.", "Cut to a 65mm top three-quarter shot. Light soy sauce is added in one small pour and the mixture is guided toward the fine sieve. No foam, other seasonings or people enter. End ready to strain."],
            ["Locked 55mm close shot. Begin on the fine sieve over the white heatproof bowl. Pale egg mixture passes through in one smooth pour, leaving a bubble-free surface in the bowl. The sieve lifts away once and the surface stays level.", "Cut to an 80mm bowl-height insert. A lid or heat-safe cover settles over the bowl in one calm downward motion, with no water droplets inside. End on the covered bowl ready for gentle steam.", "Cut to a medium steamer shot. The covered bowl is placed inside a bamboo steamer above gentle steam; the lid closes once. Camera stays fixed, ending on the closed steamer and soft escaping vapour."],
            ["Locked 50mm steamer shot. Begin on the closed bamboo lid as soft steam rises. Anonymous hands lift the lid once and reveal a fully set, smooth pale-golden custard with a mirror-like surface, then hold the lid away.", "Cut to an 85mm macro insert. A small spoon drizzles light soy sauce and a few drops of sesame oil across the custard once, followed by a sparse scatter of fine scallion. Surface remains unbroken except the gentle sauce sheen.", "Cut to a calm 60mm final bowl hero. White porcelain spoon rests beside the finished custard while steam fades softly behind it. End with the silky surface and scallion sharp, no other breakfast dishes entering frame."],
        ],
    },
]

def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")

def reference_prompt(p: dict, kind: str) -> str:
    return f"""Use case: ads-marketing
Asset type: no-person MiniMax H3 R2V reference image for a vertical cooking commercial
Primary request: create the {kind.replace('_', ' ')} reference for {p['title']}.
Input image: Image 1 is the approved ASIAN GROCER ONLINE / powered by UMALL tabletop sign artwork; preserve it only where the scene asks for a physical tabletop card.
Scene/backdrop: {p['scene']}.
Subject: {p['states'][kind]}
Food authority: {p['food']}.
Style/medium: high-end photorealistic food-commercial still with real cookware, appetising texture and physically plausible steam.
Composition/framing: vertical 9:16, one calm food action or still state, no face, torso or visible person.
Lighting/mood: purposeful soft natural light, coherent direction and clean highlights.
Constraints: {p['logic']} No visible face, body, portrait or anonymous person; only cropped unidentifiable hands at the edge are allowed where action is indispensable. No fake labels, captions, price graphics, watermarks or invented products.
Avoid: western cuisine substitution, warped utensils, extra fingers, melted food, excessive steam, clutter and fake app interface.
"""

def h3_prompt(p: dict, clip_no: int) -> str:
    refs = {1: ["the no-person scene and dish-identity anchor", "the prepared state", "the cooking-state target", "the finished serving-state target"], 2: ["the exact final frame of clip 01", "the no-person scene and dish-identity anchor", "the prepared state", "the cooking-state target", "the finished serving-state target"], 3: ["the exact final frame of clip 02", "the no-person scene and dish-identity anchor", "the cooking-state target", "the finished serving-state target"]}[clip_no]
    definitions = "\n".join(f"<Picture {i}> is {value}." for i, value in enumerate(refs, 1))
    cut_times = {1: "", 2: " At 00:01.600,", 3: " At 00:03.400,"}
    shot_lines = []
    for i, text in enumerate(p["shots"][clip_no - 1], 1):
        for prefix in ("Locked ", "Cut to "):
            text = text.removeprefix(prefix)
        shot_lines.append(f"[Shot {i}]{cut_times[i]} {text}")
    shots = "\n\n".join(shot_lines)
    location = 1 if clip_no == 1 else 2
    food_ref = 2 if clip_no == 1 else 3 if clip_no == 2 else 3
    return f"""subject_definitions:
<Subject 1> is the dish and its essential cookware only. No human person is a subject; when an action requires it, show only cropped unidentifiable hands at a frame edge.
{definitions}

summary:
reference generation. A five-second vertical no-person cooking commercial, clip {clip_no} of three, for {p['title']}. The clip advances one true food state while retaining the same kitchen materials, cookware and dish identity from the local reference stack.

retention_analysis:
<Subject 1>: fully_preserved. Food, cookware and anonymous edge-of-frame action remain physically coherent with no visible person.
<Picture {location}>: fully_preserved. It anchors the unique kitchen, counter, vessel, light direction and no-person visual treatment.
<Picture {food_ref}>: fully_preserved. It preserves the exact ingredients, cooking state, texture and serving logic.
Food sequence: fully_preserved. {p['logic']}
Human visibility: fully_preserved. Never reveal a face, head, torso, arms, reflection or portrait.

detailed_description:
{shots}

[Continuity guard] Treat <Picture {location}> as the only spatial and lighting bible. Keep counter material, wall treatment, pot or pan, burner, bowl and tableware identical throughout the clip. Treat <Picture {food_ref}> as the food-state authority: preserve its ingredients, cut size, colour, sheen and cooking stage exactly. No food should appear, disappear, melt, float or transform without the named movement. If a hand is required, crop it at the wrist and keep it at the lower edge only; it has no identity, clothing, face or body. Hold each endpoint cleanly for the next clip to inherit.

[Frame discipline] Keep the food as the central subject in every frame, with one vessel and one action clearly readable. Do not introduce decorative props that obscure the ingredient state. Maintain believable gravity, liquid levels, utensil contact and heat behaviour. The camera must never reveal a person through reflections in cookware, glass, windows or polished surfaces. Preserve clean negative space and avoid sudden changes in time of day, colour temperature or table layout.

Across all shots retain {p['food']}. Use cuts only at 00:01.600 and 00:03.400, with one physical action per shot and a stable camera. Keep cookware rigid, steam controlled and food texture visibly coherent at every precise moment. Do not add people, faces, bodies, captions, subtitles, title cards, price graphics, watermarks, fake labels, shopping UI, camera shake, scene jumps, warped tools, extra fingers, different cuisine or different dish identity. Avoid blank product-free endings and excessive close-ups of hands.

overall_soundscape:
Natural kitchen ambience only: quiet flame, water simmer, gentle wok sizzle, lid movement, chopstick contact, steamer vapour and ceramic plating as physically appropriate. No dialogue.

non_diegetic_music:
Restrained modern food-commercial instrumental with a clean, warm three-shot cadence and no vocals.
"""

def sequence(p: dict) -> dict:
    base = f"../sequence_outputs/{p['slug']}/preproduction"
    assets = f"../outputs/reference_assets/{p['asset_dir']}/generated"
    refs = [f"{assets}/{p['slug']}_{kind}-1.png" for kind in ["scene_anchor", "prep_state", "cook_state", "hero_state"]]
    return {"sequence_id": f"{p['slug']}_3x5_native1080", "server": "http://127.0.0.1:8189", "defaults": {"mode": "r2v", "width": 1088, "height": 1920, "duration": 5.0, "steps": 8, "turbo": True, "turbo_low_vram": True, "no_audio": True, "ref_image_size": "match", "poll": 10, "timeout": 10800}, "clips": [{"id": "clip-01-prep-hook", "prompt_file": f"{base}/h3_prompts/clip_01_ref2va.md", "ref_images": refs, "seed": 202608250101, "prefix": f"sequence/{p['slug']}_3x5_native1080/clip-01"}, {"id": "clip-02-cook-proof", "prompt_file": f"{base}/h3_prompts/clip_02_ref2va.md", "use_previous_last_frame_as_ref": True, "ref_images": refs, "seed": 202608250102, "prefix": f"sequence/{p['slug']}_3x5_native1080/clip-02"}, {"id": "clip-03-serving-hero", "prompt_file": f"{base}/h3_prompts/clip_03_ref2va.md", "use_previous_last_frame_as_ref": True, "ref_images": [refs[0], refs[2], refs[3]], "seed": 202608250103, "prefix": f"sequence/{p['slug']}_3x5_native1080/clip-03"}], "final": {"filename": f"{p['slug']}_3x5_native_1080x1920.mp4", "concat_mode": "both", "crop": {"width": 1080, "height": 1920, "x": 4, "y": 0}, "crf": 16, "preset": "medium", "keep_audio": False}}

def package(p: dict) -> None:
    pre = ROOT / "sequence_outputs" / p["slug"] / "preproduction"
    write(pre / "recipe_bible.md", f"""# {p['title']} — No-Person Production Bible

## Food logic

{p['logic']}

## Visual rule

No visible person. The commercial uses ingredients, cookware, steam and only cropped unidentifiable hands when a physical action must be shown. The opening reference uses the physical tabletop sign; H3 prompts do not name it.

## States

1. Opening — {p['states']['scene_anchor']}
2. Prep — {p['states']['prep_state']}
3. Cooking — {p['states']['cook_state']}
4. Hero — {p['states']['hero_state']}
""")
    write(pre / "recipe_sources.md", "# Recipe Sources\n\n" + "\n".join(f"- [{name}]({url}) — {note}" for name, url, note in p["sources"]))
    for kind in ["scene_anchor", "prep_state", "cook_state", "hero_state"]:
        write(pre / "reference_prompts" / f"{kind}.md", reference_prompt(p, kind))
    lines = [f"# {p['title']} — No-Person 3×5s Storyboard", "", "Three independent 5-second H3 R2V clips. No people appear; only cropped anonymous hands may perform indispensable cooking actions.", ""]
    for n, (title, shots) in enumerate(zip(p["titles"], p["shots"]), 1):
        lines += [f"## Clip {n}: {title}", "", *[f"- {shot}" for shot in shots], ""]
    write(pre / "storyboard.md", "\n".join(lines))
    for n in range(1, 4):
        write(pre / "h3_prompts" / f"clip_{n:02d}_ref2va.md", h3_prompt(p, n))
    manifest = {"product": p["title"], "dish_identity": p["food"], "physical_sign_reference": "../../../company_logo/AGO.png", "assets": {kind: f"outputs/reference_assets/{p['asset_dir']}/generated/{p['slug']}_{kind}-1.png" for kind in ["scene_anchor", "prep_state", "cook_state", "hero_state"]}, "generation_order": ["scene_anchor", "prep_state", "cook_state", "hero_state"]}
    write(pre / "reference_manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    write(SEQUENCES / f"{p['slug']}_3x5_1080.json", json.dumps(sequence(p), ensure_ascii=False, indent=2))

def main() -> None:
    for product in PRODUCTS:
        package(product)
        print(f"prepared {product['slug']}")

if __name__ == "__main__":
    main()
