#!/usr/bin/env python3
"""
Generate the Seedream reference bible for a dish from a config file.

For any new cooking dish, search real recipes and write the source notes and
recipe bible required by prompts/COOKING_PROMPT_PRODUCTION_STANDARD.md before
writing or generating reference prompts.

Hand-writing four prompts and a PowerShell script per dish does not scale past
about three dishes, and the parts that actually matter are the same four every
time: who is cooking, what the prep looks like, what the working state looks
like, and what the finished dish looks like. Everything else is boilerplate that
was being copied and drifting.

So the varying parts live in prompts/dish_configs/<slug>.json and the structure
lives here. Four assets, generated in order because each feeds the next as a
reference; that chain is what keeps the cook, the kitchen and the ingredient
looking like one shoot across three clips.

  1 character_scene   the person and the kitchen
  2 prep_state        proves the cutting happened, defines the cut sizes
  3 cook_state        the working state clip 02 must match
  4 hero_state        the frame the whole ad lands on

Two rules are baked into every prompt because both cost us real time:

  no brand text   Seedream rendered UMALL as UMANE and invented its own layout.
                  H3 gets the real logo as a reference and renders it correctly,
                  so Seedream is told to keep all printed cards out of frame.
  no hands in prep The prep image exists precisely so no clip has to show a knife
                  working in close-up, which is where H3 falls apart.

Examples:
  python generate_dish_assets.py --list
  python generate_dish_assets.py kungpao_chicken --print-only
  python generate_dish_assets.py --all
"""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent
CONFIG_DIR = ROOT / "prompts" / "dish_configs"
PROMPT_DIR = ROOT / "prompts" / "seedream_reference_assets"
OUT_ROOT = ROOT / "outputs" / "reference_assets" / "_generated"

COMMON_STYLE = (
    "STYLE: photorealistic commercial food cinematography, high quality, "
    "realistic hands, natural textures, rich but clean colour grade.")
COMMON_NEG = (
    "subtitles, title cards, watermarks, floating logo, any printed card, "
    "any brand text, invented lettering, fake app UI, distorted face, "
    "extra fingers, warped cookware, messy kitchen")

TEMPLATES = {
    "character_scene": """Create a clean high-quality vertical reference image for a premium cooking commercial, 1080x1920.

PURPOSE: character and kitchen style reference for MiniMax H3 {dish_en}.

SCENE: {kitchen}.

SUBJECT: {cook}, standing at a prep counter. The raw ingredient is clearly presented on the counter: {product_desc}. Keep all printed cards, packaging and brand text out of frame.

COMPOSITION: vertical 9:16, medium shot from a slightly high three-quarter angle. Cook, ingredient, cooking vessel and kitchen style all legible. Leave room for hand motion.

{style}

NEGATIVE: {neg}, {negatives_global}.
""",
    "prep_state": """Create a clean high-quality vertical reference image for a premium cooking commercial, 1080x1920.

PURPOSE: prep-state reference proving real ingredient processing, for MiniMax H3 {dish_en}. This image defines {prep_defines} for the whole ad.

SCENE: a work surface in the kitchen described by the character reference, natural directional light.

SUBJECT: {prep_subject}.

COMPOSITION: vertical 9:16, close-up from a high three-quarter angle. Every cut size and every component is clearly legible. No hands in frame.

{style}

NEGATIVE: {neg}, hands in frame, packaging in frame, {negatives_global}.
""",
    "cook_state": """Create a clean high-quality vertical reference image for a premium cooking commercial, 1080x1920.

PURPOSE: mid-cooking state reference for MiniMax H3 {dish_en}. This is the working state the second clip must match.

SCENE: {cook_vessel} in the kitchen described by the character reference.

SUBJECT: {cook_subject}.

COMPOSITION: vertical 9:16, close-up at vessel height looking slightly down. The state of the ingredient and the heat source are both legible.

{style}

NEGATIVE: {neg}, {cook_negatives}, {negatives_global}.
""",
    "hero_state": """Create a clean high-quality vertical reference image for a premium cooking commercial, 1080x1920.

PURPOSE: finished hero state for MiniMax H3 {dish_en}. This is the final frame the whole ad lands on.

SCENE: {hero_setting}.

SUBJECT: {hero_subject}. Keep all printed cards, packaging and brand text out of frame.

COMPOSITION: vertical 9:16, close hero food angle from about 30 degrees above. The texture and gloss of the finished dish are the subject.

{style}

NEGATIVE: {neg}, hands in frame, {negatives_global}.
""",
}

