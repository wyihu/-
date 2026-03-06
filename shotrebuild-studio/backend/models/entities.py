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


class ProviderUpdate(BaseModel):
    provider_type: str | None = None
    enabled: int | None = None
    config_json: str | None = None


class ProviderModelCreate(BaseModel):
    provider_id: int
    model_key: str
    display_name: str
    capabilities: str = "[]"
    is_default: int = 0


class ProviderModelUpdate(BaseModel):
    model_key: str | None = None
    display_name: str | None = None
    capabilities: str | None = None
    is_default: int | None = None


class WorkflowCreate(BaseModel):
    provider_id: int | None = None
    workflow_key: str
    name: str
    definition_json: str = "{}"


class WorkflowUpdate(BaseModel):
    workflow_key: str | None = None
    name: str | None = None
    definition_json: str | None = None


class ProviderJobSubmitRequest(BaseModel):
    workflow_id: int | None = None
    model_key: str | None = None
    fallback_provider: str | None = None
    fallback_model_key: str | None = None
    max_retries: int = 0
    prompt: dict = Field(default_factory=dict)


class ProviderJobRetryRequest(BaseModel):
    max_retries: int | None = None
