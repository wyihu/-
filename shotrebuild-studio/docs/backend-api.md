# Backend API（MVP+ComfyUI）

Base URL: `http://127.0.0.1:8000`

## Provider CRUD
- `GET /providers`
- `POST /providers`
- `PUT /providers/{provider_name}`
- `DELETE /providers/{provider_name}`

## Model CRUD
- `GET /models?provider={provider_name}`
- `POST /models`
- `PUT /models/{model_id}`
- `DELETE /models/{model_id}`

## Workflow CRUD
- `GET /workflows?provider={provider_name}`
- `POST /workflows`
- `PUT /workflows/{workflow_id}`
- `DELETE /workflows/{workflow_id}`

## ComfyUI 接口
- `GET /providers/comfyui/health`
- `GET /providers/comfyui/models`
- `POST /providers/comfyui/jobs`（经 `POST /providers/{provider_name}/jobs`）

提交参数（支持自动回退与重试）：
- `model_key`
- `fallback_provider`
- `fallback_model_key`
- `max_retries`
- `prompt`

## 任务接口
- `GET /provider_jobs`：任务列表（用于前端任务历史展示）
- `GET /provider_jobs/{job_id}/status`
- `GET /provider_jobs/{job_id}/outputs`
- `POST /provider_jobs/{job_id}/retry`

## 状态流转与字段说明
状态：`PENDING` → `RUNNING` → `SUCCEEDED` / `FAILED`；重试中：`RETRYING`

`provider_jobs` 关键字段：
- `retry_count`: 当前累计重试次数
- `max_retries`: 最大重试次数
- `fallback_provider`: 备用 provider
- `fallback_model_key`: 备用模型
- `active_provider`: 本次执行实际 provider
- `active_model_key`: 本次执行实际 model
- `error_message`: 最后失败原因
- `status_history_json`: 状态历史记录（时间、状态、说明）
