# MiniMax H3 H100 Migration Cheat Sheet

`MIGRATION_A100_H3.md` 的 H100 版。那份记的是老式 conda 环境、`768x1344`、
`steps=4` 的过时生产配置；这份记的是 Vast.ai `PyTorch NGC` 镜像 + H100 NVL 的
实际装机过程，包括一个那份文档完全没遇到过的坑。**卡的性能对比、$/clip、
Sage attention 提速数字看 `GPU_CARD_REFERENCE.md`，这里只管"怎么把一台新
H100 从零装到能跑图"。**

Do not store SSH passwords or API keys in this file.

## 用的镜像

Vast.ai 模板选 **`PyTorch NGC`**（`nvcr.io/nvidia/pytorch_26.01-py3`），
不是 `PyTorch (Vast)`——后者没有 CUDA 标签，给 sm_90 解析不出镜像 tag，
点 RENT 会直接报 `no_compatible_tag`，详见 `GPU_CARD_REFERENCE.md`。

装出来是：

```text
Ubuntu: 24.04
Python: 3.12（系统自带，ComfyUI venv 建在 /opt/ComfyUI/venv）
PyTorch: 2.13.0+cu130（torch.version.cuda 报 13.0）
CUDA runtime available: True
ComfyUI: /opt/ComfyUI, v0.30.2
API: 127.0.0.1:8189
```

**2026-08-22 补充：Vast 上不一定真的给你这个模板。** 两次单独租的 H100 NVL
实例，模板选的都是 Vast 那个大杂烩 `ComfyUI` 模板（`/workspace/ComfyUI`，
torch 2.10.0+cu128），不是字面意义上的 `PyTorch NGC`。不要为了凑镜像名字重
新租——下面这条"原地升级"的路子在这种模板上照样能走通，而且更快，见
`如果拿到的不是 NGC 镜像` 一节。

## 一个这个镜像特有的坑：nvcc 和 torch 的 CUDA 版本对不上

`torch.version.cuda` 报 `13.0`，但镜像自带的系统 CUDA toolkit **只有 12.9**：

```bash
which nvcc            # 空的，不在 PATH 上
ls -d /usr/local/cuda*
# /usr/local/cuda /usr/local/cuda-12 /usr/local/cuda-12.9   <- 没有 13.x
```

平时用预编译的 torch 算子不会碰到这个问题，但**从源码编译任何 CUDA 扩展会**——
这次是 SageAttention 2.x。第一次编译直接报：

```text
RuntimeError: ('The detected CUDA version (%s) mismatches the version that
was used to compile PyTorch (%s). Please make sure to use the same CUDA
versions.', '12.9', '13.0')
```

**修法**：装一个精确匹配 torch 版本的 CUDA toolkit。镜像自带的 apt 源里已经配好了
NVIDIA 的 CUDA repo（`/etc/apt/sources.list.d/cuda.list` 现成的，不用自己加），
直接能装到 `13-0`：

```bash
apt-get update -qq
apt-get install -y --no-install-recommends cuda-toolkit-13-0
```

**不要只装 `cuda-nvcc-13-0` + `cuda-cudart-dev-13-0` 想省时间**——试过，
省不下来。SageAttention 的 `fused.cu` 要 `cusparse.h`，那个在 cuBLAS/cuSPARSE
的 dev 包里，minimal 组合没有，会在链接前一步炸：

```text
fatal error: cusparse.h: No such file or directory
```

装完整的 `cuda-toolkit-13-0` 元包（连头文件带全部数学库），一次到位。
在这台 150GB 盘的机器上，装完整工具链之后总占用到 89G，还有 62G 余量，
不是什么要省的地方。

## 编译 SageAttention 2.x

装完匹配的 CUDA toolkit 之后，编译要显式指定 `CUDA_HOME`，因为系统默认还是
指向那个 12.9 的：

```bash
cd /opt/ComfyUI && . venv/bin/activate
cd /root/SageAttention   # git clone thu-ml/SageAttention 到这

export CUDA_HOME=/usr/local/cuda-13.0
export PATH=/usr/local/cuda-13.0/bin:$PATH
export EXT_PARALLEL=8 NVCC_APPEND_FLAGS="--threads 8" MAX_JOBS=32
export TORCH_CUDA_ARCH_LIST="9.0"

python -m pip install --no-build-isolation -v . > /root/sage_build.log 2>&1
```

**编译日志一定要落盘到文件，不要只看管道尾部。** 第一次失败时我用
`| tail -25`，把真正的编译器报错（那句 `fatal error: cusparse.h`）挤没了，
只剩 pip 的通用摘要 `No available output`，白白多花一轮才找到真因。

验证装没装成，**必须换一个不是 `/root/SageAttention` 的目录**，否则 Python
会导入源码树而不是装好的包，报一个跟真实原因无关的假错误
（`cannot import name '_fused'`，因为 `_fused` 是编译产物，只在 site-packages
里，源码树里没有）：

```bash
cd /tmp && python -c "
import sageattention as s
print(sorted(n for n in dir(s) if n.startswith('sageattn')))
"
```

