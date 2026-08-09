#!/usr/bin/env python3
"""
MiniMax H3 SSH cluster runner.

Local orchestrator for dispatching multiple MiniMax H3 jobs to several SSH
servers. It assumes each server can run ComfyUI locally and that `h3_runner.py`
is available or can be uploaded into the remote ComfyUI directory.

This script intentionally avoids storing passwords. Use SSH keys, ssh-agent,
or your normal interactive SSH credential flow.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import dataclasses
import datetime as dt
import ast
import json
import os
import re
import shlex
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - exercised only on machines without PyYAML
    yaml = None


DEFAULT_CONDA_SH = "/home/node/anaconda3/etc/profile.d/conda.sh"
DEFAULT_CONDA_ENV = "comfy_h3_torch29_cu126"
DEFAULT_COMFY_DIR = "/root/ComfyUI"
DEFAULT_REMOTE_JOB_ROOT = "cluster_jobs"
DEFAULT_LOCAL_OUTPUT_ROOT = "cluster_outputs"
DEFAULT_PYTHON = "python"
DEFAULT_MODE = "r2v"
DEFAULT_WIDTH = 1344
DEFAULT_HEIGHT = 768
DEFAULT_DURATION = 15.0
DEFAULT_STEPS = 4
DEFAULT_POLL = 10.0
DEFAULT_TIMEOUT = 21600.0
REQUIRED_MODEL_FILES = (
    "models/diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors",
    "models/diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors",
    "models/text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors",
    "models/vae/minimax_h3_video_vae_fp16.safetensors",
    "models/vae/minimax_h3_audio_vae_fp32.safetensors",
    "models/loras/minimax_h3_turbo_v4_step600_ema.safetensors",
    "custom_nodes/ComfyUI-MiniMax-H3-Turbo/__init__.py",
)


class ClusterError(RuntimeError):
    pass


def now_id() -> str:
    return dt.datetime.now().strftime("%Y%m%d_%H%M%S")


def slug(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9._-]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "item"


def q(value: str | os.PathLike[str]) -> str:
    return shlex.quote(str(value))


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ClusterError(f"YAML file not found: {path}")
    text = path.read_text(encoding="utf-8")
    data = yaml.safe_load(text) if yaml is not None else simple_yaml_load(text)
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ClusterError(f"Expected a YAML mapping in {path}")
    return data


def simple_yaml_load(text: str) -> Any:
    """Small YAML subset parser for this repo's config files.

    It supports nested mappings/lists, scalar values, inline lists/dicts, and
    block strings. PyYAML is still preferred when installed.
    """

    raw_lines = text.splitlines()
    lines: list[tuple[int, str, int]] = []
    for line_no, raw in enumerate(raw_lines, start=1):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        lines.append((indent, raw[indent:].rstrip(), line_no))

    def strip_comment(value: str) -> str:
        quote: str | None = None
        for index, ch in enumerate(value):
            if ch in {"'", '"'}:
                quote = None if quote == ch else ch if quote is None else quote
            elif ch == "#" and quote is None and (index == 0 or value[index - 1].isspace()):
                return value[:index].rstrip()
        return value.strip()

    def parse_scalar(value: str) -> Any:
        value = strip_comment(value)
        if value == "":
            return ""
        lowered = value.lower()
        if lowered in {"true", "false"}:
            return lowered == "true"
        if lowered in {"null", "none", "~"}:
            return None
        if (value.startswith("'") and value.endswith("'")) or (
            value.startswith('"') and value.endswith('"')
        ):
            return ast.literal_eval(value)
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            if not inner:
                return []
            return [parse_scalar(part.strip()) for part in inner.split(",")]
        if value.startswith("{") and value.endswith("}"):
            inner = value[1:-1].strip()
            if not inner:
                return {}
            result: dict[str, Any] = {}
            for part in inner.split(","):
                key, sep, raw = part.partition(":")
                if not sep:
                    raise ClusterError(f"Invalid inline mapping value: {value}")
                result[str(parse_scalar(key.strip()))] = parse_scalar(raw.strip())
            return result
        try:
            if re.fullmatch(r"[-+]?\d+", value):
                return int(value)
            if re.fullmatch(r"[-+]?(\d+\.\d*|\d*\.\d+)", value):
                return float(value)
        except ValueError:
            pass
        return value

    def collect_block_string(index: int, parent_indent: int, folded: bool) -> tuple[str, int]:
        collected: list[str] = []
        base_indent: int | None = None
        while index < len(lines):
            indent, content, _line_no = lines[index]
            if indent <= parent_indent:
                break
            if base_indent is None:
                base_indent = indent
            cut = min(indent, base_indent)
            collected.append(" " * (indent - cut) + content)
            index += 1
        if folded:
            return " ".join(part.strip() for part in collected), index
        return "\n".join(collected), index

    def split_key_value(content: str, line_no: int) -> tuple[str, str]:
        if ":" not in content:
            raise ClusterError(f"Invalid YAML line {line_no}: {content}")
        key, value = content.split(":", 1)
        key = key.strip()
        if not key:
            raise ClusterError(f"Invalid empty key on YAML line {line_no}")
        return key, value.strip()

    def parse_block(index: int, indent: int) -> tuple[Any, int]:
        if index >= len(lines):
            return {}, index
        next_indent, content, _line_no = lines[index]
        if next_indent < indent:
            return {}, index
        if content.startswith("- "):
            return parse_list(index, next_indent)
        return parse_map(index, next_indent)

    def parse_map(index: int, indent: int) -> tuple[dict[str, Any], int]:
        result: dict[str, Any] = {}
        while index < len(lines):
            line_indent, content, line_no = lines[index]
            if line_indent < indent:
                break
            if line_indent > indent:
                raise ClusterError(f"Unexpected indentation on YAML line {line_no}")
            if content.startswith("- "):
                break
            key, value = split_key_value(content, line_no)
            index += 1
            if value in {"|", ">"}:
                result[key], index = collect_block_string(index, line_indent, value == ">")
            elif value == "":
                result[key], index = parse_block(index, line_indent + 2)
            else:
                result[key] = parse_scalar(value)
        return result, index

    def parse_list(index: int, indent: int) -> tuple[list[Any], int]:
        result: list[Any] = []
        while index < len(lines):
            line_indent, content, line_no = lines[index]
            if line_indent < indent:
                break
            if line_indent > indent:
                raise ClusterError(f"Unexpected indentation on YAML line {line_no}")
            if not content.startswith("- "):
                break
            item_content = content[2:].strip()
            index += 1
            if item_content == "":
                item, index = parse_block(index, line_indent + 2)
                result.append(item)
            elif ":" in item_content and not item_content.startswith(("'", '"')):
                key, value = split_key_value(item_content, line_no)
                item: dict[str, Any] = {}
                if value in {"|", ">"}:
                    item[key], index = collect_block_string(index, line_indent, value == ">")
                elif value == "":
                    item[key], index = parse_block(index, line_indent + 2)
                else:
                    item[key] = parse_scalar(value)
                if index < len(lines) and lines[index][0] > line_indent:
                    more, index = parse_map(index, line_indent + 2)
                    item.update(more)
                result.append(item)
            else:
                result.append(parse_scalar(item_content))
                if index < len(lines) and lines[index][0] > line_indent:
                    raise ClusterError(f"Unexpected nested block after scalar on YAML line {line_no}")
        return result, index

    parsed, next_index = parse_block(0, 0)
    if next_index != len(lines):
        _, _, line_no = lines[next_index]
        raise ClusterError(f"Could not parse YAML near line {line_no}")
    return parsed


def deepish_merge(base: dict[str, Any], item: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in item.items():
        if (
            isinstance(value, dict)
            and isinstance(merged.get(key), dict)
            and key not in {"workers"}
        ):
            merged[key] = deepish_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def as_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


def rel_path(path_value: str, base_dir: Path) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    return (base_dir / path).resolve()


@dataclasses.dataclass(frozen=True)
class Worker:
    name: str
    server_name: str
    host: str
    user: str
    ssh_port: int
    gpu: int | None
    comfy_port: int
    comfy_dir: str
    conda_sh: str
    conda_env: str
    python: str
    lowvram: bool
    auto_start: bool
    upload_runner: bool
    remote_job_root: str
    ssh_extra_args: tuple[str, ...] = ()

    @property
    def ssh_target(self) -> str:
        return f"{self.user}@{self.host}" if self.user else self.host

    @property
    def server_url(self) -> str:
        return f"http://127.0.0.1:{self.comfy_port}"

    @property
    def label(self) -> str:
        return f"{self.server_name}/{self.name}"


@dataclasses.dataclass(frozen=True)
class Job:
    job_id: str
    mode: str
    prompt: str
    prompt_source: str
    ref_images: tuple[Path, ...]
    first_frame: Path | None
    last_frame: Path | None
    width: int
    height: int
    duration: float
    steps: int
    seed: int | None
    turbo: bool
    turbo_low_vram: bool
    turbo_strength: float
    turbo_lora: str | None
    ref_image_size: str
    poll: float
    timeout: float
    prefix: str
    enabled: bool
    raw: dict[str, Any]


@dataclasses.dataclass
class JobResult:
    job_id: str
    worker: str
    status: str
    local_dir: str
    local_video: str | None = None
    remote_video: str | None = None
    seconds: float | None = None
    error: str | None = None


def parse_servers(path: Path) -> list[Worker]:
    data = load_yaml(path)
    defaults = data.get("defaults") or {}
    servers = data.get("servers") or []
    if not isinstance(servers, list):
        raise ClusterError("servers.yaml must contain a list under `servers`")

    workers: list[Worker] = []
    for raw_server in servers:
        if not isinstance(raw_server, dict):
            raise ClusterError("Each server entry must be a mapping")
        server = deepish_merge(defaults, raw_server)
        server_name = str(server.get("name") or server.get("host") or "server")
        host = str(server.get("host") or "")
        if not host:
            raise ClusterError(f"Server {server_name} is missing `host`")
        user = str(server.get("user") or "root")
        ssh_port = int(server.get("ssh_port") or server.get("port") or 22)
        comfy_dir = str(server.get("comfy_dir") or DEFAULT_COMFY_DIR)
        conda_sh = str(server.get("conda_sh") or DEFAULT_CONDA_SH)
        conda_env = str(server.get("conda_env") or DEFAULT_CONDA_ENV)
        python = str(server.get("python") or DEFAULT_PYTHON)
        lowvram = as_bool(server.get("lowvram"), True)
        auto_start = as_bool(server.get("auto_start"), True)
        upload_runner = as_bool(server.get("upload_runner"), True)
        remote_job_root = str(server.get("remote_job_root") or DEFAULT_REMOTE_JOB_ROOT)
        ssh_extra_args = tuple(str(x) for x in server.get("ssh_extra_args") or [])

        raw_workers = server.get("workers")
        if raw_workers is None:
            raw_workers = [
                {
                    "name": "gpu0",
                    "gpu": server.get("gpu", 0),
                    "comfy_port": server.get("comfy_port", 8189),
                }
            ]
        if not isinstance(raw_workers, list):
            raise ClusterError(f"Server {server_name} has invalid `workers`")

        for index, raw_worker in enumerate(raw_workers):
            if not isinstance(raw_worker, dict):
                raise ClusterError(f"Worker #{index} on {server_name} is invalid")
            worker = deepish_merge(server, raw_worker)
            worker_name = str(worker.get("name") or f"gpu{index}")
            gpu_value = worker.get("gpu", index)
            gpu = None if gpu_value is None else int(gpu_value)
            comfy_port = int(worker.get("comfy_port") or worker.get("port") or 8189)
            workers.append(
                Worker(
                    name=worker_name,
                    server_name=server_name,
                    host=host,
                    user=user,
                    ssh_port=ssh_port,
                    gpu=gpu,
                    comfy_port=comfy_port,
                    comfy_dir=comfy_dir,
                    conda_sh=conda_sh,
                    conda_env=conda_env,
                    python=python,
                    lowvram=as_bool(worker.get("lowvram"), lowvram),
                    auto_start=as_bool(worker.get("auto_start"), auto_start),
                    upload_runner=as_bool(worker.get("upload_runner"), upload_runner),
                    remote_job_root=str(worker.get("remote_job_root") or remote_job_root),
                    ssh_extra_args=ssh_extra_args,
                )
            )
    if not workers:
        raise ClusterError("No workers found in servers config")
    return workers


def read_prompt(job: dict[str, Any], base_dir: Path) -> tuple[str, str]:
    if "prompt" in job and str(job["prompt"]).strip():
        return str(job["prompt"]).strip(), "inline"
    prompt_file = job.get("prompt_file")
    if prompt_file:
        path = rel_path(str(prompt_file), base_dir)
        if not path.exists():
            raise ClusterError(f"Prompt file not found: {path}")
        return path.read_text(encoding="utf-8").strip(), str(path)
    raise ClusterError(f"Job {job.get('id') or job.get('name')} needs prompt or prompt_file")


def parse_jobs(path: Path) -> tuple[str, list[Job]]:
    data = load_yaml(path)
    base_dir = path.parent.resolve()
    batch_id = slug(str(data.get("batch_id") or data.get("name") or path.stem))
    defaults = data.get("defaults") or {}
    raw_jobs = data.get("jobs") or []
    if not isinstance(raw_jobs, list):
        raise ClusterError("jobs.yaml must contain a list under `jobs`")

    jobs: list[Job] = []
    for index, raw_job in enumerate(raw_jobs):
        if not isinstance(raw_job, dict):
            raise ClusterError(f"Job #{index} must be a mapping")
        item = deepish_merge(defaults, raw_job)
        job_id = slug(str(item.get("id") or item.get("name") or f"job-{index + 1}"))
        prompt, prompt_source = read_prompt(item, base_dir)
        mode = str(item.get("mode") or DEFAULT_MODE)
        if mode not in {"t2v", "i2v", "flf2v", "r2v"}:
            raise ClusterError(f"Job {job_id} has unsupported mode: {mode}")

        ref_images = tuple(
            rel_path(str(p), base_dir) for p in (item.get("ref_images") or [])
        )
        first_frame = (
            rel_path(str(item["first_frame"]), base_dir)
            if item.get("first_frame")
            else None
        )
        last_frame = (
            rel_path(str(item["last_frame"]), base_dir)
            if item.get("last_frame")
            else None
        )
        prefix = str(item.get("prefix") or f"cluster/{batch_id}/{job_id}")
        jobs.append(
            Job(
                job_id=job_id,
                mode=mode,
                prompt=prompt,
                prompt_source=prompt_source,
                ref_images=ref_images,
                first_frame=first_frame,
                last_frame=last_frame,
                width=int(item.get("width") or DEFAULT_WIDTH),
                height=int(item.get("height") or DEFAULT_HEIGHT),
                duration=float(item.get("duration") or DEFAULT_DURATION),
                steps=int(item.get("steps") or DEFAULT_STEPS),
                seed=int(item["seed"]) if item.get("seed") is not None else None,
                turbo=as_bool(item.get("turbo"), True),
                turbo_low_vram=as_bool(item.get("turbo_low_vram"), False),
                turbo_strength=float(item.get("turbo_strength") or 1.0),
                turbo_lora=(
                    str(item["turbo_lora"]) if item.get("turbo_lora") else None
                ),
                ref_image_size=str(item.get("ref_image_size") or "match"),
                poll=float(item.get("poll") or DEFAULT_POLL),
                timeout=float(item.get("timeout") or DEFAULT_TIMEOUT),
                prefix=prefix,
                enabled=as_bool(item.get("enabled"), True),
                raw=item,
            )
        )
    if not jobs:
        raise ClusterError("No jobs found in jobs config")
    return batch_id, jobs


def validate_assets(jobs: list[Job], strict_assets: bool = False) -> list[str]:
    warnings: list[str] = []
    for job in jobs:
        paths = list(job.ref_images)
        if job.first_frame:
            paths.append(job.first_frame)
        if job.last_frame:
            paths.append(job.last_frame)
        for path in paths:
            if not path.exists():
                msg = f"Job {job.job_id}: missing asset {path}"
                if strict_assets:
                    raise ClusterError(msg)
                warnings.append(msg)

        if job.mode == "r2v" and not job.ref_images:
            raise ClusterError(f"Job {job.job_id}: r2v requires ref_images")
        if job.mode == "i2v" and not job.first_frame:
            raise ClusterError(f"Job {job.job_id}: i2v requires first_frame")
        if job.mode == "flf2v" and (not job.first_frame or not job.last_frame):
            raise ClusterError(f"Job {job.job_id}: flf2v requires first_frame and last_frame")
        if job.mode == "r2v" and len(job.ref_images) > 9:
            raise ClusterError(f"Job {job.job_id}: MiniMax H3 supports up to 9 ref_images")
        if job.width % 32 != 0 or job.height % 32 != 0:
            raise ClusterError(f"Job {job.job_id}: width/height must be multiples of 32")
    return warnings


def ssh_args(worker: Worker) -> list[str]:
    args = ["ssh", "-p", str(worker.ssh_port), *worker.ssh_extra_args, worker.ssh_target]
    return args


def scp_args(worker: Worker) -> list[str]:
    return ["scp", "-P", str(worker.ssh_port), *worker.ssh_extra_args]


def run_command(
    args: list[str],
    *,
    input_text: str | None = None,
    timeout: float | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        input=input_text,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
        check=False,
    )


def remote_bash(worker: Worker, script: str, timeout: float | None = None) -> str:
    cmd = [*ssh_args(worker), "bash", "-s"]
    proc = run_command(cmd, input_text=script, timeout=timeout)
    if proc.returncode != 0:
        raise ClusterError(proc.stdout.strip() or f"remote command failed: {cmd}")
    return proc.stdout


def scp_to(worker: Worker, local: Path, remote: str) -> None:
    cmd = [*scp_args(worker), str(local), f"{worker.ssh_target}:{remote}"]
    proc = run_command(cmd)
    if proc.returncode != 0:
        raise ClusterError(proc.stdout.strip() or f"scp failed: {' '.join(cmd)}")


def scp_from(worker: Worker, remote: str, local: Path) -> None:
    local.parent.mkdir(parents=True, exist_ok=True)
    cmd = [*scp_args(worker), f"{worker.ssh_target}:{remote}", str(local)]
    proc = run_command(cmd)
    if proc.returncode != 0:
        raise ClusterError(proc.stdout.strip() or f"scp failed: {' '.join(cmd)}")


def remote_job_dir(worker: Worker, batch_id: str, run_id: str, job_id: str) -> str:
    return (
        f"{worker.comfy_dir.rstrip('/')}/"
        f"{worker.remote_job_root.strip('/')}/"
        f"{slug(batch_id)}/{slug(run_id)}/{slug(job_id)}-{slug(worker.name)}"
    )


def activate_lines(worker: Worker) -> str:
    return f"""
