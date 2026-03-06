# Backend API（MVP）

Base URL: `http://127.0.0.1:8000`

## 健康检查
- `GET /health`

## Provider / Model / Workflow
- `GET /providers`：从 SQLite 读取 provider，并附加 provider mock health/capabilities。
- `POST /providers`：新增 provider（占位配置管理）。
- `GET /models`：读取 provider_models（JOIN providers）。
- `POST /models`：新增模型记录。
- `GET /workflows`：读取 workflows（JOIN providers）。
- `POST /workflows`：新增 workflow 记录。
- `POST /providers/{provider_name}/jobs`：提交 mock job（真实提交后续接入）。

## 项目与资产
- `GET /projects`
- `POST /projects`
- `GET /assets`
- `POST /assets`

> 注：当前接口为骨架实现；ComfyUI/即梦/可灵真实任务提交、状态追踪与产物拉取仍为后续接入点。