装成后应该看到 `sageattn_qk_int8_pv_fp8_cuda_sm90`——这就是
`JR_H3_UnifiedAcceleration` 节点点名要的那个。

## 如果拿到的不是 NGC 镜像：原地把 torch 升到 cu130

2026-08-22 在 Vast 的 `ComfyUI` 大杂烩模板上验证过、成功的路径。这个模板一台
机器上塞了七八个 app（ComfyUI、ACE-Step、Wan2GP、forge、unsloth……），每个都
有自己的 venv（`/venv/comfyui`、`/venv/main`、`/venv/forge`……），但**这些
venv 不是互相独立的**：

```bash
cat /venv/comfyui/lib/python3.12/site-packages/*.pth
# /venv/main/lib/python3.12/site-packages
```

`/venv/comfyui` 自己的 `site-packages` 里只有 torch 的 dist-info（元数据），
真正的包体在 `/venv/main`，靠这条 `.pth` 追加到 `sys.path` 里借用。
`torch.__file__` 能验证：

```bash
/venv/comfyui/bin/python -c "import torch; print(torch.__file__)"
# /venv/main/lib/python3.12/site-packages/torch/__init__.py
```

**不要因此去改 `/venv/main`**——那是其他 app 共用的底座，谁知道 unsloth 或
forge 有没有钉死某个 torch 版本。正确做法是直接在 `/venv/comfyui` 自己的
site-packages 里装一份新的，Python 的 `sys.path` 顺序保证自己的目录排在
`.pth` 追加的路径前面，装了就会被优先命中，不用碰 `/venv/main`：

```bash
/venv/comfyui/bin/python -m pip install --upgrade torch torchvision torchaudio \
  --index-url https://download.pytorch.org/whl/cu130
```

装完验证版本、CUDA 可用、`cu130 optimized CUDA operations` 那条警告消失：

```bash
/venv/comfyui/bin/python -c "import torch;print(torch.__version__, torch.version.cuda, torch.cuda.is_available())"
# 2.13.0+cu130 13.0 True
```

**顺序不能反：先升 torch，再装匹配的 CUDA toolkit，最后编 SageAttention。**
2026-08-22 就在这上面吃过一次亏：先用 cu128 配的 `cuda-toolkit-12-8` 编了一
遍 SageAttention，编到一半才想起要把 torch 也升到 cu130，只能把整个编译进
程树 `kill -9` 掉重来（`pkill -f` 在这个环境里匹配到自己的 SSH 命令行，报
`exit 127`，改成记下 PID 直接 `kill -9 <pid...>` 才行）。torch 版本一变，
之前编的 `.so` 就跟新 torch 的 ABI 对不上，等于白编。升级 torch 之后重新走
一遍装 CUDA toolkit 那步（这次是 `cuda-toolkit-13-0`，跟 cu130 对齐），
`CUDA_HOME` 也要跟着改成 `/usr/local/cuda-13.0`：

```bash
apt-get install -y --no-install-recommends cuda-toolkit-13-0
cd /root/SageAttention && rm -rf build
export CUDA_HOME=/usr/local/cuda-13.0 PATH=/usr/local/cuda-13.0/bin:$PATH \
       EXT_PARALLEL=8 NVCC_APPEND_FLAGS="--threads 8" MAX_JOBS=32 TORCH_CUDA_ARCH_LIST=9.0
/venv/comfyui/bin/python -m pip install --no-build-isolation -v . > /root/sage_build.log 2>&1
```

**验证注册成功，不能只信 `import sageattention` 成功。** Python import 成
功只说明包能被导入，不说明 ComfyUI 的自定义节点加载器真的把
`JR_H3_UnifiedAcceleration` 注册进了节点表——这是两回事，2026-08-21 那晚就
没验过后半段。真正的验收是直接查 `/object_info`：

```bash
curl -s http://127.0.0.1:8189/object_info | /venv/comfyui/bin/python3 -c "
import json,sys
d=json.load(sys.stdin)
print('JR_H3_UnifiedAcceleration' in d)
"
```

**实测效果比文档里单独的 Sage -11% 大得多。** 同一条生产流水线（1088x1920、
8步、6参考图、`turbo_low_vram: true`），从"cu128 + 服务端 `--lowvram`+ 无加
速"（~800s/clip，2026-08-21 基线）换到"cu130 + 不开 `--lowvram` + Sage 加
速"（~470s/clip，2026-08-22 实测），**快了约 41%**。这不是同一条 clip、同一
个 seed 测的，达不到 `GPU_CARD_REFERENCE.md` 表格要求的逐字节可比标准，所以
没有把这个数字填进那张表——但差距大到可以确定：大头来自去掉不必要的
`--lowvram`（H100 NVL 95GB 显存本来就不需要 async weight offload）和 cu130
优化路径生效，Sage 加速是在这基础上再叠加的一小块，不是全部。

## 模型和节点