if [ -f {q(worker.conda_sh)} ]; then
  source {q(worker.conda_sh)}
fi
if [ -n {q(worker.conda_env)} ]; then
  conda activate {q(worker.conda_env)}
fi
"""


def ensure_comfy_running(worker: Worker, dry_run: bool = False) -> None:
    script = f"""
set -euo pipefail
URL={q(worker.server_url + "/system_stats")}
if curl -fsS "$URL" >/dev/null 2>&1; then
  echo "ComfyUI already running at {worker.server_url}"
  exit 0
fi
if [ {q("1" if worker.auto_start else "0")} != "1" ]; then
  echo "ComfyUI is not running and auto_start=false"
  exit 3
fi
{activate_lines(worker)}
cd {q(worker.comfy_dir)}
LOG={q(f"comfyui_cluster_{worker.name}.log")}
PID={q(f"comfyui_cluster_{worker.name}.pid")}
LOWVRAM=""
if [ {q("1" if worker.lowvram else "0")} = "1" ]; then
  LOWVRAM="--lowvram"
fi
echo "Starting ComfyUI at {worker.server_url}"
CUDA_PREFIX=""
if [ {q("" if worker.gpu is None else str(worker.gpu))} != "" ]; then
  CUDA_PREFIX="CUDA_VISIBLE_DEVICES={'' if worker.gpu is None else worker.gpu}"