ORDER = ["character_scene", "prep_state", "cook_state", "hero_state"]


def load(slug: str) -> dict:
    path = CONFIG_DIR / f"{slug}.json"
    if not path.is_file():
        raise SystemExit(f"no config for {slug!r}; expected {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def render(cfg: dict) -> dict[str, pathlib.Path]:
    PROMPT_DIR.mkdir(parents=True, exist_ok=True)
    written = {}
    for kind in ORDER:
        text = TEMPLATES[kind].format(style=COMMON_STYLE, neg=COMMON_NEG, **cfg)
        path = PROMPT_DIR / f"{cfg['slug']}_{kind}.md"
        path.write_text(text, encoding="utf-8", newline="\n")
        written[kind] = path
    return written


def product_path(cfg: dict) -> pathlib.Path:
    path = ROOT / "sample_pictures" / cfg["product_dir"] / cfg["product_file"]
    if not path.is_file():
        raise SystemExit(f"product image not found: {path}")
    return path


def generated(cfg: dict, kind: str) -> pathlib.Path:
    stem = f"{cfg['slug']}_{kind}"
    return OUT_ROOT / stem / "generated" / f"{stem}-1.png"


def build_jobs(cfg: dict, prompts: dict[str, pathlib.Path]) -> list[dict]:
    product = product_path(cfg)
    chain = {
        # Each asset sees the product plus whatever was already established,
        # so the cook and kitchen carry through instead of being reinvented.
        "character_scene": [product],
        "prep_state": [generated(cfg, "character_scene"), product],
        "cook_state": [generated(cfg, "character_scene"),
                       generated(cfg, "prep_state"), product],
        "hero_state": [generated(cfg, "character_scene"),
                       generated(cfg, "cook_state"), product],
    }
    jobs = []
    for kind in ORDER:
        stem = f"{cfg['slug']}_{kind}"
        jobs.append({
            "stem": stem,
            "prompt": prompts[kind],
            "out": OUT_ROOT / stem,
            "refs": chain[kind],
        })
    return jobs


def run(job: dict, print_only: bool) -> None:
    cmd = [sys.executable, str(ROOT / "image2_first_frame.py"),
           "--prompt-file", str(job["prompt"]),
           "--out-dir", str(job["out"]),
           "--stem", job["stem"],
           "--model", "bytedance-seed/seedream-4.5",
           "--resolution", "2K",
           "--aspect-ratio", "9:16",
           "--final-size", "1080x1920"]
    for ref in job["refs"]:
        cmd += ["--reference", str(ref)]
    if print_only:
        print("  " + " ".join(cmd))
        return
    print(f"  generating {job['stem']}")
    result = subprocess.run(cmd, cwd=ROOT)
    if result.returncode != 0:
        raise SystemExit(f"generation failed: {job['stem']}")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("slugs", nargs="*", help="dish config slugs")
    parser.add_argument("--all", action="store_true", help="every config in prompts/dish_configs")
    parser.add_argument("--list", action="store_true", help="list available configs and exit")
    parser.add_argument("--print-only", action="store_true",
                        help="write the prompts and show the commands, generate nothing")
    args = parser.parse_args(argv)

    available = sorted(p.stem for p in CONFIG_DIR.glob("*.json"))
    if args.list:
        for slug in available:
            cfg = load(slug)
            print(f"  {slug:32} {cfg['dish_cn']}  ({cfg['dish_en']})")
        return 0

    slugs = available if args.all else args.slugs
    if not slugs:
        parser.error("name a dish, or use --all or --list")

    for slug in slugs:
        cfg = load(slug)
        print(f"\n{cfg['dish_cn']} ({slug})")
        prompts = render(cfg)
        print(f"  wrote {len(prompts)} prompts to {PROMPT_DIR.relative_to(ROOT).as_posix()}/")
        for job in build_jobs(cfg, prompts):
            run(job, args.print_only)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
