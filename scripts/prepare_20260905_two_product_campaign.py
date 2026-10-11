#!/usr/bin/env python3
"""Create two with-person MiniMax H3 3x5s reference and prompt packages:
outdoor camping lamb skewers, and an office-desk instant beauty-congee sachet.

Uses the clip1-leak-fixed pattern from prepare_20260830_six_recipe_campaign.py
(ref_kinds_for / food_line_for / food_sequence_line_for) - see
CURRENT_WORKFLOW.md section 4c - adapted for a WITH-PERSON cast instead of a
no-person campaign. Because a real person is on screen throughout, section
5a-0's hand question does not apply here: hands are simply normal.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEQUENCES = ROOT / "sequences"

PRODUCTS = [
    {
        "slug": "bbq_lamb_camping",
        "title": "户外露营羊肉串",
        "en": "Outdoor Camping Lamb Skewers",
        "asset_dir": "54_bbq_lamb_camping",
        "source_products": ["outputs/reference_assets/54_bbq_lamb_camping/source_products/bbq_lamb_camping_source.png"],
        "talent": "a no-face fictional Asian man in his late twenties, relaxed camp-casual olive utility jacket with sleeves pushed up over a plain grey tee - filmed only from the shoulders down or from behind, at a camera height that keeps his head and face above or outside every frame; his build, jacket, forearms and hands are the only identity markers carried across every clip",
        "scene": "a cozy dusk campsite beside a small clear forest stream, one canvas tent glowing softly behind, tall pines, a warm string of camp lights, and a portable folding charcoal BBQ grill set on a flat rock ledge with a steady bed of glowing charcoal",
        "food": "the supplied raw lamb skewers - thin bamboo skewers threading alternating 3 cm cubes of deep-red lean lamb and white marbled fat, seven to eight pieces per skewer - grilled directly over glowing charcoal until the fat renders glossy and every surface turns an even sauce-brown with light char at a few edges, cooked through with no pink centre, never blackened, dried out, or confused with paler pork or coarser dark-grained beef",
        "logic": (
            "Thread alternating 3 cm lean-lamb cubes and white fat cubes onto thin skewers, "
            "seven to eight pieces each. Lay the skewers directly over glowing charcoal with no "
            "open flame, turning every two to three minutes until each side reaches an even "
            "sauce-brown colour. Dust with cumin and chilli flakes while turning near the end so "
            "the seasoning toasts onto the surface rather than burning. The fat should render to "
            "a glossy sheen and the lean meat should read fully opaque brown throughout with no "
            "pink centre, consistent with USDA guidance that whole-muscle lamb reach a minimum "
            "145 degF (63 degC) internal temperature, taken further to a fully opaque well-done "
            "finish for pieces this small."
        ),
        "clip2_near_finished": False,
        "sources": [
            ("烤羊肉串的做法——新疆味道", "https://home.meishichina.com/recipe-107447.html", "羊肉切3厘米见方、肥瘦相间穿串，无明火炭火烤制，肉色转酱黄色后翻面，烤制中撒孜然面和辣椒面。"),
            ("USDA FSIS: Lamb From Farm to Table", "https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/meat-catfish/lamb-farm-table", "整块羊肉（如烤串所用的小块）安全最低中心温度为145°F（63°C），静置至少3分钟。"),
        ],
        "states": {
            "character_scene": "Vertical dusk opening at the campsite, camera held at chest height and tilted slightly down so the cook's head and face stay above the top frame edge throughout; only his jacket, shoulders, forearms and hands are in view. He stands at the portable folding charcoal grill on the flat rock ledge; behind him a canvas tent glows softly and a narrow clear stream catches the last blue light through the pines, with warm string lights strung overhead. On the grill's side board rest the supplied raw lamb skewers exactly as photographed: thin bamboo skewers each threading alternating deep-red lean lamb cubes and white marbled fat cubes, laid in a neat row, beside small tins of cumin and chilli flakes. A small physical AGO tabletop card sits near the board's far edge, secondary and slightly out of focus. The charcoal bed glows steady with no open flame; the grate itself is still empty.",
            "prep_state": "Top three-quarter close-up on the raw skewer row on the wood board, framed low enough that only the cook's sleeve, forearm and hand enter from the side of frame to steady one skewer - his head and face never enter the shot. Each thin bamboo skewer threads seven to eight alternating cubes of deep-red lean lamb and white marbled fat at an even 3 cm size, clearly distinct from paler pink pork or coarser dark beef. Small tins of cumin and chilli flakes sit beside the board. No fat is rendered yet; every surface is still raw and matte.",
            "cook_state": "Close vessel-height shot at the charcoal grill, framed at grate height so only the cook's sleeve, forearm and hand enter frame to turn a skewer - his head and face stay out of the shot throughout. Several skewers lie across the glowing grate; the turned side shows an even sauce-brown colour developing with a few light char edges, while the untouched side is still a shade lighter. A faint dusting of cumin and chilli clings to the browning surface, and the rendering fat gives a single small glossy flare where it meets the coals. Tent and dark pines blur softly behind, embers glowing red beneath the grate.",
            "hero_state": "Final camp hero, camera held at chest height so the cook's jacket, shoulders and one hand setting the plate down are visible while his head and face stay above the frame edge throughout. The skewers rest on a small tin plate beside the grill, every surface an even deep sauce-brown with light char at a few edges and a glossy rendered sheen, cooked through with no pink centre. The tent glows, the stream catches warm light, and the string lights sit soft behind him - a relaxed, comfortable outdoor payoff.",
        },
        "titles": ["Campsite skewer setup", "Charcoal sear and turn", "Fire-charred camp hero"],
        "shots": [
            [
                "A locked 40mm high three-quarter shot, camera height at the cook's chest so his head and face stay above the top frame edge, begins on his jacket, shoulders and the raw skewer row on the side board, the tent glowing and the stream catching light behind him. The charcoal bed glows steady with no open flame; the grate is still empty. A small, slow 4 cm push-in toward the board. End with every raw skewer readable and the grate bare.",
                "Cut to a 70mm board-height insert, framed low so only sleeve, forearm and hand enter frame. One hand lifts a single raw skewer from the board and turns it slightly, showing the alternating lean and fat cubes clearly, then holds it steady above the grate. End with the skewer poised just above the coals, still raw.",
                "Cut to a 60mm grill-height medium close shot, framed at grate height so only sleeve, forearm and hand are in view. The skewers are laid one at a time onto the grate in a neat row over the glowing charcoal. End with every skewer placed flat across the grate, fat still pale and no colour change yet.",
            ],
            [
                "A locked 55mm grill-height shot, framed at grate height so only sleeve, forearm and hand are in view, begins on the row of raw skewers already resting on the glowing grate from the prior clip. One hand turns the nearest skewer once; the turned side shows the first even sauce-brown colour beginning while the far side stays lighter. End with one skewer clearly ahead of the others in colour.",
                "Cut to an 80mm close insert, framed low so only sleeve, forearm and fingers are in view. Two fingers pinch cumin and chilli flakes from their tins and dust them once across the turning skewers. A single small glossy flare catches where rendering fat meets the coals, then settles. End with the seasoning visibly clinging to the browning surface.",
                "Cut to a 65mm side medium close shot, framed at grate height so only sleeve, forearm and hand are in view. Each skewer is turned to its second side; every surface now reads an even sauce-brown with light char at a few edges, fat glossy and rendered. End with the skewers still on the grate, fully coloured but not yet lifted.",
            ],
            [
                "A locked 50mm grill-to-plate shot, framed at grate height so only sleeve, forearm and hand are in view, begins on the fully coloured skewers still on the grate from the prior clip. One hand lifts the skewers together and sets them onto a small tin plate beside the fire. End with the skewers resting on the plate, off the grate.",
                "Cut to an 85mm macro texture insert. Warm ember light catches the glossy rendered fat, the deep sauce-brown lean meat and the faint cumin dusting on the plated skewers. Keep the texture readable and appetising, with no pink centre anywhere. End on crisp, believable char detail.",
                "Cut to a calm 60mm final camp hero, camera held at chest height so the cook's jacket, shoulders and one hand are visible while his head and face stay above the frame edge. The plated skewers sit beside him, the tent glowing, the stream catching warm light and the string lights soft behind him. End on a relaxed, comfortable outdoor-camping payoff.",
            ],
        ],
    },
    {
        "slug": "beauty_congee_office",
        "title": "办公室茯苓百合美苓粥",
        "en": "Poria Lily Beauty Congee, Office Breakfast",
        "asset_dir": "55_beauty_congee_office",
        "source_products": ["outputs/reference_assets/55_beauty_congee_office/source_products/beauty_congee_office_source.png"],
        "talent": "a no-face fictional Asian woman in her late twenties, business-casual blazer with sleeves pushed up over a simple top - filmed only from the shoulders down or from behind, at a camera height that keeps her head and face above or outside every frame; her build, blazer, forearms and hands are the only identity markers carried across every clip",
        "scene": "a bright modern open-plan office desk nook with a slim laptop, a small potted succulent, warm morning window light, a soft grey desk mat, a white ceramic mug and spoon, and an electric kettle within reach on a side shelf",
        "food": "the supplied 五仁本草 茯苓百合美苓粥 (Poria Lily Beauty Congee) instant sachet - a pale ivory grain-and-fungus powder that becomes a smooth, glossy, creamy off-white congee-like drink with a few visible pale flecks of white fungus and lily bulb once stirred with hot water, thicker than milk and never a thin watery liquid",
        "logic": (
            "Tear open one single-serve sachet of the pale ivory powder blend (poria, lily bulb, "
            "white fungus, yam, lotus seed, job's tears, soybean and rice, per the supplied "
            "packaging) and pour its contents into an empty mug. Pour hot water in a controlled "
            "stream over the powder, then stir in slow circles until every dry lump dissolves "
            "and the mixture turns smooth, glossy and evenly pale ivory, thick enough to coat "
            "the back of a spoon. This is a reconstituted instant product, not a simmered "
            "congee: no stovetop or boiling step is shown."
        ),
        "clip2_near_finished": True,
        "sources": [
            ("Supplied product packaging (五仁本草 茯苓百合美苓粥)", "outputs/reference_assets/55_beauty_congee_office/source_products/beauty_congee_office_source.png", "包装标注精选8大白养食材：茯苓、百合、银耳、山药、莲子、薏米、黄豆、亚米；净含量960g（30条），冲调谷物制品，标注需用热水冲调。"),
        ],
        "states": {
            "character_scene": "Vertical morning opening at the office desk, camera held at chest height and tilted slightly down so the office worker's head and face stay above the top frame edge throughout; only her blazer, shoulders, forearms and hands are in view. She sits at her bright desk with her laptop open; in front of her stands the supplied product box (五仁本草 茯苓百合美苓粥) exactly as photographed, one individual sachet resting beside it, an empty white ceramic mug and a spoon. The electric kettle warms on the side shelf behind. A small physical AGO tabletop card sits near the box's far corner, secondary and slightly out of focus. The box's large title calligraphy and red badges stay legible; its small ingredient list, nutrition panel and barcode stay softly out of focus, never sharpened or invented.",
            "prep_state": "Top three-quarter close-up on the desk, framed low enough that only her sleeve, forearm and hand enter frame - her head and face never enter the shot. One sachet is already torn open at its top corner, held upright just above the empty mug, the pale ivory powder visible inside the opening. The spoon and the still-sealed box remain beside the mug. No powder has entered the mug yet.",
            "cook_state": "Close mug-height shot, framed low so only sleeve, forearm and hand pouring from the kettle are in view - her head and face stay out of the shot throughout. A small heap of pale ivory powder sits at the bottom of the mug, and hot water pours in from the kettle in a controlled stream over it, with a soft plume of steam rising. The powder begins to dissolve into a pale swirling cloud where the water meets it.",
            "hero_state": "Final desk hero, camera held at chest height so her blazer, shoulders and one hand resting near the mug are visible while her head and face stay above the frame edge throughout. The mug holds a smooth, glossy, creamy off-white congee-like drink with a few visible pale flecks of white fungus and lily bulb, thick enough to coat the spoon resting against its rim. The laptop screen glow and small succulent sit softly blurred behind in the warm morning light - a comfortable, calm office-breakfast payoff.",
        },
        "titles": ["Desk sachet opening", "Hot water bloom", "Morning sip payoff"],
        "shots": [
            [
                "A locked 40mm high three-quarter desk shot, camera height at her chest so her head and face stay above the top frame edge, begins on her blazer, shoulders, the standing product box, one sachet, the empty mug and spoon laid out, the kettle warming on the shelf behind her. A small, slow 4 cm push-in toward the desk items. End with every item readable and the mug still empty.",
                "Cut to a 70mm desk-height insert, framed low so only sleeve, forearm and hand enter frame. One hand picks up the sachet and tears open its top corner in one clean motion. End with the sachet open and the pale ivory powder visible inside.",
                "Cut to a 60mm mug-height medium close shot, framed low so only sleeve, forearm and hand are in view. The open sachet tips and the pale ivory powder pours in a steady stream into the empty mug. End with the dry powder settled in the mug and the empty sachet set aside; no water has been added yet.",
            ],
            [
                "A locked 55mm desk-height shot, framed low so only sleeve, forearm and hand are in view, begins on the mug already holding the dry pale powder from the prior clip. One hand lifts the kettle and tilts it so hot water pours in a controlled stream into the mug, a soft plume of steam rising. End with the water fully poured and the powder beginning to dissolve.",
                "Cut to an 80mm mug-height close insert, framed low so only sleeve, forearm and hand are in view. The spoon in her other hand stirs the mixture in slow, even circles; the texture turns from grainy to smooth as the pale ivory colour becomes even throughout. End with no dry lumps remaining.",
                "Cut to a 65mm side medium close shot, framed low so only sleeve, forearm and hand are in view. The stirring completes and the drink is smooth, glossy and evenly pale ivory with a few visible flecks of white fungus and lily bulb; the spoon lifts and rests against the mug's rim. End with the finished drink readable and the mug steady on the desk.",
            ],
            [
                "A locked 50mm desk-height shot, framed low so only sleeve, forearm and hand are in view, begins on the finished mug from the prior clip. One hand sets the spoon down beside the mug and lifts the mug slightly off the desk. End with the mug held just above the desk, steady.",
                "Cut to an 85mm macro texture insert. Gentle steam rises off the creamy pale surface as the laptop screen glow and small succulent blur softly behind. Keep the texture glossy and appetising, never watery or grainy. End on crisp, believable surface detail.",
                "Cut to a calm 60mm final desk hero, camera held at chest height so her blazer, shoulders and the hand holding the mug are visible while her head and face stay above the frame edge. The desk sits fully composed around her with the box, the empty sachet, the laptop and the succulent in warm morning light. End on a comfortable, unhurried office-breakfast payoff.",
            ],
        ],
    },
]


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


# Per-kind framing distance, same principle as prepare_20260830_six_recipe_campaign.py's
# COMPOSITION_BY_KIND: without an explicit distance/angle per kind, the model defaults to
# one wide shot regardless of what the reference is actually for.
COMPOSITION_BY_KIND = {
    "character_scene": "vertical 9:16, medium shot from a slightly high three-quarter angle - the widest shot in this set. Cast, location and every supplied product/prop stay legible.",
    "prep_state": "vertical 9:16, close-up from a high three-quarter angle. The product/ingredient state fills most of the frame and is clearly legible.",
    "cook_state": "vertical 9:16, close-up at working height looking slightly down. The transformation in progress fills most of the frame and stays legible.",
    "hero_state": "vertical 9:16, close hero angle from about 30 degrees above. The finished product and its vessel fill most of the frame; texture and gloss are the subject.",
}


def reference_prompt(p: dict, kind: str) -> str:
    source_line = ""
    if kind == "character_scene" and p["source_products"]:
        source_line = "Image 2 is the approved supplied product reference. Preserve it faithfully only where the scene specifies it: never redraw, relabel, translate, substitute or invent it. "
    return f"""Use case: ads-marketing
