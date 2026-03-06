from pydantic import BaseModel


class ProjectCreate(BaseModel):
    name: str
    description: str = ""


class AssetCreate(BaseModel):
    project_id: int | None = None
    asset_type: str
    uri: str
    metadata: str = "{}"
