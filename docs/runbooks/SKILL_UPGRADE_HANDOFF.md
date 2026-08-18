# 交接：viral-creative-rewrite-skill 的四项修改

写给接手改这个 skill 的人。**全部是文本/代码活，不需要 GPU，不需要开机器。**

背景：2026-08-18 用这套流程做了一条 Kirin 午後の紅茶 Straight Tea 的 15.5 秒复刻广告，
成片在 `local_artifacts/kirin_straight_tea_rewrite/final/kirin_straight_tea_sage_1080x1920.mp4`。
片子是好的，但**好的地方基本都不是 skill 给的** —— 是手工补出来的。下面四条就是
把那些手工步骤固化进 skill。

改完的验收标准写在每一节末尾，都可以离线跑。

---

## 现状：skill 生成的 prompt 过不了自己的校验器

```bash
python prompts/validate_prompt.py sequence_outputs/viral-rewrite/20260818_152021/h3-package/prompts/clip-01_ref2va.md
```

```text
FAIL clip-01_ref2va.md
  ! detailed_description is 200 words, want 350-500
```

三段都是 199-200 词。**格式全对**（六段、`fully_preserved` 标记词、
`[Shot 2] At 00:01.600,` 时间码），所以不要动格式，只动内容。

`prompts/H3_OFFICIAL_PROMPT_SPEC.md` 是格式的权威来源，350-500 词那条出自那里。

---

## 修改 1：把分镜模板从"菜单"改成"必须指定"

**位置**：`viral-creative-rewrite-skill/viral-creative-rewrite-skill/scripts/h3_runtime.py`
函数 `_h3_prompt_for_clip`（约 209 行），`shot_1` / `shot_2` / `shot_3` 三个字符串
（约 227 / 232 / 237 行）。

**现在 shot 2 写的是**：

```text
Show one physical proof action only: a pour, lift, texture reveal, hand placement,
use motion, or product-state change that completes inside this shot.
```

这是给模型一份**可选项清单**。H3 会自己挑一个，于是每条片子的第二镜都不一样，
而且经常挑到和这一段身份不符的那个。

**要改成**：模板必须强制填入**具体的一个动作**、**具体的物体位置**、
**具体的进出画方向**。参考今天实际生效的写法
（`local_artifacts/kirin_straight_tea_rewrite/prompts/clip-01_opening_product_identity.md`）：

```text
[Shot 1] ... A realistic adult hand enters from the left edge holding the bottle of
<Picture 1> upright by its red label, carries it in over the green surface, sets it
down squarely on the wood riser and withdraws to the left out of frame. The camera
pushes in about 4 cm across the whole shot, one continuous move that never pauses
and never reverses. The shot ends with the bottle standing alone on the riser.
```

要点：进画方向、握持位置、落点、退出方向、镜头运动的量和连续性、**这一镜结束时画面里是什么**。

**同时把字数推到 350-500。** 现在 200 词，缺的 150-300 词应该花在：每镜的结束状态、
物体在三镜之间的位置追踪、以及下面第 3 条的正面画面陈述。不要靠灌形容词凑数。

**验收**：

```bash
python prompts/validate_prompt.py <新生成的 clip-01_ref2va.md>
# 必须 0 failed，且不再报 word count
```

---

## 修改 2：单个物体要跨三镜头显式追踪

**位置**：同上，三个 shot 字符串。

今天 clip 02 第一版画面里出现了**两支瓶子**。原因是 prompt 自己矛盾：
shot 1 和 shot 3 写了"瓶子立在后面的木座上"，shot 2 又写"瓶子从右上角进画倾倒"。
模型没法同时满足，就渲染了两支。

**修法不是加"only one bottle"这种否定句**（否定词在 H3 上基本无效，本仓库已记录十余次），
而是把这一个物体的位置在三镜之间显式接续：

```text
[Shot 1] ... The single bottle of <Picture 1> stands on the light-wood riser behind
the glass and stays there for this whole shot.
[Shot 2] ... That same bottle has been lifted off the riser and enters from the upper
right ... The riser behind it is now empty, because there is only ever this one bottle.
[Shot 3] ... The one bottle has been set back down and stands again on the riser behind.
```

改完之后重跑就没有第二支瓶子了。

**模板层面要做的**：给 `_h3_prompt_for_clip` 一个"主体物体位置状态机"的概念 ——
每一镜都必须声明主体在哪、以及上一镜之后它怎么移动过来的。

---

## 修改 3：正面陈述画面内容，并用产品自己的原料打底

**位置**：同上，以及 `_h3_prompt_for_clip` 末尾那段 `Preserve across all shots: ...
Avoid template product leakage, fake labels, invented text, ...`。

**3a. 否定词无效，要正面陈述。** 今天 clip 02 的 prompt 里明明写了
`avoid fruit slices, citrus`，画面里还是出现了两个柠檬半切。改成正面陈述之后就干净了：

```text
Everything in frame across all three shots: the background of <Picture 4>, one
light-wood riser, exactly one bottle of <Picture 1>, one tumbler, clear ice, one pair
of tongs, one adult hand, and bare surface around them.
```

**现在那段 `Avoid ...` 列表要保留**（它挡住了字幕、水印、假标签这些），
但**必须在它前面加一句"画面里有且只有以下这些"的正面清单**。

