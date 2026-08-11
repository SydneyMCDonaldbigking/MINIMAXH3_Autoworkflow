# Local ComfyUI MiniMax H3 Asset Map

Purpose: record the user's local Comfy Desktop / ComfyUI MiniMax H3 paths so future Codex tasks do not confuse the official native H3 workflow with the external Turbo LoRA workflow.

## ComfyUI Install

- Desktop shell path: `D:\comfyUI`
- Real ComfyUI install: `D:\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI`
- Comfy Desktop app config: `C:\Users\uryuu\AppData\Roaming\Comfy Desktop`
- Shared model/input/output root: `D:\Comfy-Desktop\ComfyUI-Shared`
- Shared model mapping file: `C:\Users\uryuu\AppData\Roaming\Comfy Desktop\shared_model_paths.yaml`

`D:\comfyUI` is not the model/runtime folder. Comfy Desktop maps models to `D:\Comfy-Desktop\ComfyUI-Shared\models`.

## Official Local H3 Models Found

Found under `D:\Comfy-Desktop\ComfyUI-Shared\models`:

```text
diffusion_models\minimax_h3_ref2va_pruned_int8_convrot.safetensors
text_encoders\qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors
vae\minimax_h3_video_vae_fp16.safetensors
vae\minimax_h3_audio_vae_fp32.safetensors
```

Not found locally in the shared model folder during this scan:

```text
diffusion_models\minimax_h3_fl2va_pruned_int8_convrot.safetensors
loras\minimax_h3_turbo_v4_step600_ema.safetensors
```

The local `loras` and `model_patches` shared folders were empty at scan time.

## Official Native H3 Nodes Found

Native MiniMax H3 nodes are part of the ComfyUI checkout, not `custom_nodes`:

```text
D:\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\comfy_extras\nodes_minimax_h3.py
```

Node classes in that file:

```text
EmptyMiniMaxH3LatentAV
MiniMaxH3ImageToVideo
MiniMaxH3ReferenceToVideo
MiniMaxH3SigmaShift
```

Sage attention is a core ComfyUI startup flag:

```text
--use-sage-attention
```

Implementation references:

```text
D:\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\comfy\cli_args.py
D:\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\comfy\model_management.py
```

## Local Official Workflow Evidence

Local output with embedded workflow:

```text
D:\Comfy-Desktop\ComfyUI-Shared\output\video\MiniMax_H3_00001_.mp4
```

That embedded workflow used:

```text
MiniMaxH3ReferenceToVideo
minimax_h3_ref2va_pruned_int8_convrot.safetensors
qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors
minimax_h3_video_vae_fp16.safetensors
minimax_h3_audio_vae_fp32.safetensors
KSamplerSelect: res_multistep
BasicScheduler: simple, 20 steps
Resolution: 864x480
Duration: about 5.17s
References: 首帧.png, 模特.png
```

The official template includes a size table where `0.3 megapixels / 16:9` maps to `736 x 416`, matching the user's screenshot resolution.

## Turbo LoRA Workflow Used By Our Server Runner

The local automation repo expects this external Turbo LoRA setup:

```text
Custom node repo: Larryvrh/ComfyUI-MiniMax-H3-Turbo
LoRA repo: larryvrh/MiniMax-H3-Turbo-Lora
LoRA file: minimax_h3_turbo_v4_step600_ema.safetensors
Expected server LoRA path: /root/ComfyUI/models/loras/minimax_h3_turbo_v4_step600_ema.safetensors
Expected local shared LoRA path if installed locally: D:\Comfy-Desktop\ComfyUI-Shared\models\loras\minimax_h3_turbo_v4_step600_ema.safetensors
```

The Turbo API templates in this repo use:

```text
MiniMaxH3TurboLoRA
MiniMaxH3TurboSampler
steps: 8 by production default
```

Examples:

```text
workflows\h3_r2v_turbo_api.json
workflows\h3_i2v_turbo_8step_api.json
workflows\h3_t2v_turbo_api.json
```

## Practical Distinction

- Official Comfy Desktop H3 local workflow: native H3 nodes, no external Turbo LoRA file, usually 20 steps unless edited.
- Our fast server workflow: external Turbo custom node plus `minimax_h3_turbo_v4_step600_ema.safetensors`, production 8 steps.
- If a server is missing `MiniMaxH3TurboLoRA` or `MiniMaxH3TurboSampler`, install/copy the Turbo custom node.
- If a server is missing `minimax_h3_turbo_v4_step600_ema.safetensors`, copy/download it into `models/loras`.
