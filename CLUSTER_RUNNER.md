# MiniMax H3 SSH Cluster Runner

This is the production-oriented control layer for batch MiniMax H3 ads.

The intended workflow:

```text
product brief + Image2 opening frame + references
-> jobs.yaml
-> cluster_runner.py
-> several SSH servers / ComfyUI workers
-> local MP4 folders
-> user review and second-pass edit
```

The runner does not store passwords. Use SSH keys, ssh-agent, or the normal
interactive SSH credential flow.

## Files

- `cluster_runner.py`: local orchestrator.
- `servers.example.yaml`: server and worker template.
- `jobs.example.yaml`: batch job template.
- `prompts/*.example.txt`: example 10s/15s MiniMax storyboard prompts.
- `cluster_outputs/`: local generated results, ignored by git.

## Server Model

One worker equals one ComfyUI endpoint.

Single GPU server:

```yaml
servers:
  - name: a100-cn-01
    host: 0.0.0.0
    ssh_port: 22
    workers:
      - name: gpu0
        gpu: 0
        comfy_port: 8189
```

Multi-GPU server:

```yaml
servers:
  - name: six-card-box
    host: 0.0.0.0
    workers:
      - {name: gpu0, gpu: 0, comfy_port: 8188}
      - {name: gpu1, gpu: 1, comfy_port: 8189}
      - {name: gpu2, gpu: 2, comfy_port: 8190}
```

Each worker runs one H3 job at a time. Do not run several H3 jobs through one
GPU/ComfyUI process.

## Job Model

For brand/product ads, prefer `r2v` with multiple references:

```yaml
jobs:
  - id: baozi-15s
    mode: r2v
    duration: 15
    width: 1344
    height: 768
    steps: 4
    turbo: true
    prompt_file: prompts/baozi_15s.example.txt
    ref_images:
      - assets/baozi/image2-opening-frame.png
      - assets/baozi/model-or-hands.png
      - assets/baozi/product.png
      - assets/baozi/product-logo.png
      - assets/baozi/scene.png
```

Reference image order matters:

1. Image2/OpenRouter opening frame.
2. Model/person/hands reference.
3. Product/package reference.
4. Product plus logo or official brand lockup.
5. Scene/kitchen/store/background reference.
6. Optional cooked/served result, packaging close-up, or style reference.

## Commands

Optional but recommended:

```powershell
python -m pip install -r requirements.txt
```

`cluster_runner.py` has a small built-in YAML fallback for the example schema,
but PyYAML is more complete for future config edits.

Copy examples first:

```powershell
Copy-Item servers.example.yaml servers.yaml
Copy-Item jobs.example.yaml jobs.yaml
```

Edit `servers.yaml` and `jobs.yaml`, then validate:

```powershell
python cluster_runner.py validate --servers servers.yaml --jobs jobs.yaml
```

Preflight-check SSH servers before running paid jobs:

```powershell
python cluster_runner.py check --servers servers.yaml
```

This checks SSH, GPU/driver, conda env, PyTorch/CUDA, ComfyUI files, required
MiniMax H3 model files, Turbo LoRA files, and the ComfyUI API/node status if the
worker port is already running.

To also upload the latest `h3_runner.py` and start ComfyUI if it is down:

```powershell
python cluster_runner.py check --servers servers.yaml --upload-runner --start-comfy
```

Print the assignment plan:

```powershell
python cluster_runner.py plan --servers servers.yaml --jobs jobs.yaml
```

Dry-run dispatch without SSH/SCP:

```powershell
python cluster_runner.py run --servers servers.yaml --jobs jobs.yaml --dry-run
```

Run for real:

```powershell
python cluster_runner.py run --servers servers.yaml --jobs jobs.yaml
```

Limit a test to the first job:

```powershell
python cluster_runner.py run --servers servers.yaml --jobs jobs.yaml --limit 1
```

Resume a known run ID:

```powershell
python cluster_runner.py run --servers servers.yaml --jobs jobs.yaml --run-id 20260809_test
```

## What Happens Per Job

For each job, the runner:

1. uploads `h3_runner.py` to the remote ComfyUI directory if enabled;
2. starts ComfyUI on the worker port if it is not already running;
3. uploads prompt and reference images to a remote job folder;
4. runs remote `h3_runner.py` against `http://127.0.0.1:<comfy_port>`;
5. downloads the generated MP4 and logs to local `cluster_outputs/`;
6. records job state in `cluster_outputs/<batch>/<run-id>/state.json`.

Local result shape:

```text
cluster_outputs/
  demo-food-ads/
    20260809_153000/
      baozi-15s/
        job.json
        prompt.txt
        run_remote.sh
        ssh-output.log
        runner.log
        <generated>.mp4
      state.json
```

## Failure Behavior

- If a worker fails, that job is marked `failed` in `state.json`.
- Successful jobs are skipped when resuming the same `--run-id`, unless
  `--rerun` is passed.
- Failed jobs can be retried by reusing the same run ID after fixing the server
  or assets.
- If a server crashes, inspect the per-job logs and rerun the batch. The runner
  will not delete remote files.

## Production Notes

- Use `1344x768`, `duration: 10` or `15`, `steps: 4`, `turbo: true` for batch.
- Use `turbo_low_vram: true` for native 1080-ish runs on A100 40G.
- Keep `no_audio: true` for MiniMax H3 food ads; finish BGM/voice/captions in editing.
- CPU upgrades are not the main speed lever. More GPUs or more servers are.
- Keep secrets out of YAML. Put SSH config in `~/.ssh/config` or use keys.
- The user reviews and edits. The runner stops after local MP4 handoff.
