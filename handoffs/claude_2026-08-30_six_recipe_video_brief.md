# Claude 执行说明｜2026-08-30 六份做菜视频素材

请基于仓库中已经准备好的参考图和 H3 prompt，制作今天的六组竖屏做菜素材。每组只做 **3 条独立 5 秒片段**，用于后期手动剪辑；不要自行拼接成长片。

## 统一交付规格

- 每组：`clip-01_1080x1920.mp4`、`clip-02_1080x1920.mp4`、`clip-03_1080x1920.mp4`。
- 先生成 `1088×1920`，再裁为精确 `1080×1920`；8 steps、Turbo、R2V、无原生音频。
- 每条 5 秒只有 3 个镜头，切点固定在约 `0.0–1.6s / 1.6–3.4s / 3.4–5.0s`。以每组 `sequence JSON` 与三个 `h3_prompts/clip_*.md` 为唯一镜头文本，不要自行改写流程。
- 全部无真人：不得出现人、手、脸、身体、倒影或影子。镜头稳定，优先锁定镜头、极小推近或小幅拉焦；不要晃动、跳景、食物变形或转场特效。
- 每一道都是**可操作的后厨**，不可出现吧台、餐厅座位、户外餐桌或摆拍沙发区。保留各自不同的厨房风格。
- 所有过程都要符合物理烹饪：原料状态、加热状态与成品状态必须连续；不出现同一盘食物的复制、塑料质感、凭空移动或不合食谱的配菜。

## 品牌与首帧边界（务必遵守）

1. 每组的 `scene_anchor` 已经带有桌牌；带实际商品的项目也已经带有准确包装/商品参考。请将这些**作为图像参考本身的可见信息**保留，不要替换、重绘、虚构包装或增加其他产品。
2. **视频 prompt 的文字中不要写公司名、品牌名、Logo、包装文字或招牌文字。** 这些识别内容只能从首帧参考图自然继承，画面中也不叠加字幕、水印、价格或文字特效。
3. 仅椰奶咖啡的首帧允许指定的黑黄椰奶纸盒；牛肉夹馍首帧以用户提供的夹馍成品外观为准。其余四道没有包装商品，不要凭空加入包装。

## 先打开的总文件

每个项目先打开对应的 sequence JSON；它已经绑定每条片段所需的 `scene_anchor / prep_state / cook_state / hero_state` 图片和 H3 prompt。

| 项目 | Sequence JSON | 预制作目录 |
|---|---|---|
| 椰奶咖啡 | `sequences/hainan_coconut_coffee_3x5_1080.json` | `sequence_outputs/hainan_coconut_coffee/preproduction/` |
| 牛肉夹馍 | `sequences/xian_beef_roujiamo_3x5_1080.json` | `sequence_outputs/xian_beef_roujiamo/preproduction/` |
| 港式西多士 | `sequences/hong_kong_french_toast_3x5_1080.json` | `sequence_outputs/hong_kong_french_toast/preproduction/` |
| 日本番茄酱蛋包饭 | `sequences/japanese_ketchup_omurice_3x5_1080.json` | `sequence_outputs/japanese_ketchup_omurice/preproduction/` |
| 印尼风味烤鸡腿 | `sequences/indonesian_grilled_chicken_leg_3x5_1080.json` | `sequence_outputs/indonesian_grilled_chicken_leg/preproduction/` |
| 家常双皮奶 | `sequences/homestyle_double_skin_milk_3x5_1080.json` | `sequence_outputs/homestyle_double_skin_milk/preproduction/` |

每个预制作目录都含：

- `storyboard.md`：分镜和每段 3 镜头动作；
- `recipe_bible.md`、`recipe_sources.md`：食谱与禁忌；
- `h3_prompts/clip_01_ref2va.md` 至 `clip_03_ref2va.md`：直接使用的文案；
- `reference_prompts/`、`reference_manifest.json`：参考图说明与路径。

## 六组内容锁定要求

### 1. 椰奶咖啡

- 参考图：`outputs/reference_assets/48_hainan_coconut_coffee/generated/`；首帧准确纸盒源文件为 `outputs/reference_assets/48_hainan_coconut_coffee/source_products/hainan_coconut_milk_carton.png`。
- 场景是海绿色水磨石操作台、金属咖啡机与厨房置物架的**海南咖啡后厨**，不是咖啡吧台或户外。
- Clip 1 必须从更新后的竖屏 `hainan_coconut_coffee_scene_anchor-1.png` 起：完整纸盒在画面左侧、完整桌牌在右后方、空玻璃杯与冰咖啡食材在中间。镜头一开始不能裁掉、替换或凭空移走参考图已有物品；视频文字不写包装或品牌名称。
- 过程：透明冰块 → 深色咖啡 → 椰奶慢倒形成自然褐白羽状融合 → 冷饮成品。不要搅打成奶昔；不要珍珠、奶油顶、吸管或水果。

### 2. 西安牛肉夹馍

