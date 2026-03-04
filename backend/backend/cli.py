from __future__ import annotations

import asyncio
from pathlib import Path

import typer
from rich import print

from backend.pipeline import analyze_video
from backend.scanner.service import scan_videos
from backend.settings import settings
from backend.model_provider.config import load_models_config
from backend.model_provider.factory import create_provider
from backend.embedding.search import search_videos
from backend.indexer.service import load_index
from backend.embedding.build_index import build_index
from backend.watcher.watcher import IngestWatcher

app = typer.Typer(add_completion=False, help="video-clip-tagger CLI")


@app.command()
def start() -> None:
    """One-command start: Ollama (if needed) + API + UI + open browser."""
    import subprocess

    root = Path(__file__).resolve().parents[2]  # .../backend
    script = root / "scripts" / "start.sh"
    subprocess.run(["bash", str(script)], check=False)


@app.command()
def stop() -> None:
    """Stop API/UI (and ollama if started by script)."""
    import subprocess

    root = Path(__file__).resolve().parents[2]
    script = root / "scripts" / "stop.sh"
    subprocess.run(["bash", str(script)], check=False)


@app.command()
def doctor() -> None:
    """Run system health checks and print a readiness report."""
    from backend.health.model_health import check_ollama
    from backend.health.system_health import check_ffmpeg, check_clips_dir, check_storage_writable
    from backend.model_provider.config import load_models_config

    cfg = load_models_config(settings.models_config_path)
    local_cfg = cfg.providers.get("local", {})
    host = str(local_cfg.get("host", "http://localhost:11434"))
    model = str(local_cfg.get("model", "llava:13b"))

    # API server check (optional)
    api_base = "http://localhost:8000"
    api_ok = False
    try:
        import httpx

        r = httpx.get(f"{api_base}/health", timeout=1.5)
        api_ok = r.status_code == 200
    except Exception:
        api_ok = False

    print(f"System Check")
    print(f"API server: {'OK' if api_ok else 'offline'} ({api_base})")

    oll = check_ollama(host=host, required_model=model)
    if oll.get("status") == "offline":
        print("Ollama: offline")
        print("Hint: Run: ollama serve")
    else:
        print("Ollama: OK")
        if oll.get("model") == "missing":
            print(f"Model {model}: missing")
            print(f"Hint: Run: ollama pull {model}")
        else:
            print(f"Model {model}: OK")

    ff = check_ffmpeg()
    print(f"ffmpeg: {'OK' if ff.get('status') == 'ok' else 'missing'}")

    clips = check_clips_dir()
    print(f"clips dir: {'OK' if clips.get('status') == 'ok' else 'missing'} ({clips.get('path')})")

    st = check_storage_writable()
    print(f"storage: {'OK' if st.get('status') == 'ok' else st.get('status')} ({st.get('path')})")

    ready = (
        oll.get("status") == "running"
        and oll.get("model") != "missing"
        and ff.get("status") == "ok"
        and clips.get("status") == "ok"
        and st.get("status") == "ok"
    )
    print("Ready" if ready else "Not ready")


@app.command()
def build_index() -> None:
    """Rebuild FAISS embeddings index from storage/library/index.json."""
    items = load_index(settings.index_path)
    r = build_index(items)
    print(r)


@app.command()
def search(query: str, top_k: int = 5) -> None:
    """Semantic search videos by text query."""
    hits = search_videos(query, top_k=top_k)
    print("Top Results")
    for h in hits:
        print(f"{h['file']}\t{h['score']}")


@app.command()
def watch(scan_existing: bool = typer.Option(False, "--scan-existing", help="Enqueue existing mp4 on start")) -> None:
    """Watch clips dir and auto-ingest new mp4: clips -> processing -> library (or failed)."""
    w = IngestWatcher(settings.clips_dir)
    w.start(scan_existing=scan_existing)
    try:
        while True:
            import time

            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        w.stop()


@app.command()
def scan() -> None:
    """Scan ~/ai-video-factory/clips for *.mp4 and analyze all."""
    videos = scan_videos(settings.clips_dir)
    print(f"Found {len(videos)} videos")

    async def run():
        # naive sequential CLI run; API has parallel mode
        for v in videos:
            print(f"Analyzing {v.path}")
            r = await analyze_video(v.path)
            print(r)

    asyncio.run(run())


@app.command()
def tag(path: str) -> None:
    """Analyze a single video (mp4) OR a single image frame (jpg/png).

    Examples:
      video-clip-tagger tag ~/ai-video-factory/clips/clip.mp4
      video-clip-tagger tag frame.jpg
    """

    p = Path(path).expanduser().resolve()

    async def run():
        suf = p.suffix.lower()
        if suf in {".jpg", ".jpeg", ".png", ".webp"}:
            cfg = load_models_config(settings.models_config_path)
            provider_cfg = cfg.providers.get(cfg.active_provider, {})
            provider = create_provider(cfg.active_provider, provider_cfg)
            r = await provider.analyze_image(p)
            print(r)
            return

        r = await analyze_video(p)
        print(r)

    asyncio.run(run())


if __name__ == "__main__":
    app()