fi
if [ -n "$CUDA_PREFIX" ]; then
  CUDA_VISIBLE_DEVICES={"" if worker.gpu is None else worker.gpu} nohup {q(worker.python)} main.py --listen 127.0.0.1 --port {worker.comfy_port} $LOWVRAM > "$LOG" 2>&1 &
else
  nohup {q(worker.python)} main.py --listen 127.0.0.1 --port {worker.comfy_port} $LOWVRAM > "$LOG" 2>&1 &
fi
echo $! > "$PID"
for _ in $(seq 1 90); do
  if curl -fsS "$URL" >/dev/null 2>&1; then
    echo "ComfyUI ready at {worker.server_url}"
    exit 0
  fi
  sleep 2
done
tail -n 120 "$LOG" >&2 || true
exit 4
"""
    if dry_run:
        print(f"[dry-run] would ensure ComfyUI on {worker.label} {worker.server_url}")
        return
    remote_bash(worker, script, timeout=240)


def build_check_script(worker: Worker) -> str:
    model_checks = "\n".join(
        f"check_file {q(worker.comfy_dir.rstrip('/') + '/' + path)}"
        for path in REQUIRED_MODEL_FILES
    )
    return f"""
set +e
echo "## worker={worker.label}"
echo "## ssh_target={worker.ssh_target}:{worker.ssh_port}"
echo "## comfy_url={worker.server_url}"

