#!/usr/bin/env bash
set -euo pipefail

# Start ComfyUI and run a MiniMax-H3 Turbo I2V probe.
#
# Optional env:
#   COMFYUI_DIR=/root/ComfyUI
#   CONDA_ENV=comfy_h3_torch29_cu126
#   PORT=8189
#   WIDTH=768
#   HEIGHT=448
#   DURATION=5
#   STEPS=8
#   TURBO_LOW_VRAM=0

COMFYUI_DIR="${COMFYUI_DIR:-/root/ComfyUI}"
CONDA_ENV="${CONDA_ENV:-comfy_h3_torch29_cu126}"
PORT="${PORT:-8189}"
WIDTH="${WIDTH:-768}"
HEIGHT="${HEIGHT:-448}"
DURATION="${DURATION:-5}"
STEPS="${STEPS:-8}"
TURBO_LOW_VRAM="${TURBO_LOW_VRAM:-0}"
PROMPT="${PROMPT:-A cinematic product-style shot, slow camera push in, soft practical light, synchronized ambient room tone.}"
PREFIX="${PREFIX:-test_outputs/h3_turbo_probe_${WIDTH}x${HEIGHT}_${STEPS}step}"

activate_python() {
  if command -v conda >/dev/null 2>&1; then
    # shellcheck disable=SC1091
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate "$CONDA_ENV"
  elif [ -f "$COMFYUI_DIR/venv/bin/activate" ]; then
    # shellcheck disable=SC1091
    source "$COMFYUI_DIR/venv/bin/activate"
  fi
}

wait_for_comfy() {
  local url="http://127.0.0.1:${PORT}/system_stats"
  for _ in $(seq 1 90); do
    if curl -fsS "$url" >/dev/null 2>&1; then
      return 0
    fi
    sleep 2
  done
  echo "ComfyUI did not become ready. Last log lines:" >&2
  tail -n 120 "$COMFYUI_DIR/comfyui_h3.log" >&2 || true
  exit 4
}

start_comfy() {
  cd "$COMFYUI_DIR"
  if curl -fsS "http://127.0.0.1:${PORT}/system_stats" >/dev/null 2>&1; then
    echo "ComfyUI already running on port $PORT"
    return
  fi

  if [ -f comfyui_h3.pid ] && kill -0 "$(cat comfyui_h3.pid)" >/dev/null 2>&1; then
    echo "Stopping stale ComfyUI process $(cat comfyui_h3.pid)"
    kill "$(cat comfyui_h3.pid)" || true
    sleep 3
  fi

  echo "Starting ComfyUI on 127.0.0.1:$PORT"
  nohup python main.py --listen 127.0.0.1 --port "$PORT" --lowvram > comfyui_h3.log 2>&1 &
  echo $! > comfyui_h3.pid
  wait_for_comfy
}

make_probe_image() {
  cd "$COMFYUI_DIR"
  if [ -f h3_probe_input.png ]; then
    return
  fi
  python - <<'PY'
from PIL import Image, ImageDraw

w, h = 768, 448
img = Image.new("RGB", (w, h), "#1b2230")
draw = ImageDraw.Draw(img)
for y in range(h):
    c = int(30 + 80 * y / h)
    draw.line([(0, y), (w, y)], fill=(c, 40, 80 + c // 2))
draw.ellipse((80, 70, 220, 210), fill=(245, 180, 80))
draw.rounded_rectangle((310, 150, 520, 310), radius=24, fill=(70, 130, 210), outline=(240, 240, 255), width=4)
draw.text((70, 355), "MiniMax H3 Turbo probe", fill=(245, 245, 245))
img.save("h3_probe_input.png")
PY
}

run_probe() {
  cd "$COMFYUI_DIR"
  if [ ! -f h3_runner.py ]; then
    echo "Missing $COMFYUI_DIR/h3_runner.py. Upload the local h3_runner.py first." >&2
    exit 5
  fi

  local extra=()
  if [ "$TURBO_LOW_VRAM" = "1" ]; then
    extra+=(--turbo-low-vram)
  fi

  mkdir -p test_outputs
  echo "Running Turbo probe: ${WIDTH}x${HEIGHT}, duration=${DURATION}s, steps=${STEPS}, low_vram=${TURBO_LOW_VRAM}"
  /usr/bin/time -p python h3_runner.py i2v \
    --server "http://127.0.0.1:${PORT}" \
    --prompt "$PROMPT" \
    --first-frame h3_probe_input.png \
    --width "$WIDTH" \
    --height "$HEIGHT" \
    --duration "$DURATION" \
    --steps "$STEPS" \
    --seed 2026080806 \
    --prefix "$PREFIX" \
    --output-dir test_outputs \
    --overwrite-upload \
    --turbo \
    "${extra[@]}"
}

main() {
  activate_python
  bash "$COMFYUI_DIR/server_scripts/install_h3_turbo.sh"
  start_comfy
  make_probe_image
  run_probe
}

main "$@"
