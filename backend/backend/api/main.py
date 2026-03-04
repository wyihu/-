from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from backend.model_provider.config import load_models_config, save_models_config
from backend.pipeline import analyze_video
from backend.scanner.service import scan_videos_dict
from backend.settings import settings
from backend.types import ProviderKind
from backend.health.model_health import check_ollama
from backend.health.system_health import system_health
from backend.embedding.search import search_videos
from backend.watcher.watcher import IngestWatcher

app = FastAPI(title="video-clip-tagger")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"] ,
)

# very small in-memory queue/state
STATE: dict[str, Any] = {
    "queue": [],
    "running": 0,
    "done": 0,
    "last_error": None,
}

# ingest watcher singleton
WATCHER = {"instance": None}


@app.get("/videos")
def get_videos() -> list[dict]:
    return scan_videos_dict(settings.clips_dir)


@app.get("/status")
def status() -> dict[str, Any]:
    cfg = load_models_config(settings.models_config_path)
    w = WATCHER.get("instance")
    ingest = None
    if w is not None:
        ingest = {
            "running": w.state.running,
            "current": w.state.current,
            "queue": list(w.state.queue),
            "failed_count": w.state.failed_count,
            "last_error": w.state.last_error,
        }
    return {
        "clips_dir": str(settings.clips_dir),
        "active_provider": cfg.active_provider,
        "queue": STATE["queue"],
        "running": STATE["running"],
        "done": STATE["done"],
        "last_error": STATE["last_error"],
        "ingest": ingest,
    }


@app.get("/health")
def health() -> dict[str, Any]:
    """Unified health check for system + model configuration."""
    sys = system_health()

    cfg = load_models_config(settings.models_config_path)

    # model config presence checks
    def configured(kind: str) -> bool:
        p = cfg.providers.get(kind, {})
        key = p.get("api_key")
        return bool(key) and "${" not in str(key)

    local_ok = False
    local_detail = check_ollama(
        host=str(cfg.providers.get("local", {}).get("host", "http://localhost:11434")),
        required_model=str(cfg.providers.get("local", {}).get("model", "llava:13b")),
    )
    if local_detail.get("status") == "running" and local_detail.get("model") != "missing":
        local_ok = True

    models = {
        "local": "ok" if local_ok else ("offline" if local_detail.get("status") == "offline" else "missing"),
        "openai": "ok" if configured("openai") else "not_configured",
        "gemini": "ok" if configured("google") else "not_configured",
        "qwen": "ok" if configured("qwen") else "not_configured",
        "deepseek": "ok" if configured("deepseek") else "not_configured",
    }

    overall_ok = (
        sys.get("system") == "ok"
        and sys.get("ffmpeg") == "ok"
        and sys.get("storage") == "ok"
        and sys.get("clips") == "ok"
        and models["local"] == "ok"
    )

    return {
        "system": "ok" if overall_ok else "degraded",
        "models": models,
        "ffmpeg": sys.get("ffmpeg"),
        "storage": sys.get("storage"),
        "clips": sys.get("clips"),
        "details": {"system": sys.get("details"), "ollama": local_detail},
    }


@app.get("/models/local/status")
def local_model_status() -> dict[str, Any]:
    cfg = load_models_config(settings.models_config_path)
    host = str(cfg.providers.get("local", {}).get("host", "http://localhost:11434"))
    model = str(cfg.providers.get("local", {}).get("model", "llava:13b"))
    return check_ollama(host=host, required_model=model)


@app.post("/watch/start")
def watch_start(scan_existing: bool = False) -> dict[str, Any]:
    if WATCHER.get("instance") is not None and WATCHER["instance"].state.running:
        return {"status": "already_running"}

    w = IngestWatcher(settings.clips_dir)
    w.start(scan_existing=scan_existing)
    WATCHER["instance"] = w
    return {"status": "started", "scan_existing": scan_existing}


@app.post("/watch/stop")
def watch_stop() -> dict[str, Any]:
    w = WATCHER.get("instance")
    if w is None:
        return {"status": "not_running"}
    w.stop()
    WATCHER["instance"] = None
    return {"status": "stopped"}


@app.post("/models/switch")
def switch_model(provider: ProviderKind) -> dict[str, Any]:
    cfg = load_models_config(settings.models_config_path)
    if provider not in cfg.providers:
        raise ValueError(f"Unknown provider: {provider}")
    cfg.active_provider = provider
    save_models_config(settings.models_config_path, cfg)
    return {"active_provider": cfg.active_provider}


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)) -> dict[str, Any]:
    # Save to temp in clips dir (or cwd storage) then run pipeline
    tmp_dir = Path("storage") / "uploads"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    tmp_path = tmp_dir / file.filename

    data = await file.read()
    tmp_path.write_bytes(data)

    try:
        result = await analyze_video(tmp_path)
    finally:
        # keep upload file for debugging; comment out if you want cleanup
        pass

    return result


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


@app.post("/search")
def search(req: SearchRequest) -> list[dict[str, Any]]:
    return search_videos(req.query, top_k=req.top_k)


@app.post("/scan")
async def scan_and_analyze() -> dict[str, Any]:
    videos = scan_videos_dict(settings.clips_dir)
    paths = [Path(v["path"]) for v in videos]

    # bounded concurrency
    sem = asyncio.Semaphore(settings.max_workers)

    async def run_one(p: Path):
        async with sem:
            STATE["running"] += 1
            try:
                return await analyze_video(p)
            except Exception as e:
                STATE["last_error"] = f"{p}: {e}"
                return {"video": str(p), "error": str(e)}
            finally:
                STATE["running"] -= 1
                STATE["done"] += 1

    STATE["queue"] = [str(p) for p in paths]
    STATE["done"] = 0
    results = await asyncio.gather(*(run_one(p) for p in paths))
    STATE["queue"] = []
    return {"count": len(results), "results": results}
