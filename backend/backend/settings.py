from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=None)

    clips_dir: Path = Path.home() / "ai-video-factory" / "clips"
    processing_dir: Path = Path.home() / "ai-video-factory" / "processing"
    failed_dir: Path = Path.home() / "ai-video-factory" / "failed"

    frames_dir: Path = Path("storage") / "frames"
    index_path: Path = Path("storage") / "library" / "index.json"
    models_config_path: Path = Path("config") / "models.yaml"

    logs_dir: Path = Path("logs")
    ingest_log_path: Path = Path("logs") / "ingest.log"

    # parallelism
    max_workers: int = 8


settings = Settings()
