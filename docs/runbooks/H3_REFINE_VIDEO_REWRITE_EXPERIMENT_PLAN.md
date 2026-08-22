# MiniMax H3 视频复刻实验交接计划

这份文档给 Claude 接手用。目标不是马上替换当前生产流，而是把别人提到的
`双采样 + Sigma Refine + 潜空间放大 + SolAttention/LIGHTX2V` 思路拆成可验证实验。

## 当前结论

我们现在的生产流是原生竖屏 1080 路线：

- `Ref2VA`
- `1088x1920` 生成，最后裁到 `1080x1920`
- MiniMax H3 Turbo LoRA：`minimax_h3_turbo_v4_step600_ema.safetensors`
- `8` steps
- `--turbo-low-vram`
- `--no-audio`
- 三段独立 `5s` clip，默认不拼接

别人视频里讲的路线不是同一个东西。它更像：

- 横屏示例先在 `960x544` 或类似半分辨率 latent 里采样
- 第一段采样后分离 audio/video latent
- 只对 video latent 做潜空间放大
- 再合并 audio/video latent
- 第二段采样 refine
- 最后得到 1080P

所以它的价值优先看“远景人物小脸、高动态颗粒化”，不能直接推断它比我们的商品/菜谱原生 1080 更适合商业片。

## 是否继续用当前 Turbo LoRA

实验 A/B/C/D 都继续使用当前 Turbo LoRA。理由：

- 它是我们现在稳定 1080 H3 生产流的基础变量。
- 如果实验不保留它，就不知道质量变化来自 Sigma、双采样、潜空间放大，还是来自 LoRA 替换。
- LIGHTX2V 0.1 先不要和 Turbo LoRA 混用，除非已经确认它的节点位置、模型类型、强度 `0.75`、以及是否会覆盖/叠加 Turbo。

## 实验顺序

1. `A_native1080_turbo_single`

   当前基线。先跑同一个视频复刻 prompt、同一张商品图、同一个 seed，只跑 clip 01。

2. `B_native1080_turbo_sigma_default`

   原生 1080 + Turbo LoRA + 本地 Sigma 节点探针。先用默认/接近默认参数，确认图能 build、能出片、不会 shape mismatch。

3. `C_native1080_turbo_sigma8`

   原生 1080 + 非默认 sigma perturbation。只有 B 稳定后才跑；如果 sampler tensor shape 报错，直接停止这一支。

4. `D_native1080_turbo_accel_sage_only`

   加速链实验，先关 SolAttention。这个主要测速度/显存，不要把它当成画质修复，除非同 prompt 同 seed 明显更稳。

5. `E_halfres_dual_sampler_latent_upscale`

   真正对应别人视频里说的半分辨率 latent 放大路线。竖屏对应尺寸应先测 `544x960 -> 1088x1920 -> crop 1080x1920`，不是直接照搬横屏 `960x544`。

6. `F_lightx2v_compatibility_probe`

   LIGHTX2V 兼容性实验。必须先拿到别人 workflow JSON 或对应模型/节点，确认它到底是 LoRA、model patch、sampler 还是别的节点。

## Claude 接手步骤

先用视频复刻 skill 得到 H3 sequence package。不要真实提交生成，只生成 dry-run package：

```powershell
python viral-creative-rewrite-skill\viral-creative-rewrite-skill\scripts\confirm_generation.py `
  --prepared-input-json C:\path\to\prepared.json `
  --ui-language zh `
  --h3-dry-run
```

然后拿 dry-run 生成的 `h3-package\sequence.json` 准备实验包：

```powershell
python scripts\prepare_h3_refine_experiment_pack.py `
  --sequence C:\path\to\sequence_outputs\viral-rewrite\<run_id>\h3-package\sequence.json `
  --experiment-id viral-rewrite-h3-refine-clip01
