# Which card, what it costs, what to set

Everything here was measured by us on the same clip: `shuizhu_beef_roll_clip_01`,
seed `202608090301`, six references in sequence order, `1088x1920`, 5.0s, 8 steps,
turbo. Nothing is taken from a spec sheet or a vendor claim.

## The table to read before renting

| | A100 SXM4 40GB | A100 PCIE 40GB | H100 SXM 80GB | H100 NVL 94GB |
| --- | --- | --- | --- | --- |
| Measured | 2026-08-10 | 2026-08-11 | 2026-08-11 | 2026-08-18 |
| Rented at | $0.713/hr | $0.836/hr | $2.311/hr | $2.712/hr |
| One 5s clip, 8 steps | 780 s | 907 s | **471 s** | 361 s ‡ |
| **$ per clip** | **$0.154** | $0.210 | $0.302 | $0.272 |
| One 15s ad, 3 clips + stitch | ~39 min | ~24 min † | **~24 min** | ~18 min |
| Power limit | 400 W | 250 W | 700 W | 400 W |
| Observed draw | - | 247 W, capped | 333 W idle-ish, 606-700 W under Sage | 394 W under Sage |
| VRAM peak at 1088x1920 | ~30 GB | 33.1 GB | 33.1 GB | 50 GB nvidia-smi ¶ |
| Sage attention fp8 | **impossible**, sm_80 | **impossible**, sm_80 | **yes**, 401 s (-15%) | **yes**, 320 s (-11.4%) |

† the whole ad including model load and stitching, which is why it is not
simply three times the clip time.

‡ **The H100 NVL clip is not the same clip as the other three columns.** It is
`kirin_straight_tea_clip_01`, two references, seed `2608189001`, model already
warm. Compare its 361 s only against its own 320 s sage run. Comparing it to the
471 s beside it would be comparing two different workloads.

¶ nvidia-smi total, which includes the allocator's cache; the other columns are
torch-reported peaks. Not the same metric, do not read a regression into it.

## How to choose

- **Cheapest per clip is the A100 SXM4.** If you are not in a hurry, this is the
  right card. The H100 buys wall-clock time, not money: it is 1.93x faster and
  43% more expensive per clip.
- **40 GB is enough.** Native `1088x1920` peaks at 33.1 GB, measured twice.
  Paying for 80 GB buys nothing on its own.
- **Read the power limit, not the TFLOPS number.** An A100 SXM4 and an A100 PCIE
  are the same silicon at the same memory bandwidth (1314.9 vs 1312.4 GB/s, 0.2%
  apart) and both advertise 15.6 TFLOPS. SXM4 is a 400 W part, PCIE is 250 W. The
  PCIE card sat at 247 W of its 250 W cap for an entire clip, clocking 1080 MHz
  against a 1410 MHz maximum, and took 16% longer. Renting it was a mistake made
  by comparing $/hr instead of $/clip.
- **Only Hopper can run the acceleration.** The fp8 Sage attention path needs
  sm_89 or newer. On any A100 it cannot run at all, so the only reason to pay
  H100 rates is speed plus that 15%.

## Settings, identical on every card

These are not card-dependent. They are the production settings and they are
measured, not preferred - see `h3-render-settings-are-measured`.

```
mode            r2v
size            1088x1920, cropped to 1080x1920 at the final encode
duration        5.0 s per clip, three clips per ad
steps           8
turbo           on, with turbo_low_vram
ref_image_size  match
audio           on: defaults.no_audio=false, final.keep_audio=true
```

**Do not drop to 6 steps to save time.** It is 33% faster, it passes
`check_clip_quality.py` with a *better* flip rate than the 8-step control, and it
rendered a napa cabbage whole and uncut. The gate cannot read the picture.

## Environment, same on every card

Driver 595.71.05 and the vast.ai PyTorch image gave torch 2.12.0+cu130 with the
venv at `/venv/main`, on both the A100 PCIE and the H100. Full install steps are
in `H200_DAY_PLAN.md`; the parts people miss:

- **KJNodes is not optional** if you want acceleration. `JR_H3_UnifiedAcceleration`
  delegates to `PathchSageAttentionKJ` and raises at execution time without it.
- **PyPI's `sageattention` is 1.x** and lacks the `sageattn_qk_int8_pv_*` entry
  points the node names. 2.x has to be built from source, and only on sm_89+.
- Models are about 60 GB. Download time is set by the host's link, not the card:
  13 minutes at 620 Mbps, under a minute at 15 Gbps.

## Cheap suppliers, and what the cheapness is buying

The 2026-08-09 provider was materially cheaper than Vast and supplied, per the
client, ex-mining cards. That is very likely the explanation for the two days
lost on 2026-08-10: two A100s from that provider, one after the other, corrupted
bf16 tensor-core GEMM at about 1.91e-10 per MAC while fp32, fp16 and bf16
elementwise stayed perfect. At the time the second failure looked like evidence
that the diagnosis was wrong, because replacing a faulty card is not supposed to
reproduce the fault exactly. A retired mining batch explains it: same wear, same
thermal history, same defect.

None of this is provable about those specific cards, and it does not need to be.
The operational conclusion is the same either way, and it inverts the intuition:

