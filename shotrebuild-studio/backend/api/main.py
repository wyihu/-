from fastapi import FastAPI, HTTPException

from backend.db.database import execute, fetch_all, init_db
from backend.models.entities import AssetCreate, ProjectCreate
from backend.services.provider_registry import PROVIDERS

app = FastAPI(title="ShotRebuild Studio Backend", version="0.1.0")


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "shotrebuild-studio-backend"}


@app.get("/providers")
def list_providers() -> list[dict]:
    return [
        {
            "name": name,
            "health": provider.health_check(),
            "capabilities": provider.list_capabilities(),
        }
        for name, provider in PROVIDERS.items()
    ]


@app.get("/models")
def list_models() -> list[dict]:
    result: list[dict] = []
    for name, provider in PROVIDERS.items():
        for model in provider.list_models():
            result.append({"provider": name, **model})
    return result


@app.get("/workflows")
def list_workflows() -> list[dict]:
    return [
        {"provider": "comfyui", "workflow_key": "comfyui-basic-mock", "name": "ComfyUI Basic (Mock)"},
        {"provider": "jimeng", "workflow_key": "jimeng-basic-mock", "name": "即梦 Basic (Mock)"},
        {"provider": "kling", "workflow_key": "kling-basic-mock", "name": "可灵 Basic (Mock)"},
    ]


@app.get("/projects")
def get_projects() -> list[dict]:
    return fetch_all("SELECT id, name, description, status, created_at FROM projects ORDER BY id DESC")


@app.post("/projects")
def create_project(project: ProjectCreate) -> dict:
    project_id = execute(
        "INSERT INTO projects(name, description, status) VALUES (?, ?, ?)",
        (project.name, project.description, "draft"),
    )
    return {"id": project_id, "name": project.name, "description": project.description, "status": "draft"}


@app.get("/assets")
def get_assets() -> list[dict]:
    return fetch_all("SELECT id, project_id, asset_type, uri, metadata, created_at FROM assets ORDER BY id DESC")


@app.post("/assets")
def create_asset(asset: AssetCreate) -> dict:
    asset_id = execute(
        "INSERT INTO assets(project_id, asset_type, uri, metadata) VALUES (?, ?, ?, ?)",
        (asset.project_id, asset.asset_type, asset.uri, asset.metadata),
    )
    return {"id": asset_id, **asset.model_dump()}


@app.post("/providers/{provider_name}/jobs")
def submit_provider_job(provider_name: str, payload: dict) -> dict:
    provider = PROVIDERS.get(provider_name)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider.submit_job(payload)
