# Backend API（MVP+ComfyUI接入）

Base URL: `http://127.0.0.1:8000`

## 健康检查
- `GET /health`

## Provider / Model / Workflow
- `GET /providers`：读取 provider 并附加 provider health/capabilities。
- `POST /providers`：新增 provider 占位配置。
- `GET /models?provider={provider_name}`：按 provider 读取模型（不传 provider 返回全部）。
- `POST /models`：新增模型记录。
- `GET /workflows?provider={provider_name}`：按 provider 读取工作流（不传 provider 返回全部）。
- `POST /workflows`：新增工作流记录。

## ComfyUI 直连接口
- `GET /providers/comfyui/health`
  - 后端转发 ComfyUI `/system_stats` 健康检查。
- `GET /providers/comfyui/models`
  - 后端优先通过 ComfyUI `/object_info` 解析 checkpoint 列表，失败时回退 `/models`。
- `POST /providers/comfyui/jobs`
  - 请求体：
    ```json
    {
      "workflow_id": 1,
      "model_key": "sd_xxx.safetensors",
      "prompt": {
        "prompt": {
          "1": { "inputs": {}, "class_type": "CheckpointLoaderSimple" }
        }
      }
    }
    ```
  - 后端会落库到 `provider_jobs`，并调用 ComfyUI `/prompt` 提交任务。

## 任务状态与产物
- `GET /provider_jobs/{job_id}/status`
  - 返回任务当前状态，状态流转包含：`PENDING`、`RUNNING`、`SUCCEEDED`、`FAILED`。
- `GET /provider_jobs/{job_id}/outputs`
  - 获取任务输出并更新本地任务状态。

## 项目与资产
- `GET /projects`
- `POST /projects`
- `GET /assets`
- `POST /assets`

> 说明：即梦/可灵仍为占位 provider；当前真实接入仅 ComfyUI。
