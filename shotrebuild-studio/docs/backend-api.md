# Backend API（MVP）

Base URL: `http://127.0.0.1:8000`

## 健康检查
- `GET /health`

## Provider / Model / Workflow
- `GET /providers`：返回 provider 列表（mock health + capabilities）。
- `GET /models`：返回 provider 下模型列表（mock）。
- `GET /workflows`：返回 workflow 占位列表（mock）。
- `POST /providers/{provider_name}/jobs`：提交 mock job。

## 项目与资产
- `GET /projects`
- `POST /projects`
- `GET /assets`
- `POST /assets`

> 注：当前接口为骨架实现，真实任务提交、状态追踪与产物拉取将于后续批次接入。
