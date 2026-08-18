#!/usr/bin/env python3
"""Render the canonical opening prompt."""

from __future__ import annotations

import argparse
from pathlib import Path

from media_links import media_markdown


BASE_DIR = Path(__file__).resolve().parent.parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render viral creative rewrite opening prompt.")
    parser.add_argument("--ui-language", choices=["zh", "en"], default="zh")
    parser.add_argument("--media-style", choices=["codex", "link", "both"], default="codex", help="Media markdown style: codex=![](path) inline (default); link=[](file:// url) clickable; both")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    template = BASE_DIR / "assets" / "examples" / "viral_video.mp4"
    product = BASE_DIR / "assets" / "examples" / "source_product.jpg"
    if args.ui_language == "en":
        print("This skill recreates an ad template for a new product with MiniMax H3: I first understand a reference ad video's hook, shot rhythm, satisfaction moments, and ending structure, then use your product image and any local H3 references as the product truth for three generation-ready clips.")
        print("\nThere are two inputs: a template video and a product image.")
        print("\n- Template video: the reference ad structure. I borrow pacing, shot order, camera language, actions, satisfaction points, and CTA function. I do not inherit its product, brand, packaging, claims, subtitles, or selling points.")
        print("- Product image and H3 references: the source of truth for generated product identity, appearance, packaging, scene, character, product state, and confirmed selling points.")
        print(f"\nDefault template video:\n{media_markdown('Default template video', template, style=args.media_style)}")
        print(f"\nDefault product image:\n{media_markdown('Default product image', product, style=args.media_style)}")
        print("\nFor better H3 results, keep the template video, product image, and optional reference stack close in category or use case. Also avoid product images with recognizable real human faces unless the face is intentionally part of a fictional character reference.")
        print("\nFlow:\nNo-cost rehearsal, or real analysis preview / real generation.")
        print("\nMedia:\nUse the default template video or your custom template? Use the default example product image or your own product image?")
        print("\nProduct and generation direction:\nProduct identity / must-keep selling points, target audience, goal, and any local H3 reference images. Default output is 9:16, three independent 5s clips, 1088x1920 native H3 with 1080x1920 crop target, Turbo 8 steps, no exported audio.")
        print("\nReal generation requires the MiniMax H3 ComfyUI server/tunnel to be reachable. In the real analysis/generation flow, I first show the brief, strategy, forbidden carryover, risk controls, and H3 prompt preview; after you approve the direction, we move to the H3 sequence submission step.")
        return

    print("这个 skill 做的是 MiniMax H3 广告模板复刻：我会先理解参考广告视频的开头钩子、镜头节奏、产品爽点和收尾方式，再用你的商品图和本地 H3 参考图作为产品真相，生成三段可剪辑的 H3 视频片段。")
    print("\n这里有两个输入：模板视频和商品图。")
    print("\n- 模板视频：只提供广告结构参考，比如节奏、镜头顺序、动作、爽点和 CTA 结构；不会继承里面的商品、品牌、包装、字幕或卖点。")
    print("- 商品图和 H3 参考图：提供最终视频里的商品身份、外观、包装、场景、人物、产品状态和确认卖点；生成结果要围绕这些本地参考。")
    print(f"\n默认模板视频（结构参考）：\n{media_markdown('默认模板视频', template, style=args.media_style)}")
    print(f"\n默认商品图（产品真相/彩排示例）：\n{media_markdown('默认商品图', product, style=args.media_style)}")
    print("\n更稳定的组合通常是同品类或相近使用场景，比如饮品配饮品/食品广告模板，美妆配美妆/护肤模板。跨品类也能借节奏和镜头结构，但 H3 的商品一致性和场景贴合度会弱一些。")
    print("\n另外，真实生成时商品图尽量不要包含可识别真人脸；如果要保留人物，请用虚构角色/模特参考图明确控制。更推荐商品本体、包装图、手持局部或不可识别身体局部。")
    print("\n先走哪种流程：\n无成本彩排 或 真实分析预览/正式生成")
    print("\n媒体选择：\n模板视频用默认还是自定义？商品图用默认示例还是你自己的商品图？")
    print("\n商品和生成方向：\n商品身份/必须保留卖点、目标人群、目标、以及可用的本地 H3 参考图；默认输出为 9:16、三段独立 5 秒、1088x1920 原生 H3、裁切目标 1080x1920、Turbo 8 steps、不导出音频。")
    print("\n正式生成需要 MiniMax H3 ComfyUI server/tunnel 可访问。进入真实分析/生成流程后，我会先给你看 brief、策略、禁止继承项、风险控制和 H3 prompt preview；你确认方向后，才会进入提交 H3 sequence 的下一步。")


if __name__ == "__main__":
    main()