Asset type: with-person MiniMax H3 R2V reference image for a vertical commercial
Primary request: create the {kind.replace('_', ' ')} reference for {p['en']}.
Input image: Image 1 is the approved ASIAN GROCER ONLINE / powered by UMALL tabletop sign artwork; preserve it only where the scene asks for a physical tabletop card, always secondary and out of focus. {source_line}
Cast: {p['talent']}.
Scene/backdrop: {p['scene']}.
Subject: {p['states'][kind]}
Product authority: {p['food']}.
Style/medium: premium photorealistic commercial still, genuine props, credible texture, physically plausible heat, steam or liquid behaviour.
Composition/framing: {COMPOSITION_BY_KIND[kind]} Frame the cast from the shoulders down or from behind, at a camera height that keeps the head and face above or outside the frame at all times.
Lighting/mood: precise directional light, coherent shadows, clean high-end highlights.
Constraints: {p['logic']} No fake labels, invented captions, price graphics, watermarks, invented products, or unrelated dishes/props from another campaign.
Avoid: a revealed or identifiable face, warped props, melted or duplicated product, excessive steam, clutter, fake app interface, and unreadable or invented small print on any packaging.
"""


REF_KIND_LABELS = {
    "character_scene": "the cast, location and product-identity anchor",
    "prep_state": "the preparation state",
    "cook_state": "the cooking or mixing state",
    "hero_state": "the finished serving-state target",
}


def ref_kinds_for(p: dict, clip_no: int) -> list[str]:
    """Same conservative default as prepare_20260830_six_recipe_campaign.py's
    ref_kinds_for(): clip 1 never receives cook_state or hero_state, so it
    cannot land on a state it has not reached yet (CURRENT_WORKFLOW.md 4c).
    """
    if clip_no == 1:
        kinds = ["character_scene", "prep_state"]
        if p.get("clip1_cooks"):
            kinds.append("cook_state")
        for excluded in p.get("clip1_exclude", ()):
            if excluded in kinds:
                kinds.remove(excluded)
        return kinds
    if clip_no == 2:
        kinds = ["character_scene", "prep_state", "cook_state"]
        if p.get("clip2_near_finished"):
            kinds.append("hero_state")
        return kinds
    return ["character_scene", "cook_state", "hero_state"]


def food_line_for(p: dict, clip_no: int) -> str:
    if clip_no == 3:
        return f"Across all shots retain {p['food']}."
    interim = p.get("clip_states", {}).get(clip_no)
    if interim:
        return (f"Across all shots this clip stays at: {interim} Do not let this "
                f"clip land on, cut to, or preview the finished {p['en']}; that "
                f"state belongs only to the later clip(s).")
    return (f"This clip has not yet reached the finished {p['en']}. Show only the "
            f"product and process state described in the shots above for this "
            f"clip; do not let this clip's final frame resemble, cut to, or "
            f"preview the completed, finished result.")


def food_sequence_line_for(p: dict, clip_no: int) -> str:
    if clip_no == 3:
        return p["logic"]
    interim = p.get("clip_states", {}).get(clip_no)
    if interim:
        return f"This clip covers only: {interim}"
    return (f"This clip has not yet reached the finished {p['en']}; only the "
            f"product and process state shown in this clip's own shots is "
            f"true here.")


def h3_prompt(p: dict, clip_no: int) -> str:
    kinds = ref_kinds_for(p, clip_no)
    prior = [f"the exact final frame of clip {clip_no - 1:02d}"] if clip_no > 1 else []
    refs = prior + [REF_KIND_LABELS[k] for k in kinds]
    definitions = "\n".join(f"<Picture {i}> is {value}." for i, value in enumerate(refs, 1))
    cut_times = {1: "", 2: " At 00:01.600,", 3: " At 00:03.400,"}
    shot_lines = [f"[Shot {i}]{cut_times[i]} {text}" for i, text in enumerate(p["shots"][clip_no - 1], 1)]
    spatial_ref = 1 if clip_no == 1 else 2
    food_ref = spatial_ref + 1 if spatial_ref + 1 <= len(refs) else spatial_ref
    retention_lines = [f"<Picture {spatial_ref}>: fully_preserved. It anchors the unique cast, location, counter/desk materials and light direction."]
    if food_ref != spatial_ref:
        retention_lines.append(f"<Picture {food_ref}>: fully_preserved. It preserves the exact product identity, state, colour and stage of preparation.")
    else:
        retention_lines[-1] += " It is also the product-state authority for this clip: preserve identity, state, colour and stage of preparation exactly."
    retention_block = "\n".join(retention_lines)
    if food_ref == spatial_ref:
        continuity_lead = f"Treat <Picture {spatial_ref}> as the only spatial, cast and product-state authority."
        continuity_food = "Preserve product identity, state, colour and stage exactly."
    else:
        continuity_lead = f"Treat <Picture {spatial_ref}> as the spatial and cast bible."
        continuity_food = f"Treat <Picture {food_ref}> as the product-state authority: preserve identity, state, colour and stage exactly."
    return f"""subject_definitions:
<Subject 1> is {p['talent']}, established in <Picture {spatial_ref}>.
{definitions}

summary:
reference generation. A five-second vertical commercial, clip {clip_no} of three, for {p['en']}. It advances exactly one true preparation state while retaining the same cast, location, props and product identity from the local reference stack.

retention_analysis:
<Subject 1>: fully_preserved. Same build, wardrobe, forearms and hands throughout.
{retention_block}
Food sequence: fully_preserved. {food_sequence_line_for(p, clip_no)}
Face visibility: fully_preserved. <Subject 1>'s face, head and any reflection or shadow revealing it never enter frame in any shot; only build, wardrobe, forearms and hands establish <Subject 1>.

detailed_description:
{chr(10).join(chr(10) + line for line in shot_lines)}

[Continuity guard] {continuity_lead} Keep counter/desk material, wall or backdrop treatment, and every prop identical throughout the clip. {continuity_food} No product may appear, disappear, melt, float or transform without the named movement. Keep hands anatomically correct throughout. The camera height and framing keep <Subject 1>'s face out of every shot; never tilt up or turn to reveal it. Hold each endpoint cleanly for the next clip to inherit.

[Frame discipline] Keep the product central in every frame, with one vessel and one action clearly readable. Do not introduce decorative props that obscure the product state. Maintain believable gravity, liquid level, heat, steam and condensation. Preserve clean negative space and avoid sudden changes in time of day, colour temperature or layout. The camera is rigid within each shot and every movement is small, deliberate and physically motivated.