跟 `GPU_CARD_REFERENCE.md` 里的流程一致，7 个文件（5 个模型 + Turbo LoRA +
Turbo 节点自带的一个小文件），装完用 `server_scripts/check_model_integrity.sh`
对照 `server_scripts/model_manifest.sha256` 校验，这台机器验过是 **7/7 全绿**。

节点：`ComfyUI-KJNodes`、`ComfyUI-MiniMax-H3-Turbo`、`ComfyUI_JR_MiniMaxH3Node`。

## 起服务、开隧道

```bash
cd /opt/ComfyUI
nohup venv/bin/python main.py --listen 127.0.0.1 --port 8189 > /root/comfyui.log 2>&1 &
```

**`--listen` 用 `127.0.0.1`，不要用 `0.0.0.0`。** 这次装机图省事写了
`0.0.0.0`，效果是这台机器的 8189 端口只要 Vast 那边有暴露（Instance Portal 代理
经常会自动探测常见端口），任何人打开对应的公网地址就是同一个 ComfyUI 进程、
同一条采样队列、同一张卡。本地窗口和外部窗口是在抢同一个 GPU，不是各跑各的——
如果发现"开了个新窗口速度就变慢"，先查 `curl http://127.0.0.1:8189/queue` 里
`queue_running` 是不是变成了 1 个以上，而不是怀疑配置本身变了。

本地连接一律走 SSH 隧道，不依赖公网端口：

```bash
ssh -p <port> -N -L 8189:localhost:8189 -o ServerAliveInterval=15 -o ServerAliveCountMax=3 -o BatchMode=yes root@<host>
```

`<port>` 每次重开实例都会变（这台先后是 17745、12091、31383），去 Vast 的
"SSH connection" 按钮现取，不要复用上一台的。加 `ServerAliveInterval` 是
2026-08-22 吃过亏之后补的：长跑批次中途隧道断过一次（`exit 255`），本地这边
`h3_sequence_runner.py` 直接报 `ConnectionResetError` 退出。

### 隧道断了不代表 GPU 上的任务死了

**远端 ComfyUI 收到请求之后是独立跑的，本地隧道断了不会杀掉它。** 断线那次
远端还在正常采样，`nvidia-smi`、`ps` 都能证明 `main.py` 进程活着、GPU 在算。
处理步骤：

1. 重开隧道，`curl http://127.0.0.1:8189/queue` 确认 `queue_running` 里那条
   还在跑，记下 `filename_prefix` 认出是哪条 clip。
2. **不要立刻重跑**——等 `queue_running` 变空（那条任务真正跑完），用
   `/history/<prompt_id>` 查它的 `outputs`，拿到 `filename` / `subfolder`，
   直接用 `/view` 端点把已经算完的成片下载下来，不用重新采样一遍：

   ```bash
   curl -s "http://127.0.0.1:8189/view?filename=<filename>&subfolder=<subfolder>&type=output" \
     -o <local_clip_dir>/<filename>
   ```

3. 把文件放进 `h3_sequence_runner.py` 期望的那个 clip 目录（跟断线前那次的
   `run_id` 时间戳目录对齐），然后带上 `--run-id <那个时间戳> --resume` 续
   跑同一个序列——`--resume` 会认出已经存在的 clip 视频直接跳过，只会跑真正
   缺的那几条。2026-08-22 靠这一套，断线那条 clip 零重复渲染，前面两条完好
   的 clip 也没受影响。

## 渲染

跟 A100 时代的 `h3_runner.py` 直接调用不同，现在走
`h3_sequence_runner.py --runner h3_accel_shim.py`，后者是给整条三段序列自动
开 Sage 加速的 wrapper，`h3_runner.py` / `h3_sequence_runner.py` 本身不动：

```bash
python h3_sequence_runner.py run \
  --sequence <sequence.json> \
  --runner h3_accel_shim.py \
  --output-root <dish>/run --run-id <label>
```

`sequence.json` 里 `server` 字段填 `http://127.0.0.1:8189`（走隧道），
其余生产参数（`r2v`、`1088x1920` 裁 `1080x1920`、`8 steps`、Turbo）跟
`GPU_CARD_REFERENCE.md` 里"每张卡都一样"的那节完全一致，这里不重复。

**一次跑多道菜，命令之间必须用 `&&`，不能用裸的 `;` 或 `{ }` 代码块顺序排。**
`docs/history/H100_BATCH_SILENT_FAILURE_2026-08-21.md` 记录过反面案例：一个
不带短路的代码块最后一条是 `echo`，前面随便死几个都照样报
`exit code 0`、"ALL DONE"，五道菜里实际只跑成一道。2026-08-22 用 `&&` 链起来
之后，隧道断线那次立刻在失败的那一步停住、reported `exit code 1`，而不是
带着假成功继续滚下去——这是唯一一次网络中断没有变成静默数据丢失的原因。

## 用完记得

停机（Stop 不是 Destroy）能保留这 89G 的盘——63GB 模型 + 编译好的
SageAttention 都在，下次开机跳过装机那一步，直接省 20 分钟以上。
