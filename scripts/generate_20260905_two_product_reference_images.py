#!/usr/bin/env python3
"""Call the real image API for the two dishes prepared by
prepare_20260905_two_product_campaign.py.

Those reference prompts live under sequence_outputs/<slug>/preproduction/
reference_prompts/, not prompts/dish_configs/<slug>.json, so
generate_dish_assets.py's config loader does not apply here. This script
does the same generate-in-order chaining by hand: character_scene sees the
AGO tabletop-sign artwork plus the supplied product photo; prep_state,
cook_state and hero_state each see the two images the doc chain calls for,
so the same cast/kitchen keep carrying forward exactly as
generate_dish_assets.py does for the legacy config path.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGO_LOGO = ROOT / "company_logo" / "AGO.png"

DISHES = [
    {
        "slug": "bbq_lamb_camping",
        "asset_dir": "54_bbq_lamb_camping",
        "source_product": ROOT / "outputs/reference_assets/54_bbq_lamb_camping/source_products/bbq_lamb_camping_source.png",
    },
    {
        "slug": "beauty_congee_office",
        "asset_dir": "55_beauty_congee_office",
        "source_product": ROOT / "outputs/reference_assets/55_beauty_congee_office/source_products/beauty_congee_office_source.png",
    },
]

ORDER = ["character_scene", "prep_state", "cook_state", "hero_state"]


def generated_path(dish: dict, kind: str) -> Path:
    return ROOT / "outputs/reference_assets" / dish["asset_dir"] / "generated" / f"{dish['slug']}_{kind}-1.png"


def refs_for(dish: dict, kind: str) -> list[Path]:
    if kind == "character_scene":
        return [AGO_LOGO, dish["source_product"]]
    if kind == "prep_state":
        return [generated_path(dish, "character_scene")]
    if kind == "cook_state":
        return [generated_path(dish, "character_scene"), generated_path(dish, "prep_state")]
    return [generated_path(dish, "character_scene"), generated_path(dish, "cook_state")]  # hero_state


def run_one(dish: dict, kind: str, print_only: bool) -> None:
    prompt_path = ROOT / "sequence_outputs" / dish["slug"] / "preproduction" / "reference_prompts" / f"{kind}.md"
    out_dir = ROOT / "outputs/reference_assets" / dish["asset_dir"]
    refs = refs_for(dish, kind)
    if not print_only:
        for ref in refs:
            if not ref.is_file():
                raise SystemExit(f"missing reference image, generate it first: {ref}")
    cmd = [
        sys.executable, str(ROOT / "image2_first_frame.py"),
        "--prompt-file", str(prompt_path),
        "--out-dir", str(out_dir),
        "--stem", f"{dish['slug']}_{kind}",
    ]
    for ref in refs:
        cmd += ["--reference", str(ref)]
    print(f"\n== {dish['slug']} / {kind} ==")
    print("  " + " ".join(cmd))
    if print_only:
        return
    result = subprocess.run(cmd, cwd=ROOT)
    if result.returncode != 0:
        raise SystemExit(f"generation failed: {dish['slug']}/{kind}")


def main(argv: list[str]) -> int:
    print_only = "--print-only" in argv
    only_slugs = [a for a in argv if not a.startswith("--")]
    for dish in DISHES:
        if only_slugs and dish["slug"] not in only_slugs:
            continue
        for kind in ORDER:
            run_one(dish, kind, print_only)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