{food_line_for(p, clip_no)} Use cuts only at 00:01.600 and 00:03.400, with one physical action per shot and stable camera. Keep props rigid, steam controlled and product texture coherent at every moment. Do not add a revealed face, captions, subtitles, title cards, price graphics, watermarks, fake or invented small print, shopping UI, camera shake, scene jumps, warped props, extra fingers, extra people, a different product, or a different location. Avoid blank endings and excessive close-ups of non-product objects.

overall_soundscape:
Natural location sound only: soft ember crackle, stream water, kettle pour, spoon-on-ceramic contact and quiet ambience as physically appropriate. No dialogue.

non_diegetic_music:
Restrained warm commercial instrumental with a clean three-shot cadence and no vocals.
"""


def sequence(p: dict) -> dict:
    base = f"../sequence_outputs/{p['slug']}/preproduction"
    assets = f"../outputs/reference_assets/{p['asset_dir']}/generated"

    def refs_for(clip_no: int) -> list[str]:
        return [f"{assets}/{p['slug']}_{kind}-1.png" for kind in ref_kinds_for(p, clip_no)]

    return {
        "sequence_id": f"{p['slug']}_3x5_native1080",
        "server": "http://127.0.0.1:8189",
        "defaults": {"mode": "r2v", "width": 1088, "height": 1920, "duration": 5.0, "steps": 8, "turbo": True, "turbo_low_vram": True, "no_audio": True, "ref_image_size": "match", "poll": 10, "timeout": 10800},
        "clips": [
            {"id": "clip-01-setup", "prompt_file": f"{base}/h3_prompts/clip_01_ref2va.md", "ref_images": refs_for(1), "seed": 202609050101, "prefix": f"sequence/{p['slug']}_3x5_native1080/clip-01"},
            {"id": "clip-02-transformation", "prompt_file": f"{base}/h3_prompts/clip_02_ref2va.md", "use_previous_last_frame_as_ref": True, "ref_images": refs_for(2), "seed": 202609050102, "prefix": f"sequence/{p['slug']}_3x5_native1080/clip-02"},
            {"id": "clip-03-hero", "prompt_file": f"{base}/h3_prompts/clip_03_ref2va.md", "use_previous_last_frame_as_ref": True, "ref_images": refs_for(3), "seed": 202609050103, "prefix": f"sequence/{p['slug']}_3x5_native1080/clip-03"},
        ],
        "final": {"filename": f"{p['slug']}_3x5_native_1080x1920.mp4", "concat_mode": "both", "crop": {"width": 1080, "height": 1920, "x": 4, "y": 0}, "crf": 16, "preset": "medium", "keep_audio": False},
    }


def package(p: dict) -> None:
    pre = ROOT / "sequence_outputs" / p["slug"] / "preproduction"
    write(pre / "recipe_bible.md", f"""# {p['title']} ({p['en']}) — Production Bible

