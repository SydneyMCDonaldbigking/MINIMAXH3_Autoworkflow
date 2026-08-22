#!/usr/bin/env python3
"""Render the canonical generation-result frontstage response."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from media_links import media_markdown
from schemas import RewriteVideoResponse

VIDEO_EXTENSIONS = (".mp4", ".mov", ".webm", ".mkv", ".avi")


def _language(payload: dict) -> str:
    request = payload.get("request") or {}
    language = request.get("ui_language") or "zh"
    return "en" if language == "en" else "zh"


def _looks_like_video(value: str | None) -> bool:
    if not value:
        return False
    return value.split("?", 1)[0].lower().endswith(VIDEO_EXTENSIONS)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render final video generation result.")
    parser.add_argument("--result-json", required=True, help="Generation result JSON path")
    parser.add_argument("--media-style", choices=["codex", "link", "both"], default="codex", help="Media markdown style: codex=![](path) inline (default); link=[](file:// url) clickable; both")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result_path = Path(args.result_json).expanduser().resolve()
    payload = json.loads(result_path.read_text(encoding="utf-8"))
    language = _language(payload)
    response = RewriteVideoResponse.model_validate(payload)
    video = response.rewritten_video_local_path or response.rewritten_video_url or response.rewritten_video_remote_url
    if not _looks_like_video(video):
        video = ""
    if language == "en":
        print("MiniMax H3 generation complete. Review the generated clips first:")
        if response.h3_clip_paths:
            for index, clip_path in enumerate(response.h3_clip_paths, start=1):
                print(media_markdown(f"Generated clip {index:02d}", clip_path, style=args.media_style))
        elif video:
            print(media_markdown("Generated video", video, style=args.media_style))
        if response.h3_run_id:
            print(f"H3 run ID: {response.h3_run_id}")
        if response.h3_manifest_path:
            print(f"H3 manifest: {response.h3_manifest_path}")
        print("Manual review checklist:")
        print("- Confirm the product identity matches the product image.")
        print("- Confirm there are no subtitles, price tags, shopping buttons, platform UI, or template brand remnants.")
        print("- Confirm clip 01 has the hook, clip 02 has proof/texture/use mechanics, and clip 03 has a product-visible close.")
        print(f"Result JSON saved: {result_path}")
        return

    print("MiniMax H3 生成完成。先看生成片段：")
    if response.h3_clip_paths:
        for index, clip_path in enumerate(response.h3_clip_paths, start=1):
            print(media_markdown(f"生成片段 {index:02d}", clip_path, style=args.media_style))
    elif video:
        print(media_markdown("生成视频", video, style=args.media_style))
    if response.h3_run_id:
        print(f"H3 run ID：{response.h3_run_id}")
    if response.h3_manifest_path:
        print(f"H3 manifest：{response.h3_manifest_path}")
    print("人工检查重点：")
    print("- 商品身份是否和商品图一致。")
    print("- 是否没有字幕、价格、购物按钮、平台 UI 或模板品牌残留。")
    print("- clip 01 是否有 hook，clip 02 是否有证明/质感/使用机制，clip 03 是否有商品可见的收口。")
    print(f"结果 JSON 已保存：{result_path}")


if __name__ == "__main__":
    main()