check_file() {{
  if [ -f "$1" ]; then
    SIZE="$(du -h "$1" 2>/dev/null | awk '{{print $1}}')"
    echo "OK file $1 $SIZE"
  else
    echo "MISSING file $1"
  fi
}}

check_dir() {{
  if [ -d "$1" ]; then
    echo "OK dir $1"
  else
    echo "MISSING dir $1"
  fi
}}

echo "== system =="
hostname 2>/dev/null || true
date 2>/dev/null || true
uname -a 2>/dev/null || true
df -h / {q(worker.comfy_dir)} 2>/dev/null || df -h / 2>/dev/null || true

echo "== gpu =="
if command -v nvidia-smi >/dev/null 2>&1; then
  nvidia-smi --query-gpu=index,name,memory.total,memory.used,driver_version --format=csv,noheader,nounits 2>/dev/null || nvidia-smi
else
  echo "MISSING command nvidia-smi"
fi

echo "== conda =="
if [ -f {q(worker.conda_sh)} ]; then
  echo "OK conda_sh {worker.conda_sh}"
  source {q(worker.conda_sh)}
else
  echo "MISSING conda_sh {worker.conda_sh}"
fi
if command -v conda >/dev/null 2>&1; then
  conda env list 2>/dev/null | sed -n '1,40p'
  if conda env list 2>/dev/null | awk '{{print $1}}' | grep -qx {q(worker.conda_env)}; then
    echo "OK conda_env {worker.conda_env}"
  else
    echo "MISSING conda_env {worker.conda_env}"
  fi
