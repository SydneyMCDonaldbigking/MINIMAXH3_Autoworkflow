#!/usr/bin/env python3
"""Build contact sheets for the current cooking material batch."""

from __future__ import annotations

from pathlib import Path
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
THUMB_W = 180
THUMB_H = 320
GAP = 22
LABEL_H = 54
HEADER_H = 46
MARGIN = 36
BG = (247, 245, 239)
INK = (37, 35, 32)
MUTED = (102, 96, 88)


PROJECTS = [
    {
        "title": "Freezer Shrimp Wonton Egg Drop Soup",
        "preview": ROOT / "sequence_outputs/freezer_shrimp_wonton_egg_drop_soup/preproduction/preview/freezer_shrimp_wonton_full_material_preview.jpg",
        "items": [
            ("character_scene", ROOT / "outputs/reference_assets/19_freezer_shrimp_wonton_egg_drop_soup/freezer_shrimp_wonton_character_scene.png"),
            ("frozen_package", ROOT / "outputs/reference_assets/19_freezer_shrimp_wonton_egg_drop_soup/freezer_shrimp_wonton_frozen_package.png"),
            ("soup_seasoning_kit", ROOT / "outputs/reference_assets/19_freezer_shrimp_wonton_egg_drop_soup/freezer_shrimp_wonton_soup_seasoning_kit.png"),
            ("egg_reference", ROOT / "outputs/reference_assets/19_freezer_shrimp_wonton_egg_drop_soup/freezer_shrimp_wonton_egg_reference.png"),
            ("prep_state", ROOT / "outputs/reference_assets/19_freezer_shrimp_wonton_egg_drop_soup/freezer_shrimp_wonton_prep_state.png"),
            ("cook_state", ROOT / "outputs/reference_assets/19_freezer_shrimp_wonton_egg_drop_soup/freezer_shrimp_wonton_cook_state.png"),
            ("hero_state", ROOT / "outputs/reference_assets/19_freezer_shrimp_wonton_egg_drop_soup/freezer_shrimp_wonton_hero_state.png"),
        ],
    },
    {
        "title": "Japanese Teriyaki Chicken Thigh Rice",
        "preview": ROOT / "sequence_outputs/japanese_teriyaki_chicken_thigh/preproduction/preview/japanese_teriyaki_chicken_full_material_preview.jpg",
        "items": [
            ("character_scene", ROOT / "outputs/reference_assets/20_japanese_teriyaki_chicken_thigh/japanese_teriyaki_chicken_character_scene.png"),
            ("teriyaki_sauce_kit", ROOT / "outputs/reference_assets/20_japanese_teriyaki_chicken_thigh/japanese_teriyaki_chicken_teriyaki_sauce_kit.png"),
            ("prep_state", ROOT / "outputs/reference_assets/20_japanese_teriyaki_chicken_thigh/japanese_teriyaki_chicken_prep_state.png"),
            ("cook_state", ROOT / "outputs/reference_assets/20_japanese_teriyaki_chicken_thigh/japanese_teriyaki_chicken_cook_state.png"),
            ("hero_state_whole_thigh", ROOT / "outputs/reference_assets/20_japanese_teriyaki_chicken_thigh/japanese_teriyaki_chicken_hero_state.png"),
        ],
    },
    {
        "title": "Banana Milkshake",
        "preview": ROOT / "sequence_outputs/banana_milkshake/preproduction/preview/banana_milkshake_full_material_preview.jpg",
        "items": [
            ("banana_reference", ROOT / "outputs/reference_assets/22_banana_milkshake/banana_milkshake_banana_reference.png"),
            ("ingredient_kit", ROOT / "outputs/reference_assets/22_banana_milkshake/banana_milkshake_ingredient_kit.png"),
            ("character_scene", ROOT / "outputs/reference_assets/22_banana_milkshake/banana_milkshake_character_scene.png"),
            ("blend_state", ROOT / "outputs/reference_assets/22_banana_milkshake/banana_milkshake_blend_state.png"),
            ("hero_state", ROOT / "outputs/reference_assets/22_banana_milkshake/banana_milkshake_hero_state.png"),
        ],
    },
    {
        "title": "Rock Sugar Asian Pear Soup",
        "preview": ROOT / "sequence_outputs/rock_sugar_asian_pear_soup/preproduction/preview/rock_sugar_asian_pear_soup_full_material_preview.jpg",
        "items": [
            ("pear_reference", ROOT / "outputs/reference_assets/23_rock_sugar_asian_pear_soup/rock_sugar_asian_pear_soup_pear_reference.png"),
            ("ingredient_kit", ROOT / "outputs/reference_assets/23_rock_sugar_asian_pear_soup/rock_sugar_asian_pear_soup_ingredient_kit.png"),
            ("character_scene", ROOT / "outputs/reference_assets/23_rock_sugar_asian_pear_soup/rock_sugar_asian_pear_soup_character_scene.png"),
            ("prep_state", ROOT / "outputs/reference_assets/23_rock_sugar_asian_pear_soup/rock_sugar_asian_pear_soup_prep_state.png"),
            ("cook_state", ROOT / "outputs/reference_assets/23_rock_sugar_asian_pear_soup/rock_sugar_asian_pear_soup_cook_state.png"),
            ("hero_state", ROOT / "outputs/reference_assets/23_rock_sugar_asian_pear_soup/rock_sugar_asian_pear_soup_hero_state.png"),
        ],
    },
    {
        "title": "Garlic Chive Flower Pork Strips",
        "preview": ROOT / "sequence_outputs/garlic_chive_flower_pork_strips/preproduction/preview/garlic_chive_flower_pork_strips_full_material_preview.jpg",
        "items": [
            ("product_reference", ROOT / "outputs/reference_assets/24_garlic_chive_flower_pork_strips/garlic_chive_flower_pork_strips_product_reference.png"),
            ("ingredient_kit", ROOT / "outputs/reference_assets/24_garlic_chive_flower_pork_strips/garlic_chive_flower_pork_strips_ingredient_kit.png"),
            ("character_scene", ROOT / "outputs/reference_assets/24_garlic_chive_flower_pork_strips/garlic_chive_flower_pork_strips_character_scene.png"),
            ("prep_state", ROOT / "outputs/reference_assets/24_garlic_chive_flower_pork_strips/garlic_chive_flower_pork_strips_prep_state.png"),
            ("cook_state", ROOT / "outputs/reference_assets/24_garlic_chive_flower_pork_strips/garlic_chive_flower_pork_strips_cook_state.png"),
            ("hero_state", ROOT / "outputs/reference_assets/24_garlic_chive_flower_pork_strips/garlic_chive_flower_pork_strips_hero_state.png"),
        ],
    },
    {
        "title": "Yellow Chive Pork Strips",
        "preview": ROOT / "sequence_outputs/yellow_chive_pork_strips/preproduction/preview/yellow_chive_pork_strips_full_material_preview.jpg",
        "items": [
            ("product_reference", ROOT / "outputs/reference_assets/25_yellow_chive_pork_strips/yellow_chive_pork_strips_product_reference.png"),
            ("ingredient_kit", ROOT / "outputs/reference_assets/25_yellow_chive_pork_strips/yellow_chive_pork_strips_ingredient_kit.png"),
            ("character_scene", ROOT / "outputs/reference_assets/25_yellow_chive_pork_strips/yellow_chive_pork_strips_character_scene.png"),
            ("prep_state", ROOT / "outputs/reference_assets/25_yellow_chive_pork_strips/yellow_chive_pork_strips_prep_state.png"),
            ("cook_state", ROOT / "outputs/reference_assets/25_yellow_chive_pork_strips/yellow_chive_pork_strips_cook_state.png"),
            ("hero_state", ROOT / "outputs/reference_assets/25_yellow_chive_pork_strips/yellow_chive_pork_strips_hero_state.png"),
        ],
    },
    {
        "title": "Classic Kake Udon Noodle Soup",
        "preview": ROOT / "sequence_outputs/kake_udon_noodle_soup/preproduction/preview/kake_udon_noodle_soup_full_material_preview.jpg",
        "items": [
            ("product_reference", ROOT / "outputs/reference_assets/26_kake_udon_noodle_soup/kake_udon_noodle_soup_product_reference.png"),
            ("ingredient_kit", ROOT / "outputs/reference_assets/26_kake_udon_noodle_soup/kake_udon_noodle_soup_ingredient_kit.png"),
            ("character_scene", ROOT / "outputs/reference_assets/26_kake_udon_noodle_soup/kake_udon_noodle_soup_character_scene.png"),
            ("prep_state", ROOT / "outputs/reference_assets/26_kake_udon_noodle_soup/kake_udon_noodle_soup_prep_state.png"),
            ("cook_state", ROOT / "outputs/reference_assets/26_kake_udon_noodle_soup/kake_udon_noodle_soup_cook_state.png"),
            ("hero_state", ROOT / "outputs/reference_assets/26_kake_udon_noodle_soup/kake_udon_noodle_soup_hero_state.png"),
        ],
    },
    {
        "title": "Luffa Egg Soup",
        "preview": ROOT / "sequence_outputs/luffa_egg_soup/preproduction/preview/luffa_egg_soup_full_material_preview.jpg",
        "items": [
            ("product_reference", ROOT / "outputs/reference_assets/27_luffa_egg_soup/luffa_egg_soup_product_reference.png"),
            ("ingredient_kit", ROOT / "outputs/reference_assets/27_luffa_egg_soup/luffa_egg_soup_ingredient_kit.png"),
            ("character_scene", ROOT / "outputs/reference_assets/27_luffa_egg_soup/luffa_egg_soup_character_scene.png"),
            ("prep_state", ROOT / "outputs/reference_assets/27_luffa_egg_soup/luffa_egg_soup_prep_state.png"),
            ("cook_state", ROOT / "outputs/reference_assets/27_luffa_egg_soup/luffa_egg_soup_cook_state.png"),
            ("hero_state", ROOT / "outputs/reference_assets/27_luffa_egg_soup/luffa_egg_soup_hero_state.png"),
        ],
    },
    {
        "title": "McSpicy-Style Crispy Chicken Wings",
        "preview": ROOT / "sequence_outputs/mcspicy_chicken_wings/preproduction/preview/mcspicy_chicken_wings_full_material_preview.jpg",
        "items": [
            ("product_reference", ROOT / "outputs/reference_assets/28_mcspicy_chicken_wings/mcspicy_chicken_wings_product_reference.png"),
            ("ingredient_kit", ROOT / "outputs/reference_assets/28_mcspicy_chicken_wings/mcspicy_chicken_wings_ingredient_kit.png"),
            ("character_scene", ROOT / "outputs/reference_assets/28_mcspicy_chicken_wings/mcspicy_chicken_wings_character_scene.png"),
            ("prep_state", ROOT / "outputs/reference_assets/28_mcspicy_chicken_wings/mcspicy_chicken_wings_prep_state.png"),
            ("cook_state", ROOT / "outputs/reference_assets/28_mcspicy_chicken_wings/mcspicy_chicken_wings_cook_state.png"),
            ("hero_state", ROOT / "outputs/reference_assets/28_mcspicy_chicken_wings/mcspicy_chicken_wings_hero_state.png"),
        ],
    },
    {
        "title": "Lava Custard Mooncakes",
        "preview": ROOT / "sequence_outputs/lava_custard_mooncakes/preproduction/preview/lava_custard_mooncakes_full_material_preview.jpg",
        "items": [
            ("product_reference", ROOT / "outputs/reference_assets/29_lava_custard_mooncakes/lava_custard_mooncakes_product_reference.png"),
            ("gift_box_scene", ROOT / "outputs/reference_assets/29_lava_custard_mooncakes/lava_custard_mooncakes_gift_box_scene.png"),
            ("character_scene", ROOT / "outputs/reference_assets/29_lava_custard_mooncakes/lava_custard_mooncakes_character_scene.png"),
            ("cut_reveal_state", ROOT / "outputs/reference_assets/29_lava_custard_mooncakes/lava_custard_mooncakes_cut_reveal_state.png"),
            ("tea_pairing_state", ROOT / "outputs/reference_assets/29_lava_custard_mooncakes/lava_custard_mooncakes_tea_pairing_state.png"),
            ("hero_state", ROOT / "outputs/reference_assets/29_lava_custard_mooncakes/lava_custard_mooncakes_hero_state.png"),
        ],
    },
    {
        "title": "Cucumber Egg Soup",
        "preview": ROOT / "sequence_outputs/cucumber_egg_soup/preproduction/preview/cucumber_egg_soup_full_material_preview.jpg",
        "items": [
            ("product_reference", ROOT / "outputs/reference_assets/30_cucumber_egg_soup/cucumber_egg_soup_product_reference.png"),
            ("ingredient_kit", ROOT / "outputs/reference_assets/30_cucumber_egg_soup/cucumber_egg_soup_ingredient_kit.png"),
            ("character_scene", ROOT / "outputs/reference_assets/30_cucumber_egg_soup/cucumber_egg_soup_character_scene.png"),
            ("prep_state", ROOT / "outputs/reference_assets/30_cucumber_egg_soup/cucumber_egg_soup_prep_state.png"),
            ("cook_state", ROOT / "outputs/reference_assets/30_cucumber_egg_soup/cucumber_egg_soup_cook_state.png"),
            ("hero_state", ROOT / "outputs/reference_assets/30_cucumber_egg_soup/cucumber_egg_soup_hero_state.png"),
        ],
    },
]


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