- 参考图：`outputs/reference_assets/49_xian_beef_roujiamo/generated/`；用户提供的成品形状参考为 `outputs/reference_assets/49_xian_beef_roujiamo/source_products/beef_roujiamo_product_reference.png`。
- 石灰岩、玄武岩、黑铁鏊子的西安后厨。圆馍必须有清晰烤制层次，不是汉堡面包、墨西哥饼或西式三明治。
- 过程：已卤熟的牛肉切成不规则 8–12 mm 小块，与 8–10 mm 鲜青椒块分开备好 → 热黑锅中先煸牛肉、再下青椒 → 沿锅边少量生抽快速收成薄褐色挂汁 → 圆馍烙至金黄酥层、开口填入。牛肉必须是有肉纤维的块，青椒脆绿，馅湿润但不流汤；不要肉末糊、深色酱汁、芝士、蛋黄酱、生菜、番茄。

### 3. 港式西多士

- 参考图：`outputs/reference_assets/50_hong_kong_french_toast/generated/`。
- 薄荷绿墙板、琥珀色备餐台、黑色平底锅和铬色厨房置物架的茶餐厅**后厨**；不能有卡座、餐厅桌椅。
- Clip 1 必须先静止、完整地展示分开的两片厚吐司、花生酱碗、蛋液碗、黄油、炼乳和空平底锅，再涂花生酱并合成干的夹心吐司。Clip 2 才蘸蛋液和浅油煎制，Clip 3 才加黄油和炼乳。成品切面需有清晰花生酱层；不要果酱、巧克力、芝士、水果、冰淇淋或糖浆湖。

### 4. 日本番茄酱蛋包饭

- 参考图：`outputs/reference_assets/51_japanese_ketchup_omurice/generated/`。`hero_state-1.png` 是最新认可的自然成品图，务必以它为主。
- 深棕 Formica 操作台、奶油圆形瓷砖、小煎锅灶台的东京 kissaten **后厨**；没有就餐卡座。
- 过程：熟鸡腿小丁、洋葱、蘑菇、隔夜饭与番茄酱炒出粒粒分明的橙红炒饭 → 煎出柔软薄蛋皮 → 低矮饭团用带轻微手工褶皱的蛋皮覆盖，前缘可自然微露炒饭。
- 成品不可做成气球般蓬松的黄蛋枕，也不可镜面塑料感。番茄酱只有一条细、短、自然不规则的线；禁止字样、粗红带、酱汁积水、芝士和沙拉。

### 5. 印尼风味烤鸡腿（Ayam Bakar）

- 参考图：`outputs/reference_assets/52_indonesian_grilled_chicken_leg/generated/`。
- 爪哇开放式炭烤后厨：赤陶操作台、钴蓝蜡染纹瓷砖、浅腌制托盘和低矮炭炉；风格必须与其他厨房不同。
- 过程：整只带骨鸡腿在浅盘中覆以红葱头、蒜、姜、姜黄、香菜籽、香茅和甜酱油香料 → **直接放上中火炭炉**烤熟 → 分次薄刷甜酱油，形成深红木色、局部轻焦的全熟鸡腿。
- 全片不得出现锅、炒锅、汤锅、焖锅、炖煮液或烤箱。不要裹粉、黑焦一片、粉红生肉、厚重酱汤或米饭大堆；成品只配少量青柠、参巴酱与黄瓜片。

### 6. 家常双皮奶

- 参考图：`outputs/reference_assets/53_homestyle_double_skin_milk/generated/`。
- 顺德甜品后厨：蜂蜜色橡木、乳白搪瓷、黄铜细节、浅青瓷碗与蒸锅。
- 过程：鲜奶加热形成第一层奶皮并倒出奶液 → **近景：两枚鸡蛋已经打在稳放的玻璃碗中，蛋黄完整、蛋清为微黄半透明；不能悬空、不能出现手** → 硬切到分离完成的微黄蛋清玻璃碗，蛋黄另置小白碗 → 蛋清加入回温奶和糖后仅轻打至均匀、无泡沫 → 细筛后沿碗壁回注奶皮下方 → 碗口覆紧保鲜膜、只扎 2–3 个小孔 → 放入同一只不锈钢蒸锅轻蒸定型 → 温热成品。Clip 2 必须依次加载 `homestyle_double_skin_milk_cracked_egg_state-1.png`、`homestyle_double_skin_milk_prep_state-1.png`、`homestyle_double_skin_milk_egg_white_mix_state-1.png`。奶皮要完整、细薄、无气泡、无裂纹、无水珠。
- 保持纯双皮奶：不要水果、红豆、珍珠、果冻、奶油或夸张摆盘。

## 交付前最低技术检查

- 每条都是 5 秒、1080×1920、无音频，并能独立播放。
- 逐一检查 18 条片段是否有手、人、文字、假包装、场景跳变、食物融化/变形、错误熟度或不连续烹饪状态；有任一项即重跑该条，不调整其他已通过的片段。
- 交付路径和 clip 名称请清楚列出，不要只给拼接预览。