else
  echo "MISSING command conda"
fi

echo "== python/torch =="
if command -v conda >/dev/null 2>&1; then
  conda activate {q(worker.conda_env)} >/dev/null 2>&1
fi
{q(worker.python)} - <<'PY' 2>&1
import sys
print("python:", sys.version.replace("\\n", " "))
try:
    import torch
    print("torch:", torch.__version__)
    print("torch_cuda:", torch.version.cuda)
    print("cuda_available:", torch.cuda.is_available())
    if torch.cuda.is_available():
        print("gpu_name:", torch.cuda.get_device_name(0))
        props = torch.cuda.get_device_properties(0)
        print("vram_gb:", round(props.total_memory / 1024**3, 2))
except Exception as exc:
    print("torch_check_error:", repr(exc))
PY

echo "== comfyui files =="
check_dir {q(worker.comfy_dir)}
check_file {q(worker.comfy_dir.rstrip('/') + '/main.py')}
check_file {q(worker.comfy_dir.rstrip('/') + '/h3_runner.py')}
{model_checks}

echo "== comfyui api =="
if curl -fsS {q(worker.server_url + "/system_stats")} >/tmp/cluster_comfy_stats.json 2>/dev/null; then
  echo "OK comfy_running {worker.server_url}"
  head -c 1000 /tmp/cluster_comfy_stats.json
  echo
  {q(worker.python)} - <<'PY' 2>&1
import json, urllib.request
url = {worker.server_url!r} + "/object_info"
nodes = ["MiniMaxH3TurboLoRA", "MiniMaxH3TurboSampler", "MiniMaxH3ImageToVideo", "MiniMaxH3ReferenceToVideo"]
try:
    obj = json.load(urllib.request.urlopen(url, timeout=30))
    for node in nodes:
        print(("OK node " if node in obj else "MISSING node ") + node)
except Exception as exc:
    print("object_info_error:", repr(exc))
PY
else
  echo "NOT_RUNNING comfy {worker.server_url}"