TITLE_FONT = font(26, True)
SUB_FONT = font(18)
LABEL_FONT = font(15)


def thumb(path: Path) -> Image.Image:
    with Image.open(path) as image:
        rgb = image.convert("RGB")
        src_w, src_h = rgb.size
        scale = min(THUMB_W / src_w, THUMB_H / src_h)
        resized = rgb.resize((round(src_w * scale), round(src_h * scale)), Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (THUMB_W, THUMB_H), (232, 228, 219))
        x = (THUMB_W - resized.width) // 2
        y = (THUMB_H - resized.height) // 2
        canvas.paste(resized, (x, y))
        return canvas


def draw_label(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str) -> None:
    x, y = xy
    lines = wrap(text.replace("_", " "), width=20)[:2]
    for index, line in enumerate(lines):
        draw.text((x, y + index * 18), line, fill=MUTED, font=LABEL_FONT)


def build_project_sheet(project: dict[str, object]) -> None:
    items = project["items"]  # type: ignore[index]
    columns = min(4, len(items))
    rows = (len(items) + columns - 1) // columns
    width = MARGIN * 2 + columns * THUMB_W + (columns - 1) * GAP
    height = MARGIN * 2 + HEADER_H + rows * (THUMB_H + LABEL_H) + (rows - 1) * GAP
    canvas = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(canvas)
    draw.text((MARGIN, MARGIN), project["title"], fill=INK, font=TITLE_FONT)  # type: ignore[index]
    y0 = MARGIN + HEADER_H
    for i, (label, path) in enumerate(items):  # type: ignore[assignment]
        col = i % columns
        row = i // columns
        x = MARGIN + col * (THUMB_W + GAP)
        y = y0 + row * (THUMB_H + LABEL_H + GAP)
        canvas.paste(thumb(path), (x, y))
        draw_label(draw, (x, y + THUMB_H + 8), label)
    out_path = project["preview"]  # type: ignore[index]
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path, quality=92)
    canvas.save(Path(str(out_path)).with_suffix(".png"))


