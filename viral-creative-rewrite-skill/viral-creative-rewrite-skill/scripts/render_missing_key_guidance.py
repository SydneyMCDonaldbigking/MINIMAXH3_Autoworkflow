#!/usr/bin/env python3
"""Render the canonical MiniMax H3 runtime-blocked frontstage response."""

from __future__ import annotations

import argparse
from pathlib import Path

from env_loader import load_env_file
from run_rewrite_video import (
    print_confirmed_missing_key_snapshot,
    print_h3_advantages_and_setup,
    request_language,
)
from schemas import PreparedRewrite
from services import normalize_prepared_for_generation


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render complete MiniMax H3 runtime guidance for a confirmed prepared brief.")
    parser.add_argument("--prepared-input-json", required=True, help="Confirmed prepared JSON path")
    parser.add_argument("--env-file", default=".env", help="Env file path to load")
    parser.add_argument("--ui-language", choices=["auto", "zh", "en"], default="auto", help="User-facing language")
    parser.add_argument("--issue", default="", help="Preflight issue text to show before setup guidance")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    load_env_file(args.env_file)
    prepared_path = Path(args.prepared_input_json).expanduser().resolve()
    prepared = normalize_prepared_for_generation(PreparedRewrite.model_validate_json(prepared_path.read_text(encoding="utf-8")))
    language = request_language(prepared.request, args.ui_language)

    print_confirmed_missing_key_snapshot(prepared, language=language)
    if args.issue:
        print()
        print(args.issue)
    if language == "en":
        print("\nMiniMax H3 generation was not submitted, no GPU time was used, and no new clips were generated.")
        print("The prepared brief is reusable after the H3 runtime/server issue is fixed.")
    else:
        print("\n未提交 MiniMax H3，未消耗 GPU 时间，也没有生成新片段。")
        print("修好 H3 运行环境或 server 后，这份 prepared brief 可以继续复用。")
    print_h3_advantages_and_setup(language=language)


if __name__ == "__main__":
    main()
