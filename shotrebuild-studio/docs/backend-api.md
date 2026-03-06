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
- `POST /providers/comfyui/jobs`（通过 `POST /providers/{provider_name}/jobs`）

任务提交请求体示例：
```json
{
  "workflow_id": 1,
  "model_key": "sd_xxx.safetensors",
  "fallback_provider": "kling",
  "fallback_model_key": "kling/mock-1.6",
  "max_retries": 2,
  "prompt": {
    "prompt": {}
  }
}
```

## 任务状态/输出/重试
- `GET /provider_jobs/{job_id}/status`
- `GET /provider_jobs/{job_id}/outputs`
- `POST /provider_jobs/{job_id}/retry`

状态流转：`PENDING` → `RUNNING` → `SUCCEEDED` / `FAILED`；失败中间态含 `RETRYING`。

`provider_jobs` 记录字段包含：`retry_count`、`max_retries`、`fallback_provider`、`fallback_model_key`、`error_message`。
