#!/usr/bin/env bash
set -euo pipefail

# macOS desktop entrypoint for Video Clip Tagger
# Starts: Ollama (if needed) + FastAPI + Next.js, then opens the UI.

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$ROOT_DIR/logs"
mkdir -p "$LOG_DIR"

log() { echo "[app_start] $*"; }

is_ollama_running() {
  curl -fsS "http://127.0.0.1:11434/api/tags" >/dev/null 2>&1
}

start_ollama() {
  if is_ollama_running; then
    log "Ollama: running"
    return 0
  fi

  if command -v ollama >/dev/null 2>&1; then
    log "Ollama: starting (ollama serve &)"
    nohup ollama serve >"$LOG_DIR/ollama.out" 2>&1 &
    echo $! >"$LOG_DIR/ollama.pid"

    for _ in {1..50}; do
      if is_ollama_running; then
        log "Ollama: up"
        return 0
      fi
      sleep 0.2
    done

    log "Ollama: still not responding (continuing anyway)"
  else
    log "Ollama: not found in PATH (skip)"
  fi
}

start_backend() {
  if lsof -nP -iTCP:8000 -sTCP:LISTEN >/dev/null 2>&1; then
    log "Backend: already listening on 8000"
    return 0
  fi

  log "Backend: starting on 127.0.0.1:8000"
  cd "$ROOT_DIR"
  nohup python3 -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8000 >"$LOG_DIR/backend.out" 2>&1 &
  echo $! >"$LOG_DIR/backend.pid"
}

start_frontend() {
  if lsof -nP -iTCP:3000 -sTCP:LISTEN >/dev/null 2>&1; then
    log "Frontend: already listening on 3000"
    return 0
  fi

  log "Frontend: starting on 127.0.0.1:3000"
  cd "$ROOT_DIR/frontend"

  if [ ! -d node_modules ]; then
    log "Frontend: installing deps (npm install)"
    npm install >"$LOG_DIR/frontend.install.out" 2>&1
  fi

  export NEXT_PUBLIC_API_BASE="http://localhost:8000"
  nohup npm run dev -- --port 3000 >"$LOG_DIR/frontend.out" 2>&1 &
  echo $! >"$LOG_DIR/frontend.pid"
}

open_ui() {
  log "Opening UI: http://localhost:3000"
  open "http://localhost:3000" >/dev/null 2>&1 || true
}

start_ollama
start_backend
start_frontend

sleep 3
open_ui
