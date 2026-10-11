# Claude：四组 H3 带货视频执行说明

## 交付目标

请在本仓库为下列四个商品分别渲染 **3 条独立竖版视频**，不要拼接：

- 每条约 5 秒；MiniMax H3 R2V / Ref2VA；8 steps Turbo；无原生音频。
- 先以 1088×1920 生成，交付时裁切为 **1080×1920、24fps**。
- 输出命名为 `clip-01_1080x1920.mp4`、`clip-02_1080x1920.mp4`、`clip-03_1080x1920.mp4`。
- 不要做 final concat，不要加字幕、旁白、价格、UI、水印或后期贴图。

这不是重新策划任务。请严格使用已经存在的分镜、Prompt、sequence JSON 与参考图；除非渲染失败，不要改写创意或换产品。

## 必读文件与入口

工作区：`C:\Users\uryuu\Desktop\comfyui_workflow`

| 商品 | Sequence | 分镜 | H3 Prompts | 参考图目录 |
|---|---|---|---|---|
| 缤纷迷你月饼 | `sequences/assorted_mini_mooncakes_3x5_1080.json` | `sequence_outputs/assorted_mini_mooncakes/preproduction/storyboard.md` | `sequence_outputs/assorted_mini_mooncakes/preproduction/h3_prompts/` | `outputs/reference_assets/31_assorted_mini_mooncakes/generated/` |
| 寿桃台湾刀削面 | `sequences/sautao_knife_cut_noodles_3x5_1080.json` | `sequence_outputs/sautao_knife_cut_noodles/preproduction/storyboard.md` | `sequence_outputs/sautao_knife_cut_noodles/preproduction/h3_prompts/` | `outputs/reference_assets/32_sautao_knife_cut_noodles/generated/` |
| 潮汕牛骨清汤料 | `sequences/chaopai_beef_bone_broth_3x5_1080.json` | `sequence_outputs/chaopai_beef_bone_broth/preproduction/storyboard.md` | `sequence_outputs/chaopai_beef_bone_broth/preproduction/h3_prompts/` | `outputs/reference_assets/33_chaopai_beef_bone_broth/generated/` |
| 灌汤包 | `sequences/xiaolongbao_3x5_1080.json` | `sequence_outputs/xiaolongbao/preproduction/storyboard.md` | `sequence_outputs/xiaolongbao/preproduction/h3_prompts/` | `outputs/reference_assets/34_xiaolongbao/generated/` |

各商品的原始产品图在相应 `preproduction/product_references/` 下。所有参考图已是 1080×1920。

## 不可改动的视觉规则

1. 以原商品图为产品真相，**绝不换成想象出来的产品、包装或配料**。
2. `<Picture 1>` 在第一条是新首帧；第二、三条的 `<Picture 1>` 是上段尾帧，标签会顺延。以 sequence JSON 中 `ref_images` 的顺序为准。
3. 首帧里的桌面品牌牌是已经生成到图中的真实道具；可以自然地随参考延续，但**不得在 H3 视频 Prompt 内写 logo、品牌名、品牌文案或要求叠加图形**，也不得做浮动贴片。
4. 有原包装的产品必须在画面中保持原包装：
   - 刀削面：橙色寿桃包装；
   - 牛骨汤：金米色潮汕牛骨清汤包装。
   月饼和灌汤包没有原包装，不得虚构包装。
5. 四组人物、服装、厨房/场地不得互相串用：
   - 月饼：户外花园，四位亚洲成年好友；
   - 刀削面：灰砖红窗北方厨房，靛蓝上衣男厨师；
   - 牛骨汤：墨绿砖家庭厨房、黑砂锅，深绿上衣中年女厨师；
   - 灌汤包：明亮粤式早餐厨房，芥末黄毛衣男主人。
6. 灌汤包始终是蒸笼内 **6 只**；仅最终状态可另有 1 只落在白瓷勺上。两杯豆浆必须保留。
7. 牛骨汤必须清亮金黄，配牛骨/牛肉、白萝卜、豆腐、红枣和葱；不可变成红油、麻辣或浑汤。
8. 刀削面必须宽、扁、波纹状；不可生成拉面、意面或细面。

## 已锁定的故事节奏

每条严格只有 3 个镜头：

- `0.0–1.6s`：建立场景和动作起点。
- `1.6–3.4s`：一个清晰的近景/中近景动作证明。
- `3.4–5.0s`：完成动作并交给下一段。

按各自 `storyboard.md` 与 `clip_XX_ref2va.md` 执行，勿在单段加入第四个切镜、复杂多重运镜或多项同时发生的动作。

## 开跑前校验

在工作区根目录执行：

```powershell
& 'C:\Users\uryuu\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' prompts\validate_prompt.py `
  sequences\assorted_mini_mooncakes_3x5_1080.json `
  sequences\sautao_knife_cut_noodles_3x5_1080.json `
  sequences\chaopai_beef_bone_broth_3x5_1080.json `
  sequences\xiaolongbao_3x5_1080.json
```

预期结果：`12 passed, 0 failed`。

先逐个 dry-run。远端默认目录和环境仅作参考，先确认实际路径、ComfyUI 队列、GPU 空闲与模型是否就绪：

```bash
cd /root/MINIMAXH3_Autoworkflow
source /home/node/anaconda3/etc/profile.d/conda.sh
conda activate comfy_h3_torch29_cu126
python h3_sequence_runner.py run \
  --sequence sequences/<上述某一个 sequence>.json \
  --server http://127.0.0.1:8189 \
  --output-root sequence_outputs \
  --run-id <product>_r2v_v2 \
  --no-concat \
  --dry-run
```

如果实际运行机不是这个目录，先同步 product references、16 张生成参考图、prompt 文件和 sequence JSON，并保持相对路径有效。不要在 skill 目录里写输出。

## 正式渲染与验收

1. 四个 sequence 逐一用 `--no-concat` 运行；第二、三条保留 `use_previous_last_frame_as_ref`。
2. 每条完成后裁切：`crop=1080:1920:4:0`，导出无音频。
3. 运行 `ffprobe`，确认每条为 `1080 / 1920 / 24fps`，时长约 5 秒。
4. 技术验收后把每个商品的三条成片放入本地 `outputs/server_reviews/<run-id>/`。
5. 汇报时提供本地文件路径、run ID、manifest 路径；不要把密钥、SSH 密码、签名链接或原始 API 响应写入日志或说明。

## 如果某条失败，只做定向修复

- 手/工具抖动：减少运镜，保留每镜头一个动作。
- 产品变形：优先重跑该条并保持原 reference stack，不用新产品替代。
- 人物/厨房跳变：确认 Character Scene 仍在本条静态 refs，且人物参考排在前。
- 汤变红/面条变细/灌汤包数量不对：用已生成的 `cook_state` 或 `hero_state` 重跑对应单条，不重写其余商品。