**A cheaper card needs the bf16 test more, not less.** The failure is silent. It
does not show up in nvidia-smi, in ECC counters, in Xid, in remapped rows, or in
a full VRAM sweep - all of those were clean. It shows up as a black clip after
thirteen minutes of paid sampling, intermittently, so a machine can pass one clip
and fail the next three. One minute of testing against hours of that.

Price the risk honestly when comparing suppliers: a card that is 40% cheaper and
fails one render in four is more expensive than the dear one.

## Before anything else

`bash server_scripts/check_bf16_mma.sh` must print `bf16 ... PASS`. It builds for
the card's own compute capability, so it handles sm_90 by itself; the prebuilt
`tools/bf16_check_sm80` binary is A100-only. Run it on every machine, every time,
including after a stop/start of the same instance.

That last clause is not caution, it is a measurement. On 2026-08-12 the H100 was
stopped and restarted, and came back with the same instance id, the same disk and
all 60 GB of models intact - but a different GPU. The UUID went from
`GPU-ffb151f0-...` to `GPU-c945196c-...`, so "same machine, already tested" was
false, and only reading the UUID revealed it.

**It does not happen every time, which is exactly why you have to read it.** On
2026-08-18 the H100 NVL was stopped and restarted and came back on the *same*
card, `GPU-95575316-...` both times, with the models and
the compiled SageAttention still in place. Two restarts, two different outcomes.
A rule of "restart always reassigns" would have wasted an acceptance run here,
and a rule of "restart never reassigns" cost two days in August. Neither rule is
the point: **record the UUID every time and compare it to the last one.** If it
changed, re-run the acceptance. If it did not, the previous PASS still stands.

## 开机那一小时真正花钱的地方（2026-08-18 实测）

租一台机器到能跑第一条片子，钱不是花在跑图上。这天从点 RENT 到模型就位，
GPU 时间大约 25 分钟，其中生成时间是 0。下面每一条都让那 25 分钟变长过。

### 镜像 tag 要对得上 compute capability

连点三次 RENT 全失败，红色 toast 一闪而过。原文是：

```text
no_compatible_tag error 400/4000: No compatible image tag found for
vastai/pytorch with compute capability 900 and CUDA version 13.2
```

Vast 的 `PyTorch (Vast)` 模板标签只有 `ARM SSH Jupyter`，**没有 CUDA 标签**，
它给 sm_90 解析不出镜像。换成带 `Cuda 13` 标签的 `PyTorch NGC` 之后，机器列表
自己从 5 台收敛到 3 台，一点就成。

当时页面上还挂着 Vast 自己的横幅 "adding enough credits to cover multiple days"，
我顺着它把失败推断成余额不足，又换了两台机器才回头去读错误原文。**页面上另一
条无关提示不是证据。**

### 镜像源跟着服务器走，不跟着人走

仓库里 `h3_server_setup.py` 的默认值是阿里云 PyPI + hf-mirror.com，那是给国内
机器准备的。这台在罗马尼亚，装之前先测了一轮：

| 端点 | 实测 | |
| --- | ---: | --- |
| pypi.org | 38.7 MB/s | 阿里云的 10 倍 |
| mirrors.aliyun.com | 3.7 MB/s | |
| huggingface.co | 78.0 MB/s | hf-mirror 的 1.5 倍 |
| hf-mirror.com | 52.9 MB/s | |
| download.pytorch.org | 119.3 MB/s | |

改成上游源之后，63 GB 模型下完用了 **9 分 04 秒**。用国内镜像至少多花十几分钟，
按 $2.712/hr 算就是白扔半美元多。这和 2026-08-11 那次 `download.pytorch.org`
在国内 5 KB/s 是同一条规律的两面：**先花 8 秒测速，再决定用哪个源。**

`--pypi-index` / `--hf-endpoint` / `--torch-index` 三个参数就是为这个留的，
默认值只对国内机器成立。

### 从 Windows 推脚本到 Linux：CRLF 会让退出码撒谎

第一次装机 **退出码 0，但什么都没装**。用 `python ... > file` 生成远端脚本时，
Windows 上 Python 的文本模式把 `\n` 写成了 `\r\n`，远端 bash 收到的第一行是
`set -euo pipefail\r`，于是报 `set: pipefail: invalid option name` —— `set -e`
从此没生效，后面每一行静默失败，最后照样给 0。

是靠 `ls /opt/` 发现目录根本不存在才抓到的。管道推脚本一律先 `tr -d '\r'`。

同一次还有 Git Bash 的 MSYS 路径转换：`--install-dir /opt/ComfyUI` 被改写成
`D:/Git/opt/ComfyUI`。要 `MSYS_NO_PATHCONV=1`。

### 一条贯穿今天的规律

租机器推断成余额问题、装机退出码 0、以及更早那次靠 billing 页面推断实例还在不在——
**三次都是拿间接信号代替直接验证。** 唯一有效的做法是每一步都去看那个东西本身：
实例状态看 Instances 页，装没装成看 `ls` 和 `find`，torch 能不能用就真去
`import torch; torch.cuda.is_available()`。退出码、页面横幅、进度条都不算数。