fi
"""


def upload_runner_if_needed(worker: Worker, dry_run: bool = False) -> None:
    if not worker.upload_runner:
        return
    local_runner = Path(__file__).with_name("h3_runner.py")
    if not local_runner.exists():
        raise ClusterError(f"Missing local h3_runner.py: {local_runner}")
    remote_runner = f"{worker.comfy_dir.rstrip('/')}/h3_runner.py"
    if dry_run:
        print(f"[dry-run] would upload {local_runner} -> {worker.label}:{remote_runner}")
        return
    remote_bash(worker, f"mkdir -p {q(worker.comfy_dir)}")
    scp_to(worker, local_runner, remote_runner)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def build_remote_run_script(
    worker: Worker,
    job: Job,
    remote_dir: str,
    remote_prompt: str,
    remote_refs: list[str],
    remote_first: str | None,
    remote_last: str | None,
) -> str:
    lines: list[str] = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        activate_lines(worker),
        f"cd {q(worker.comfy_dir)}",
        f"REMOTE_DIR={q(remote_dir)}",
        f"RUNNER_LOG={q(remote_dir + '/runner.log')}",
        "mkdir -p \"$REMOTE_DIR\"",
        "CMD=(",
        f"  {q(worker.python)} h3_runner.py {q(job.mode)}",
        f"  --server {q(worker.server_url)}",
        f"  --prompt \"$(< {q(remote_prompt)})\"",
        f"  --width {job.width}",
        f"  --height {job.height}",
        f"  --duration {job.duration}",
        f"  --steps {job.steps}",
        f"  --prefix {q(job.prefix)}",
        f"  --output-dir {q(remote_dir + '/outputs')}",
        f"  --poll {job.poll}",
        f"  --timeout {job.timeout}",
        "  --overwrite-upload",
    ]
    if job.seed is not None:
        lines.append(f"  --seed {job.seed}")
    if job.turbo:
        lines.append("  --turbo")
    if job.turbo_low_vram:
        lines.append("  --turbo-low-vram")
    if job.turbo_strength != 1.0:
        lines.append(f"  --turbo-strength {job.turbo_strength}")
    if job.turbo_lora:
        lines.append(f"  --turbo-lora {q(job.turbo_lora)}")
    if job.ref_image_size != "match":
        lines.append(f"  --ref-image-size {q(job.ref_image_size)}")
    if remote_first:
        lines.append(f"  --first-frame {q(remote_first)}")
    if remote_last:
        lines.append(f"  --last-frame {q(remote_last)}")
    for image in remote_refs:
        lines.append(f"  --ref-image {q(image)}")
    lines.extend(
        [
            ")",
            "echo \"[cluster] starting job\"",
            "printf '[cluster] command:'",
            "printf ' %q' \"${CMD[@]}\"",
            "printf '\\n'",
            "set +e",
            "/usr/bin/time -p \"${CMD[@]}\" > \"$RUNNER_LOG\" 2>&1",
            "STATUS=$?",
            "set -e",
            "cat \"$RUNNER_LOG\"",
            "exit \"$STATUS\"",
        ]
    )
    return "\n".join(lines) + "\n"


def local_job_dir(output_root: Path, batch_id: str, run_id: str, job_id: str) -> Path:
    return output_root / slug(batch_id) / slug(run_id) / slug(job_id)


def snapshot_job(local_dir: Path, worker: Worker, job: Job) -> None:
    data = {
        "job_id": job.job_id,
        "worker": worker.label,
        "mode": job.mode,
        "width": job.width,
        "height": job.height,
        "duration": job.duration,
        "steps": job.steps,
        "seed": job.seed,
        "turbo": job.turbo,
        "turbo_low_vram": job.turbo_low_vram,
        "prefix": job.prefix,
        "prompt_source": job.prompt_source,
        "ref_images": [str(p) for p in job.ref_images],
        "first_frame": str(job.first_frame) if job.first_frame else None,
        "last_frame": str(job.last_frame) if job.last_frame else None,
    }
    write_text(local_dir / "job.json", json.dumps(data, ensure_ascii=False, indent=2))
    write_text(local_dir / "prompt.txt", job.prompt)


def upload_job_assets(
    worker: Worker,
    job: Job,
    local_dir: Path,
    remote_dir: str,
    dry_run: bool = False,
) -> tuple[str, list[str], str | None, str | None]:
    remote_inputs = f"{remote_dir}/inputs"
    prompt_local = local_dir / "prompt.txt"
    prompt_remote = f"{remote_dir}/prompt.txt"
    planned_refs = [
        f"{remote_inputs}/ref_{index:02d}_{slug(path.stem)}{path.suffix}"
        for index, path in enumerate(job.ref_images, start=1)
    ]
    planned_first = (
        f"{remote_inputs}/first_{slug(job.first_frame.stem)}{job.first_frame.suffix}"
        if job.first_frame
        else None
    )
    planned_last = (
        f"{remote_inputs}/last_{slug(job.last_frame.stem)}{job.last_frame.suffix}"
        if job.last_frame
        else None
    )
    if dry_run:
        print(f"[dry-run] would create remote dir {worker.label}:{remote_dir}")
        print(f"[dry-run] would upload prompt -> {prompt_remote}")
        for path, remote_path in zip(job.ref_images, planned_refs):
            print(f"[dry-run] would upload ref image {path} -> {remote_path}")
        if job.first_frame:
            print(f"[dry-run] would upload first frame {job.first_frame} -> {planned_first}")
        if job.last_frame:
            print(f"[dry-run] would upload last frame {job.last_frame} -> {planned_last}")
        return prompt_remote, planned_refs, planned_first, planned_last

    remote_bash(worker, f"mkdir -p {q(remote_inputs)} {q(remote_dir + '/outputs')}")
    scp_to(worker, prompt_local, prompt_remote)

    remote_refs: list[str] = []
    for path, remote_path in zip(job.ref_images, planned_refs):
        scp_to(worker, path, remote_path)
        remote_refs.append(remote_path)

    remote_first = planned_first
    if job.first_frame:
        scp_to(worker, job.first_frame, remote_first)

    remote_last = planned_last
    if job.last_frame:
        scp_to(worker, job.last_frame, remote_last)

    return prompt_remote, remote_refs, remote_first, remote_last


def parse_downloaded_path(output: str) -> str | None:
    matches = re.findall(r"Downloaded:\s*(.+)", output)
    if not matches:
        return None
    return matches[-1].strip()


def run_one_job(
    worker: Worker,
    job: Job,
    *,
    batch_id: str,
    run_id: str,
    output_root: Path,
    dry_run: bool = False,
) -> JobResult:
    started = time.time()
    local_dir = local_job_dir(output_root, batch_id, run_id, job.job_id)
    snapshot_job(local_dir, worker, job)
    remote_dir = remote_job_dir(worker, batch_id, run_id, job.job_id)

    try:
        upload_runner_if_needed(worker, dry_run=dry_run)
        ensure_comfy_running(worker, dry_run=dry_run)
        remote_prompt, remote_refs, remote_first, remote_last = upload_job_assets(
            worker, job, local_dir, remote_dir, dry_run=dry_run
        )
        remote_script = build_remote_run_script(
            worker,
            job,
            remote_dir,
            remote_prompt,
            remote_refs,
            remote_first,
            remote_last,
        )
        script_local = local_dir / "run_remote.sh"
        write_text(script_local, remote_script)
        script_remote = f"{remote_dir}/run_remote.sh"

        if dry_run:
            print(
                f"[dry-run] would run job {job.job_id} on {worker.label}; "
                f"remote script {script_remote}"
            )
            return JobResult(
                job_id=job.job_id,
                worker=worker.label,
                status="dry-run",
                local_dir=str(local_dir),
                seconds=round(time.time() - started, 2),
            )

        scp_to(worker, script_local, script_remote)
        output = remote_bash(
            worker,
            f"bash {q(script_remote)}",
            timeout=job.timeout + 600,
        )
        write_text(local_dir / "ssh-output.log", output)
        try:
            scp_from(worker, f"{remote_dir}/runner.log", local_dir / "runner.log")
        except ClusterError:
            pass

        remote_video = parse_downloaded_path(output)
        local_video = None
        if remote_video:
            target = local_dir / Path(remote_video).name
            scp_from(worker, remote_video, target)
            local_video = str(target.resolve())

        return JobResult(
            job_id=job.job_id,
            worker=worker.label,
            status="success",
            local_dir=str(local_dir.resolve()),
            local_video=local_video,
            remote_video=remote_video,
            seconds=round(time.time() - started, 2),
        )
    except Exception as exc:  # noqa: BLE001 - convert to job result
        return JobResult(
            job_id=job.job_id,
            worker=worker.label,
            status="failed",
            local_dir=str(local_dir.resolve()),
            seconds=round(time.time() - started, 2),
            error=str(exc),
        )


def state_path(output_root: Path, batch_id: str, run_id: str) -> Path:
    return output_root / slug(batch_id) / slug(run_id) / "state.json"


def write_state(path: Path, results: list[JobResult]) -> None:
    data = {
        "updated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "results": [dataclasses.asdict(result) for result in results],
    }
    write_text(path, json.dumps(data, ensure_ascii=False, indent=2))


def load_state(path: Path) -> list[JobResult]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return [JobResult(**item) for item in data.get("results", [])]


def command_validate(args: argparse.Namespace) -> int:
    workers = parse_servers(Path(args.servers))
    batch_id, jobs = parse_jobs(Path(args.jobs))
    warnings = validate_assets(jobs, strict_assets=args.strict_assets)
    enabled = [job for job in jobs if job.enabled]
    print(f"Batch: {batch_id}")
    print(f"Workers: {len(workers)}")
    for worker in workers:
        gpu = "none" if worker.gpu is None else worker.gpu
        print(f"  - {worker.label}: {worker.ssh_target}:{worker.ssh_port}, gpu={gpu}, port={worker.comfy_port}")
    print(f"Jobs: {len(jobs)} total, {len(enabled)} enabled")
    for warning in warnings:
        print(f"WARNING: {warning}")
    print("Validation OK")
    return 0


def command_plan(args: argparse.Namespace) -> int:
    workers = parse_servers(Path(args.servers))
    batch_id, jobs = parse_jobs(Path(args.jobs))
    validate_assets(jobs, strict_assets=False)
    enabled_jobs = [job for job in jobs if job.enabled]
    if args.limit:
        enabled_jobs = enabled_jobs[: args.limit]
    print(f"Batch: {batch_id}")
    for index, job in enumerate(enabled_jobs):
        worker = workers[index % len(workers)]
        print(
            f"{job.job_id} -> {worker.label} "
            f"({job.mode}, {job.width}x{job.height}, {job.duration}s, "
            f"steps={job.steps}, turbo={job.turbo})"
        )
    return 0


def check_one_worker(worker: Worker, args: argparse.Namespace) -> tuple[Worker, str, str | None]:
    try:
        if args.upload_runner:
            upload_runner_if_needed(worker, dry_run=False)
        if args.start_comfy:
            ensure_comfy_running(worker, dry_run=False)
        output = remote_bash(worker, build_check_script(worker), timeout=args.timeout)
        return worker, output, None
    except Exception as exc:  # noqa: BLE001 - surface as per-worker check result
        return worker, "", str(exc)


def command_check(args: argparse.Namespace) -> int:
    workers = parse_servers(Path(args.servers))
    if args.limit:
        workers = workers[: args.limit]
    max_parallel = min(len(workers), int(args.max_parallel or len(workers)))
    print(
        f"Checking workers={len(workers)} parallel={max_parallel} "
        f"start_comfy={args.start_comfy} upload_runner={args.upload_runner}"
    )
    failures = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_parallel) as pool:
        futures = [pool.submit(check_one_worker, worker, args) for worker in workers]
        for future in concurrent.futures.as_completed(futures):
            worker, output, error_text = future.result()
            print("=" * 80)
            print(f"CHECK {worker.label}")
            print("=" * 80)
            if output:
                print(output.rstrip())
            if error_text:
                failures += 1
                print(f"ERROR {worker.label}: {error_text}")
    if failures:
        print(f"Check completed with {failures} failed worker(s).")
        return 1
    print("Check completed.")
    return 0


def command_run(args: argparse.Namespace) -> int:
    workers = parse_servers(Path(args.servers))
    batch_id, jobs = parse_jobs(Path(args.jobs))
    warnings = validate_assets(jobs, strict_assets=args.strict_assets)
    for warning in warnings:
        print(f"WARNING: {warning}")

    output_root = Path(args.output_root).resolve()
    run_id = slug(args.run_id or now_id())
    state_file = state_path(output_root, batch_id, run_id)
    old_results = load_state(state_file)
    old_success = {result.job_id for result in old_results if result.status == "success"}

    pending = [job for job in jobs if job.enabled]
    if not args.rerun:
        pending = [job for job in pending if job.job_id not in old_success]
    if args.limit:
        pending = pending[: args.limit]

    if not pending:
        print("No pending jobs.")
        return 0

    max_parallel = min(len(workers), int(args.max_parallel or len(workers)))
    print(
        f"Running batch={batch_id} run_id={run_id} "
        f"jobs={len(pending)} workers={len(workers)} parallel={max_parallel}"
    )
    if args.dry_run:
        print("Dry run: no SSH/SCP commands will execute.")

    results: list[JobResult] = list(old_results)
    result_by_job = {result.job_id: result for result in results}

    job_iter = iter(pending)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_parallel) as pool:
        future_to_job: dict[concurrent.futures.Future[JobResult], Job] = {}

        def submit_next(worker: Worker) -> None:
            try:
                job = next(job_iter)
            except StopIteration:
                return
            print(f"Dispatch {job.job_id} -> {worker.label}")
            future = pool.submit(
                run_one_job,
                worker,
                job,
                batch_id=batch_id,
                run_id=run_id,
                output_root=output_root,
                dry_run=args.dry_run,
            )
            future_to_job[future] = job

        idle_workers = workers[:max_parallel]
        for worker in idle_workers:
            submit_next(worker)

        while future_to_job:
            done, _ = concurrent.futures.wait(
                future_to_job,
                return_when=concurrent.futures.FIRST_COMPLETED,
            )
            for future in done:
                job = future_to_job.pop(future)
                result = future.result()
                result_by_job[job.job_id] = result
                results = list(result_by_job.values())
                write_state(state_file, results)
                if result.status == "success":
                    print(f"OK {job.job_id} on {result.worker}: {result.local_video}")
                elif result.status == "dry-run":
                    print(f"DRY {job.job_id} on {result.worker}")
                else:
                    print(f"FAILED {job.job_id} on {result.worker}: {result.error}")
                worker_label = result.worker
                next_worker = next(w for w in workers if w.label == worker_label)
                submit_next(next_worker)

    failures = [r for r in result_by_job.values() if r.status == "failed"]
    print(f"State: {state_file}")
    if failures:
        print(f"Completed with {len(failures)} failed job(s).")
        return 1
    print("All dispatched jobs completed.")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="MiniMax H3 SSH cluster runner")
    sub = parser.add_subparsers(dest="command", required=True)

    def add_common(p: argparse.ArgumentParser) -> None:
        p.add_argument("--servers", default="servers.yaml")
        p.add_argument("--jobs", default="jobs.yaml")

    validate = sub.add_parser("validate", help="validate server and job YAML")
    add_common(validate)
    validate.add_argument("--strict-assets", action="store_true")
    validate.set_defaults(func=command_validate)

    plan = sub.add_parser("plan", help="print job-to-worker assignment")
    add_common(plan)
    plan.add_argument("--limit", type=int, default=None)
    plan.set_defaults(func=command_plan)

    check = sub.add_parser("check", help="check SSH workers, conda, ComfyUI, models, and API")
    check.add_argument("--servers", default="servers.yaml")
    check.add_argument("--max-parallel", type=int, default=None)
    check.add_argument("--limit", type=int, default=None)
    check.add_argument("--timeout", type=float, default=300)
    check.add_argument("--start-comfy", action="store_true")
    check.add_argument("--upload-runner", action="store_true")
    check.set_defaults(func=command_check)

    run = sub.add_parser("run", help="dispatch jobs to SSH workers")
    add_common(run)
    run.add_argument("--output-root", default=DEFAULT_LOCAL_OUTPUT_ROOT)
    run.add_argument("--run-id", default=None)
    run.add_argument("--max-parallel", type=int, default=None)
    run.add_argument("--limit", type=int, default=None)
    run.add_argument("--rerun", action="store_true")
    run.add_argument("--dry-run", action="store_true")
    run.add_argument("--strict-assets", action="store_true")
    run.set_defaults(func=command_run)

    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        return int(args.func(args))
    except KeyboardInterrupt:
        return 130
    except ClusterError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
