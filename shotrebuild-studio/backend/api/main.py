from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from backend.db.database import execute, fetch_all, init_db
from backend.db.seed import seed_initial_data
from backend.models.entities import (
    AssetCreate,
    ProjectCreate,
    ProviderCreate,
    ProviderJobSubmitRequest,
    ProviderModelCreate,
    WorkflowCreate,
)
from backend.services.provider_jobs import (
    fetch_provider_job_outputs,
    get_provider_job_status,
    create_provider_job,
)
from backend.services.provider_registry import PROVIDERS

app = FastAPI(title="ShotRebuild Studio Backend", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    init_db()
    seed_initial_data()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "shotrebuild-studio-backend"}


@app.get("/providers")
def list_providers() -> list[dict]:
    rows = fetch_all("SELECT id, name, provider_type, enabled, config_json FROM providers ORDER BY id ASC")
    result = []
    for row in rows:
        impl = PROVIDERS.get(row["name"])
        result.append(
            {
                **row,
                "health": impl.health_check() if impl else {"status": "unknown"},
                "capabilities": impl.list_capabilities() if impl else [],
            }
        )
    return result


@app.post("/providers")
def create_provider(provider: ProviderCreate) -> dict:
    provider_id = execute(
        "INSERT INTO providers(name, provider_type, enabled, config_json) VALUES (?, ?, ?, ?)",
        (provider.name, provider.provider_type, provider.enabled, provider.config_json),
    )
    return {"id": provider_id, **provider.model_dump()}


@app.get("/providers/comfyui/health")
def comfyui_health() -> dict:
    provider = PROVIDERS.get("comfyui")
    if not provider:
        raise HTTPException(status_code=404, detail="ComfyUI provider not found")
    return provider.health_check()


@app.get("/providers/comfyui/models")
def comfyui_models() -> list[dict]:
    provider = PROVIDERS.get("comfyui")
    if not provider:
        raise HTTPException(status_code=404, detail="ComfyUI provider not found")
    return provider.list_models()


@app.get("/models")
def list_models(provider: str | None = Query(default=None)) -> list[dict]:
    if provider:
        return fetch_all(
            """
            SELECT m.id, p.name AS provider, m.provider_id, m.model_key, m.display_name, m.capabilities, m.is_default
            FROM provider_models m
            JOIN providers p ON p.id = m.provider_id
            WHERE p.name = ?
            ORDER BY m.id ASC
            """,
            (provider,),
        )
    return fetch_all(
        """
        SELECT m.id, p.name AS provider, m.provider_id, m.model_key, m.display_name, m.capabilities, m.is_default
        FROM provider_models m
        JOIN providers p ON p.id = m.provider_id
        ORDER BY m.id ASC
        """
    )


@app.post("/models")
def create_model(model: ProviderModelCreate) -> dict:
    model_id = execute(
        "INSERT INTO provider_models(provider_id, model_key, display_name, capabilities, is_default) VALUES (?, ?, ?, ?, ?)",
        (model.provider_id, model.model_key, model.display_name, model.capabilities, model.is_default),
    )
    return {"id": model_id, **model.model_dump()}


@app.get("/workflows")
def list_workflows(provider: str | None = Query(default=None)) -> list[dict]:
    if provider:
        return fetch_all(
            """
            SELECT w.id, p.name AS provider, w.provider_id, w.workflow_key, w.name, w.definition_json
            FROM workflows w
            LEFT JOIN providers p ON p.id = w.provider_id
            WHERE p.name = ?
            ORDER BY w.id ASC
            """,
            (provider,),
        )
    return fetch_all(
        """
        SELECT w.id, p.name AS provider, w.provider_id, w.workflow_key, w.name, w.definition_json
        FROM workflows w
        LEFT JOIN providers p ON p.id = w.provider_id
        ORDER BY w.id ASC
        """
    )


@app.post("/workflows")
def create_workflow(workflow: WorkflowCreate) -> dict:
    workflow_id = execute(
        "INSERT INTO workflows(provider_id, workflow_key, name, definition_json) VALUES (?, ?, ?, ?)",
        (workflow.provider_id, workflow.workflow_key, workflow.name, workflow.definition_json),
    )
    return {"id": workflow_id, **workflow.model_dump()}


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
def submit_provider_job(provider_name: str, request: ProviderJobSubmitRequest) -> dict:
    payload = request.prompt
    if request.model_key:
        payload = {**payload, "model_key": request.model_key}
    return create_provider_job(provider_name, payload, workflow_id=request.workflow_id)


@app.get("/provider_jobs/{job_id}/status")
def provider_job_status(job_id: int) -> dict:
    return get_provider_job_status(job_id)


@app.get("/provider_jobs/{job_id}/outputs")
def provider_job_outputs(job_id: int) -> dict:
    return fetch_provider_job_outputs(job_id)
