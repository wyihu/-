#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PID_DIR="$ROOT_DIR/logs"
PID_FILE="$PID_DIR/pids.json"

mkdir -p "$PID_DIR"

log() {
  echo "[start] $*"
}

is_ollama_running() {
  curl -fsS "http://localhost:11434/api/tags" >/dev/null 2>&1
}

start_ollama() {
  if is_ollama_running; then
    log "Ollama: already running"
    return 0
  fi

  if command -v ollama >/dev/null 2>&1; then
    log "Ollama: starting (ollama serve &)"
    (nohup ollama serve >"$PID_DIR/ollama.out" 2>&1 & echo $! >"$PID_DIR/ollama.pid") || true

    for i in {1..30}; do
      if is_ollama_running; then
        log "Ollama: running"
        return 0
      fi
      sleep 0.2
    done

    log "Ollama: still not responding on 11434 (continuing)"
  else
    log "Ollama: binary not found (skip)"
  fi
}

start_backend() {
  log "Backend: starting uvicorn on :8000"
  cd "$ROOT_DIR"
  (nohup python3 -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 >"$PID_DIR/backend.out" 2>&1 & echo $! >"$PID_DIR/backend.pid")
}

start_frontend() {
  log "Frontend: starting Next.js dev server on :3000"
  cd "$ROOT_DIR/frontend"

  if [ ! -d node_modules ]; then
    log "Frontend: node_modules missing, running npm install"
    npm install >"$PID_DIR/frontend.install.out" 2>&1
  fi

  (nohup npm run dev >"$PID_DIR/frontend.out" 2>&1 & echo $! >"$PID_DIR/frontend.pid")
}

write_pid_json() {
  local ollama_pid="" backend_pid="" frontend_pid=""
  [[ -f "$PID_DIR/ollama.pid" ]] && ollama_pid="$(cat "$PID_DIR/ollama.pid" || true)"
  [[ -f "$PID_DIR/backend.pid" ]] && backend_pid="$(cat "$PID_DIR/backend.pid" || true)"
  [[ -f "$PID_DIR/frontend.pid" ]] && frontend_pid="$(cat "$PID_DIR/frontend.pid" || true)"

  cat >"$PID_FILE" <<EOF
{
  "ollama": "${ollama_pid}",
  "backend": "${backend_pid}",
  "frontend": "${frontend_pid}"
}
EOF
}

open_browser() {
  local url="http://localhost:3000"
  log "Opening browser: $url"
  if command -v open >/dev/null 2>&1; then
    open "$url" >/dev/null 2>&1 || true
  elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$url" >/dev/null 2>&1 || true
  else
    log "No browser opener found (open/xdg-open)."
  fi
}

start_ollama
start_backend
start_frontend
write_pid_json
open_browser

log "Done. PIDs recorded in $PID_DIR/*.pid"
