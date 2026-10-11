# 给 Claude：五组竖版做菜视频重做说明

请在 `C:\Users\uryuu\Desktop\comfyui_workflow` 工作。只重做以下五组，不要重做日本番茄酱蛋包饭。

## 全局交付规则（全部必须遵守）

- 每个片段独立生成：5 秒、R2V、8 steps、Turbo、无原生音频、生成尺寸 1088×1920，最后裁切为 1080×1920。不可横屏，不拼接成长视频。
- 仅使用各 `outputs/reference_assets/.../generated/` 下的竖版参考图；`source_products/` 内原图只是素材输入，**绝不能作为最终横屏/方形参考帧交付**。
- 厨房、器皿、台面、光线和菜品状态在同一菜的三个 Clip 内必须一致。
- 不要真人、手、人体、倒影、人影或人物阴影。
- H3 视频提示词正文不能出现公司名、Logo、品牌名、包装文字或桌牌说明；首帧中的包装和实体桌牌只由已经提供的视觉参考图带入，不要靠文字重新生成。
- 不要字幕、价格、UI、水印、假包装文字。所有食材重力、液体、火候必须真实。

## 1. 椰奶咖啡：只重做 Clip 1

执行文件：

- `sequences/hainan_coconut_coffee_3x5_1080.json`
- `sequence_outputs/hainan_coconut_coffee/preproduction/h3_prompts/clip_01_ref2va.md`
- 首帧：`outputs/reference_assets/48_hainan_coconut_coffee/generated/hainan_coconut_coffee_scene_anchor-1.png`

该首帧已经是竖版。必须完整保留左前方的准确椰汁纸盒和右后方实体桌牌；不要用任何横屏商品源图替代它。后续动作仍在同一厨房完成咖啡与椰奶分层。

## 2. 西安牛肉夹馍：重做 Clip 1、Clip 2

执行文件：

- `sequences/xian_beef_roujiamo_3x5_1080.json`
- `sequence_outputs/xian_beef_roujiamo/preproduction/h3_prompts/clip_01_ref2va.md`
- `sequence_outputs/xian_beef_roujiamo/preproduction/h3_prompts/clip_02_ref2va.md`
- 新过程图：`outputs/reference_assets/49_xian_beef_roujiamo/generated/xian_beef_roujiamo_{prep_state,cook_state}-1.png`

流程必须是：已经卤熟、8–12 mm、不规则有纤维感的牛肉块 + 8–10 mm 鲜绿中块青椒 → 热黑铁锅快速翻炒 → 锅边少量生抽形成很薄的亮汁 → 烤馍、填入馅料。不要肉末、不要牛肉糊、不要汤汁、不要红烧大锅。青椒不是碎丁。

## 3. 港式西多士：重做 Clip 1、Clip 2

执行文件：

- `sequences/hong_kong_french_toast_3x5_1080.json`
- `sequence_outputs/hong_kong_french_toast/preproduction/h3_prompts/clip_01_ref2va.md`
- `sequence_outputs/hong_kong_french_toast/preproduction/h3_prompts/clip_02_ref2va.md`
- 新过程图：`outputs/reference_assets/50_hong_kong_french_toast/generated/hong_kong_french_toast_{scene_anchor,prep_state,cook_state}-1.png`

Clip 1 一开始必须是**未组装、分开摆放**的食材：吐司片、花生酱小碗、蛋液碗、黄油与炼乳，均在同一个后厨台面；随后才抹花生酱、合上吐司。Clip 2 才把夹好的吐司蘸蛋液并煎成金黄。不要餐厅卡座、人物、乱序食材或无故出现成品。

## 4. 印尼风味烤鸡腿：重做 Clip 1、Clip 2、Clip 3

执行文件：

- `sequences/indonesian_grilled_chicken_leg_3x5_1080.json`
- `sequence_outputs/indonesian_grilled_chicken_leg/preproduction/h3_prompts/clip_01_ref2va.md`
- `sequence_outputs/indonesian_grilled_chicken_leg/preproduction/h3_prompts/clip_02_ref2va.md`
- `sequence_outputs/indonesian_grilled_chicken_leg/preproduction/h3_prompts/clip_03_ref2va.md`
- 新参考图：`outputs/reference_assets/52_indonesian_grilled_chicken_leg/generated/indonesian_grilled_chicken_leg_{scene_anchor,prep_state,cook_state,hero_state}-1.png`

这是爪哇开放式炭烤厨房。鸡腿先在浅盘里腌红葱头、蒜、姜、姜黄、香菜籽、香茅、甜酱油，之后**直接放在中火炭炉上烤熟**，分次薄刷甜酱油。成品为全熟深红木色、局部轻焦的带骨鸡腿。不得出现锅、炒锅、汤锅、焖锅、烤箱、炖煮液、粉红生肉、厚重汤汁或大堆米饭。

## 5. 家常双皮奶：重做 Clip 1、Clip 2、Clip 3

执行文件：

- `sequences/homestyle_double_skin_milk_3x5_1080.json`
- `sequence_outputs/homestyle_double_skin_milk/preproduction/h3_prompts/clip_01_ref2va.md`
- `sequence_outputs/homestyle_double_skin_milk/preproduction/h3_prompts/clip_02_ref2va.md`
- `sequence_outputs/homestyle_double_skin_milk/preproduction/h3_prompts/clip_03_ref2va.md`
- 关键新图：`outputs/reference_assets/53_homestyle_double_skin_milk/generated/homestyle_double_skin_milk_{cracked_egg_state,prep_state,egg_white_mix_state,cook_state,hero_state}-1.png`

固定同一间顺德家常甜品厨房、蜂蜜色木台面、青瓷碗和同一只不锈钢蒸锅。真实顺序：

1. 鲜奶加热后在青瓷碗形成第一层奶皮，倒出奶液但保留奶皮。
2. **近景：两枚鸡蛋已经打在落地的玻璃碗中**，完整蛋黄浸在微黄、半透明的蛋清中；旁边有空小白碗。不能有蛋、蛋壳或液体悬空，不能有手。
3. 硬切到分离完成：微黄半透明蛋清在玻璃碗，蛋黄在独立白碗。
4. 蛋清加回温奶和糖，只轻打到均匀无泡。
5. 细筛，沿青瓷碗内壁回注到奶皮下方；奶皮完整浮回表面。
6. 保鲜膜覆紧，只扎 2–3 个小孔；同一只蒸锅轻蒸定型。
7. 成品是无气泡、无裂纹、无水珠的温热丝滑双皮奶；不要水果、红豆、珍珠、果冻、奶油或夸张装饰。

## 提交前检查

- 逐条确认所有输入是竖版 `generated` PNG，而非 `source_products`。
- 严格按 JSON 中每个 Clip 的 `ref_images` 顺序加载；双皮奶 Clip 2 的新增 `cracked_egg_state`、`prep_state`、`egg_white_mix_state` 不可遗漏。
- 生成前后均运行：

```powershell
D:\anaconda\python.exe prompts\validate_prompt.py sequences\hainan_coconut_coffee_3x5_1080.json sequences\xian_beef_roujiamo_3x5_1080.json sequences\hong_kong_french_toast_3x5_1080.json sequences\indonesian_grilled_chicken_leg_3x5_1080.json sequences\homestyle_double_skin_milk_3x5_1080.json
```

不要改写现有菜品逻辑、不要补编品牌、不要补编人物；按这份清单生成即可。