def build_master_sheet(
    projects: list[dict[str, object]] | None = None,
    *,
    title: str = "Current Material Batch",
    names: list[str] | None = None,
) -> None:
    projects = projects or PROJECTS
    names = names or [
        "current_material_batch_9_dishes_preview",
        "current_material_batch_11_dishes_preview",
        "current_material_batch_3_new_dishes_preview",
        "current_material_batch_6_dishes_preview",
        "wonton_chicken_banana_pear_chives_material_preview",
        "wonton_chicken_banana_pear_material_preview",
        "three_dish_split_material_preview",
    ]
    columns = 6
    width = MARGIN * 2 + columns * THUMB_W + (columns - 1) * GAP
    row_heights: list[int] = []
    for project in projects:
        rows = (len(project["items"]) + columns - 1) // columns
        row_heights.append(HEADER_H + rows * (THUMB_H + LABEL_H) + (rows - 1) * GAP + GAP)
    height = MARGIN * 2 + sum(row_heights)
    canvas = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(canvas)
    y = MARGIN
    draw.text((MARGIN, y), title, fill=INK, font=TITLE_FONT)
    y += HEADER_H + 6
    for project in projects:
        draw.text((MARGIN, y), project["title"], fill=INK, font=SUB_FONT)
        y += HEADER_H
        for i, (label, path) in enumerate(project["items"]):
            col = i % columns
            row = i // columns
            x = MARGIN + col * (THUMB_W + GAP)
            item_y = y + row * (THUMB_H + LABEL_H + GAP)
            canvas.paste(thumb(path), (x, item_y))
            draw_label(draw, (x, item_y + THUMB_H + 8), label)
        rows = (len(project["items"]) + columns - 1) // columns
        y += rows * (THUMB_H + LABEL_H) + (rows - 1) * GAP + GAP
    out_dir = ROOT / "sequence_outputs/_material_previews"
    out_dir.mkdir(parents=True, exist_ok=True)
    for name in names:
        canvas.save(out_dir / f"{name}.jpg", quality=92)
        canvas.save(out_dir / f"{name}.png")


def main() -> None:
    missing = [path for project in PROJECTS for _, path in project["items"] if not path.is_file()]
    if missing:
        for path in missing:
            print(f"missing: {path}")
        raise SystemExit(1)
    for project in PROJECTS:
        build_project_sheet(project)
    build_master_sheet()
    build_master_sheet(
        PROJECTS[-2:],
        title="Mooncake and Cucumber Material",
        names=["mooncake_cucumber_material_preview"],
    )
    print("previews built")


if __name__ == "__main__":
    main()