**3b. 用产品自己的原料给底座打底。** 这是客户看片时指出的：模板里每一段的杯子和瓶子
脚下都铺着那个口味的原料 —— 梨和马蹄、青柠、乌龙的干茶叶。那是模板的一个结构手法：
用原料给产品垫底，一眼说清这瓶东西是什么做的。

我们复刻时把"不继承梨/小青柠/枇杷/乌龙茶"执行对了，但**"借结构"这半条只做了一半**：
clip 03 有干茶叶，clip 01 和 02 的台面是光的。

**正确规则**：借这个手法，但换成**我们产品自己的原料**。Straight Tea 的标签上印着
`ディンブラ茶葉`（斯里兰卡 Dimbula 锡兰红茶），所以底座应该散一层干红茶叶。
牛奶产品就是别的，果汁产品就是那种水果。

**模板层面要做的**：在 rewrite brief 里增加一个必填槽位 —— "这个产品的原料是什么，
用它给底座打底"，并把它写进每一镜的画面清单。

---

## 修改 4：参考图的转移范围要逐条写明，不能用通用句

**位置**：`scripts/h3_runtime.py` 的 `_reference_declarations`（约 187 行）。

**现在非产品图一律生成这一句**：

```text
<Picture N>: attribute_transfer. Use only the relevant scene, character, action-state,
lighting, or material attributes; do not invent text.
```

"relevant" 是空的 —— 它没说哪些转移、哪些不转移。

参考图之间**会互相投票**。今天的实例：clip 02 绑了四张图，其中底板图给正确的哑光绿，
而冰块图自带一片更亮的绿，底板是 4 票里的 1 票，结果绿色渲歪了。

**正确写法是把转移范围写死，并显式声明什么不转移**：

```text
<Picture 3>: attribute_transfer. How the stream holds together and folds over ice
transfers. Its framing and its darker colour do not; the tea in this clip is the
lighter transparent amber of <Picture 1>.

<Picture 2>: partially_preserved. The tumbler shape, the ice, the light-wood block and
the dry loose tea leaves scattered across it carry over exactly. Its background and its
framing do not.
```

**模板层面要做的**：`_reference_declarations` 不能再对所有非产品图套同一句。
每张参考图入包时必须带上"转移什么 / 不转移什么"两个字段，由准备阶段填写。

**另外提醒**：现在的实现把**产品图放在最后一个 `<Picture N>`**，今天手写的包把产品图放
`<Picture 1>`。两种都行，只要 sequence JSON 里 `ref_images` 的顺序对得上，
因为绑定是位置性的。**不要以为这是 bug 去"修"它。**

---

## 修改 5（可选，收益最大但工作量也最大）：把模板参考图流程固化

今天成片质量的一大半来自这一步，skill 现在完全没有。

`scripts/extract_video_frames.py` 已经存在，但 skill 只把它用于**分析**
（1fps 抽帧看内容），没有用它**产出真正绑定给 H3 的参考图**。

今天手工做的流程，可以脚本化：

1. **按原生分辨率重抽**。`local_artifacts/sample_rewrite_frames/` 那批是 360x640 的缩略图，
   当参考图太糊。要用 `ffmpeg -ss <t> -i source.mp4 -frames:v 1` 从源片抽 720x1280。
2. **裁掉污染物**。模板帧里几乎每一张都带着别人的产品、别人的水果、以及后期烧上去的
   英文字。这些不裁掉，H3 会照着渲染出来 —— 参考图永远打赢文字描述。
3. **采样颜色，不要用形容词**。今天把 `saturated green tabletop` 写进 prompt，
   渲出来是抠像绿：模板是 RGB(181,213,147)，渲染是 RGB(51,209,116)，
   **"saturated" 一个词让红通道掉了 130**。用 Pillow 采一下几行代码的事。
   改成描述真实颜色 + 绑一张干净底板图之后，渲染是 RGB(181,214,141)，基本逐点命中。
4. **裁掉东西之后必须补一句那里是什么**。今天把冰块参考图的绿色带裁掉，绿色对了，
   但模型在空出来的背景里**自己发明了一块带柠檬插画的白色木框招牌**。
   这和之前"解绑 logo 参考图后模型自造了一块 TOM YUMS 招牌"是同一条规律：
   **移除一张图不等于声明那里没有东西。**

细节全部记录在
`local_artifacts/kirin_straight_tea_rewrite/README_PROMPT_NOTES.md` 和
`.claude/skills/dish-difficulty/SKILL.md`。

---

## 总验收

改完之后，跑一次 dry-run 生成，然后：

```bash
python viral-creative-rewrite-skill/viral-creative-rewrite-skill/scripts/confirm_generation.py \
  --prepared-input-json <prepared.json> --ui-language zh --h3-dry-run

python prompts/validate_prompt.py <生成的 h3-package/sequence.json>
```

**必须 3 passed, 0 failed。** 现在是 0 passed, 3 failed。

不要为了过校验器而灌水凑字数 —— 字数是结果不是目标。判断标准是：
**把生成的 prompt 读一遍，能不能照着它把这条片子拍出来。**
现在的版本读完你不知道第二镜要拍什么。
