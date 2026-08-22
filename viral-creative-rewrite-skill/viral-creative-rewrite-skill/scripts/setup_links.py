from __future__ import annotations

from pathlib import Path


def _workflow_root_hint() -> str:
    skill_root = Path(__file__).resolve().parent.parent
    for candidate in [skill_root, *skill_root.parents]:
        if (candidate / "h3_sequence_runner.py").exists():
            return str(candidate)
    return str(skill_root.parent.parent)


def print_h3_runtime_setup(language: str = "zh") -> None:
    root = _workflow_root_hint()
    if language == "en":
        print("\nMiniMax H3 runtime setup:")
        print(f"1. Use the workflow repo as H3_WORKFLOW_ROOT: {root}")
        print("2. Start ComfyUI with MiniMax H3 models and Turbo LoRA on the GPU server, listening on 127.0.0.1:8189.")
        print("3. Open the SSH tunnel on this PC: ssh -N -L 8189:127.0.0.1:8189 user@SERVER_IP")
        print("4. Confirm the server is reachable at H3_COMFYUI_SERVER=http://127.0.0.1:8189.")
        print("5. Keep product/reference images as local files. H3 Ref2VA does not accept remote image URLs in this local runner.")
        print("6. The skill writes three 5s prompt files plus sequence.json outside the skill folder, then calls h3_sequence_runner.py run --no-concat.")
        return
    print("\nMiniMax H3 运行准备：")
    print(f"1. 使用当前工作流仓库作为 H3_WORKFLOW_ROOT：{root}")
    print("2. 在 GPU server 上启动带 MiniMax H3 模型和 Turbo LoRA 的 ComfyUI，监听 127.0.0.1:8189。")
    print("3. 在这台电脑打开 SSH tunnel：ssh -N -L 8189:127.0.0.1:8189 user@SERVER_IP")
    print("4. 确认 H3_COMFYUI_SERVER=http://127.0.0.1:8189 可访问。")
    print("5. 商品图和参考图必须是本地文件；这个本地 H3 Ref2VA runner 不直接吃远程图片 URL。")
    print("6. skill 会在 skill 文件夹外写三段 5 秒 prompt 和 sequence.json，然后调用 h3_sequence_runner.py run --no-concat。")


def print_base_setup_links(language: str = "zh") -> None:
    print_h3_runtime_setup(language)


def print_real_generation_setup_flow(language: str = "zh") -> None:
    print_h3_runtime_setup(language)


def print_local_key_setup_hint(env_path: str, language: str = "zh") -> None:
    if language == "en":
        print("\nOptional local .env:")
        print(f"- File: {env_path}")
        print("- H3_COMFYUI_SERVER=http://127.0.0.1:8189")
        print("- H3_WORKFLOW_ROOT can be set when the skill is installed outside this repo.")
        print("- H3_OUTPUT_ROOT can override where sequence outputs are written.")
        return
    print("\n可选本地 .env：")
    print(f"- 文件：{env_path}")
    print("- H3_COMFYUI_SERVER=http://127.0.0.1:8189")
    print("- 如果 skill 安装到了仓库外，可以设置 H3_WORKFLOW_ROOT。")
    print("- 如需改输出位置，可以设置 H3_OUTPUT_ROOT。")