## Production use

Commercial reference-generation package: three independent 5-second vertical MiniMax H3 Ref2VA clips, no final concat by default.

## Real basis

{p['logic']}

## Source list

{chr(10).join(f"- [{name}]({url}) - {note}" for name, url, note in p['sources'])}

## Visual food/product states

1. Opening — {p['states']['character_scene']}
2. Prep — {p['states']['prep_state']}
3. Process — {p['states']['cook_state']}
4. Hero — {p['states']['hero_state']}

## Commercial beat chain

Clip 1: {p['titles'][0]}. Clip 2: {p['titles'][1]}. Clip 3: {p['titles'][2]}.
""")
    write(pre / "recipe_sources.md", "# Recipe / Product Sources\n\n" + "\n".join(f"- [{name}]({url}) — {note}" for name, url, note in p["sources"]))
    for kind in ["character_scene", "prep_state", "cook_state", "hero_state"]:
        write(pre / "reference_prompts" / f"{kind}.md", reference_prompt(p, kind))
    board = [f"# {p['title']} — 3x5s Storyboard", "", "Three independent 5-second vertical H3 R2V clips, each with three timed shots.", ""]
    for n, (title, shots) in enumerate(zip(p["titles"], p["shots"]), 1):
        board += [f"## Clip {n}: {title}", "", *[f"- {shot}" for shot in shots], ""]
    write(pre / "storyboard.md", "\n".join(board))
    for n in range(1, 4):
        write(pre / "h3_prompts" / f"clip_{n:02d}_ref2va.md", h3_prompt(p, n))
    manifest = {
        "product": p["title"],
        "product_en": p["en"],
        "dish_identity": p["food"],
        "physical_sign_reference": "../../../company_logo/AGO.png",
        "source_product_images": p["source_products"],
        "assets": {kind: f"outputs/reference_assets/{p['asset_dir']}/generated/{p['slug']}_{kind}-1.png" for kind in ["character_scene", "prep_state", "cook_state", "hero_state"]},
        "generation_order": ["character_scene", "prep_state", "cook_state", "hero_state"],
    }
    write(pre / "reference_manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    write(SEQUENCES / f"{p['slug']}_3x5_1080.json", json.dumps(sequence(p), ensure_ascii=False, indent=2))


def main() -> None:
    for product in PRODUCTS:
        package(product)
        print(f"prepared {product['slug']}")


if __name__ == "__main__":
    main()
