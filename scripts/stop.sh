#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PID_DIR="$ROOT_DIR/logs"

log() {
  echo "[stop] $*"
}

kill_pid_file() {
  local name="$1"
  local file="$PID_DIR/${name}.pid"
  if [[ ! -f "$file" ]]; then
    log "$name: pid file not found ($file)"
    return 0
  fi

  local pid
  pid="$(cat "$file" || true)"
  if [[ -z "$pid" ]]; then
    log "$name: empty pid"
    rm -f "$file" || true
    return 0
  fi

  if kill -0 "$pid" >/dev/null 2>&1; then
    log "$name: killing pid $pid"
    kill "$pid" >/dev/null 2>&1 || true
    sleep 0.3
    kill -9 "$pid" >/dev/null 2>&1 || true
  else
    log "$name: pid $pid not running"
  fi

  rm -f "$file" || true
}

kill_pid_file frontend
kill_pid_file backend
# only stop ollama if we started it (pid file exists)
kill_pid_file ollama

log "Done."
