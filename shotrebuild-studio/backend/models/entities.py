from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str
    description: str = ""


class AssetCreate(BaseModel):
    project_id: int | None = None
    asset_type: str
    uri: str
    metadata: str = "{}"


class ProviderCreate(BaseModel):
    name: str
    provider_type: str
    enabled: int = 1
    config_json: str = "{}"


class ProviderModelCreate(BaseModel):
    provider_id: int
    model_key: str
    display_name: str
    capabilities: str = "[]"
    is_default: int = 0


class WorkflowCreate(BaseModel):
    provider_id: int | None = None
    workflow_key: str
    name: str
    definition_json: str = "{}"


class ProviderJobSubmitRequest(BaseModel):
    workflow_id: int | None = None
    model_key: str | None = None
    prompt: dict = Field(default_factory=dict)
