from __future__ import annotations

import asyncio
import shutil
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileMovedEvent
from watchdog.observers import Observer

from backend.pipeline import analyze_video
from backend.settings import settings


def _now() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S")


def _log(line: str) -> None:
    settings.logs_dir.mkdir(parents=True, exist_ok=True)
    settings.ingest_log_path.parent.mkdir(parents=True, exist_ok=True)
    settings.ingest_log_path.write_text(
        settings.ingest_log_path.read_text(encoding="utf-8") + line + "\n"
        if settings.ingest_log_path.exists()
        else line + "\n",
        encoding="utf-8",
    )


def _wait_stable(path: Path, timeout_s: float = 30.0, stable_for_s: float = 1.0) -> bool:
    """Wait until file size stops changing (best-effort)."""
    start = time.time()
    last_size = -1
    stable_since = None

    while time.time() - start < timeout_s:
        if not path.exists():
            return False
        size = path.stat().st_size
        if size == last_size:
            if stable_since is None:
                stable_since = time.time()
            if time.time() - stable_since >= stable_for_s:
                return True
        else:
            stable_since = None
            last_size = size
        time.sleep(0.2)
    return False


@dataclass
class IngestState:
    running: bool = False
    queue: list[str] = field(default_factory=list)
    current: str | None = None
    failed_count: int = 0
    last_error: str | None = None


class _Handler(FileSystemEventHandler):
    def __init__(self, enqueue: Callable[[Path], None]):
        self.enqueue = enqueue

    def on_created(self, event: FileCreatedEvent):
        if event.is_directory:
            return
        p = Path(event.src_path)
        if p.suffix.lower() == ".mp4":
            self.enqueue(p)

    def on_moved(self, event: FileMovedEvent):
        if event.is_directory:
            return
        p = Path(event.dest_path)
        if p.suffix.lower() == ".mp4":
            self.enqueue(p)


class IngestWatcher:
    """Watch clips_dir and ingest new mp4 files.

    Flow: clips -> processing -> (on success) storage/library (handled by pipeline) else -> failed
    """

    def __init__(self, clips_dir: Path | None = None):
        self.clips_dir = (clips_dir or settings.clips_dir).expanduser().resolve()
        self.processing_dir = settings.processing_dir.expanduser().resolve()
        self.failed_dir = settings.failed_dir.expanduser().resolve()
        self.observer = Observer()
        self.state = IngestState()

        self.processing_dir.mkdir(parents=True, exist_ok=True)
        self.failed_dir.mkdir(parents=True, exist_ok=True)

        self._handler = _Handler(self.enqueue)
        self._worker_stop = False
        self._worker = None

    def start(self, scan_existing: bool = False) -> None:
        import threading

        self.clips_dir.mkdir(parents=True, exist_ok=True)
        self.observer.schedule(self._handler, str(self.clips_dir), recursive=True)
        self.observer.start()
        self.state.running = True
        _log(f"{_now()}\tWATCHER_START\t{self.clips_dir}")

        if scan_existing:
            for p in sorted(self.clips_dir.rglob("*.mp4")):
                self.enqueue(p)
            _log(f"{_now()}\tSCAN_EXISTING\tcount={len(list(self.clips_dir.rglob('*.mp4')))}")

        # background worker to drain queue
        self._worker_stop = False

        def loop():
            while not self._worker_stop:
                try:
                    self._drain_once()
                except Exception:
                    pass
                time.sleep(0.3)

        self._worker = threading.Thread(target=loop, name="ingest-worker", daemon=True)
        self._worker.start()

    def stop(self) -> None:
        self._worker_stop = True
        try:
            self.observer.stop()
            self.observer.join(timeout=5)
        finally:
            self.state.running = False
            _log(f"{_now()}\tWATCHER_STOP")

    def enqueue(self, path: Path) -> None:
        p = path.expanduser().resolve()
        s = str(p)
        if s not in self.state.queue and s != self.state.current:
            self.state.queue.append(s)
            _log(f"{_now()}\tENQUEUE\t{s}")

    def run_forever(self, poll_interval_s: float = 0.5) -> None:
        """Start watcher and process queue in the foreground."""
        self.start()
        try:
            while True:
                self._drain_once()
                time.sleep(poll_interval_s)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()

    def _drain_once(self) -> None:
        if not self.state.queue or self.state.current is not None:
            return

        next_path = Path(self.state.queue.pop(0))
        self.state.current = str(next_path)

        try:
            if not _wait_stable(next_path):
                raise RuntimeError("file not stable / disappeared")

            # move into processing
            dest = self.processing_dir / next_path.name
            try:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(next_path), str(dest))
            except Exception:
                # maybe already moved; continue with original
                dest = next_path

            _log(f"{_now()}\tPROCESS_START\t{dest}")

            # run async pipeline
            result: dict[str, Any] = asyncio.run(analyze_video(dest))
            _log(f"{_now()}\tPROCESS_OK\t{dest}\t{result.get('index_item', {})}")

            # pipeline already moved file to storage/library
            self.state.last_error = None
        except Exception as e:
            self.state.failed_count += 1
            self.state.last_error = str(e)
            _log(f"{_now()}\tPROCESS_FAIL\t{self.state.current}\t{e}")

            # move to failed if file exists
            try:
                p = Path(self.state.current)
                if p.exists():
                    self.failed_dir.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(p), str(self.failed_dir / p.name))
            except Exception:
                pass
        finally:
            self.state.current = None