```

这个脚本只写文件，不提交 ComfyUI，不烧 GPU。输出目录默认在：

```text
C:\Users\uryuu\Desktop\comfyui_workflow\local_artifacts\h3_refine_experiments\
```

生成后先看：

- `README_CLAUDE_HANDOFF.md`
- `experiment_manifest.json`
- `commands.build_api_json.ps1`
- `commands.submit_real_runs.ps1.disabled`

`commands.build_api_json.ps1` 只保存 API JSON，所有命令都有 `--no-submit`。
`commands.submit_real_runs.ps1.disabled` 故意禁用，只有用户明确说可以烧卡时才处理。

## 节点探针

在任何实验提交前，Claude 必须先探测 ComfyUI：

```powershell
python h3_accel_runner.py --probe --server http://127.0.0.1:8189
```

重点记录：

- `MiniMaxH3TurboLoRA`
- `MiniMaxH3TurboSampler`
- `MiniMaxH3ReferenceToVideo`
- `MiniMaxH3SigmaShift` 或 `ModelSamplingAV`
- `JR_H3_UnifiedAcceleration`
- `RHMiniMaxH3DualSigmaSampler`
- `RHMiniMaxH3SeparateAVLatent`
- `RHMiniMaxH3CombineAVLatent`
- 任何接受 `LATENT` 输入的 latent upscale 节点
- LIGHTX2V 0.1 的真实 loader/model 名称

如果找不到 dual sampler、A/V latent split/merge、latent upscale，就不要声称已经复现别人那套，只能说完成了 native 1080 sigma/accel 实验。

## 记录标准

每个 5 秒 clip 都记录：

- workflow variant id
- prompt path
- API JSON path
- seed
- width/height/steps
- Turbo LoRA 是否开启
- Sigma/Refine 节点类名和参数
- LIGHTX2V 节点类名、模型名、strength
- run seconds
- peak VRAM
- output path
- ffprobe: width, height, fps, duration

质量评分用 1-5：

- 商品/菜品身份一致性
- 人物小脸完整度
- 高动态颗粒化/像素碎裂
- 食物或商品质感真实性
- 运镜稳定度
- 手和物体交互
- 字幕/价格/UI 幻觉控制
- 末帧能否给下一段当参考

## 晋级规则

- 原生 1080 基线默认保留。
- Sigma/Refine 只有在不增加明显产品漂移的情况下才考虑进入生产流。
- 加速链只按速度晋级，不按“感觉高级”晋级。
- 半分辨率 latent upscale 如果只改善人物小脸，但损害商品包装、食物纹理或真实质感，只作为人物/高动态可选分支。
- LIGHTX2V 只有在单独兼容性测试稳定后，才允许和 Turbo LoRA 做叠加实验。

## 不要做的事

- 不要把别人横屏 `960x544` 直接套到我们的竖屏商品流。
- 不要直接替换 `h3_runner.py` 和 `h3_sequence_runner.py`。
- 不要把半分辨率放大结果当成原生 1080。
- 不要在没有 `/object_info` 证据时编造节点名。
- 不要提交 API key、SSH 信息、签名 URL、网盘链接或原始 provider 响应。

---

## 节点探测结果（2026-08-18，H100 NVL，`/object_info` 1088 个类）

这一节是事实，不是计划。下次接手不要重新探一遍。

| 实验 | 需要的节点 | 在不在 |
| --- | --- | --- |
| A 基线 | — | ✅ |
| B sigma 默认 | `MiniMaxH3SigmaShift`（inputs: model, shift_video, shift_audio） | ✅ |
| C sigma k≠12 | 同上 | ✅ |
| D sage only | `JR_H3_UnifiedAcceleration` + `PathchSageAttentionKJ` | ✅ 两个都在 |
| D+ 完整 Sol-Attn | `SolAttnPatch` | ❌ 缺 `ComfyUI-SolAttn_triton` |
| **E 半分辨率双采样** | `RHMiniMaxH3SeparateAVLatent` / `RHMiniMaxH3CombineAVLatent` / `RHMiniMaxH3DualSigmaSampler` | ❌ **三个全缺** |
| F LightX2V | 任何 lightx2v loader | ❌ 一个都没有 |

`ModelSamplingAV` 也不存在，所以 `h3_accel_runner.py` 的候选列表里只有
`MiniMaxH3SigmaShift` 会命中。

### E 组的结论要改写

`SplitSigmas` / `SplitSigmasDenoise`（ComfyUI 核心）和 `LatentUpscale` /
`LatentUpscaleBy` / `LatentUpscaleModelLoader` 都在，但 **H3 的 A/V latent
拆分合并节点不存在**。装到的三个 H3 节点包（MiniMax-H3-Turbo、JR、KJNodes）
都没有提供。有一个 `LTXVSeparateAVLatent`，那是 LTXV 的，接口不通用。

H3 一次产出音视频合并的 latent（`EmptyMiniMaxH3LatentAV` 可证），不拆开就没法
只放大视频那一半。**所以 E 不是"还没跑"，是缺件跑不了。** 要推进只有两条路：

1. 拿到对方的 workflow JSON，看清他们用的到底是哪个节点包；
2. 或者自己实现 AV latent 的拆分/合并。

在此之前，不要在任何文档或对话里说我们复现了那套路线。

### 两个计划外的发现，值得单独测

- `MiniMaxH3MemoryEfficientSageAttentionPatch` —— H3 原生的 sage attention
  节点，**不经过 JR 那条链**。我们的加速实验一直假设只有
  `JR_H3_UnifiedAcceleration` 一条路，这是第二条，而且少一层依赖
  （不需要 KJNodes）。值得作为 D 组的对照。
- `JR_H3_RTXUpscalerRefiner` —— 名字指向放大/精修，可能和 E 组想解决的问题
  部分重叠。先看 `/object_info` 里它的输入输出类型再判断。

### 晋级规则补一条

加速链只按速度晋级，放大链只按细节晋级，**都不许当语义修复用**。

别人视频里的 6 steps 和我们 2026-08-11 否掉的 6 steps 不是一回事：他们把采样
拆成两段、中间插潜空间放大，我们那次是单段直接砍到 6 步。但潜空间放大改善的是
细节不是语义，所以它救不了"白菜整颗没切"那类错误——那次 `check_clip_quality.py`
还给了比 8 步更好的 flip rate。**质量门永远读不出语义错误，只能看帧。**


## `<Video N>` 和 `<Audio N>` 是支持的（2026-08-19 探测）

`MiniMaxH3ReferenceToVideo` 的 optional 输入不止 `ref_images`：

```text
ref_images        COMFY_AUTOGROW_V3
ref_videos        COMFY_AUTOGROW_V3
ref_video_audios  COMFY_AUTOGROW_V3
ref_audios        COMFY_AUTOGROW_V3
```

节点原生接受**视频参考和音频参考**，也就是官方文档里的 `<Video N>` 和
`<Audio N>` 标签，配套的 retention 词表是 `fully_copy` / `partially_copy` /
`reference` / `weak_reference` —— `prompts/validate_prompt.py` 早就认这套词，
我们只是从来没用过。

**为什么这对复刻是条新路**：现在的做法是从模板视频里裁静帧，而裁帧会连带拖进
水印、标题卡、别人的道具（2026-08-19 的 sample2 包就是这样：`miikubakinglab`
水印 + `Strawberry Iced Tea` 标题卡 + 杯里漂着草莓）。绑整段视频当**时序参考**，
让静帧只管颜色和道具，可能是更干净的分工。

**要用还得改 runner**：`h3_runner.py` 只把 `--ref-image` 接到 `ref_images`，
另外三个口没接。改动落在实验 runner 或新文件里，不动稳定生产流。

先记下来，没测过。别拿它当结论。
