# ShotRebuild Studio 架构（本批次）

## 模块边界
- `apps/desktop`: Tauri + React + TypeScript UI 层，仅负责页面和 API 调用。
- `backend/api`: FastAPI 路由层。
- `backend/services`: 业务编排层（本批次为 provider 注册 + SQLite 配置占位管理）。
- `backend/providers`: Provider 抽象和实现层。
- `backend/db`: SQLite 连接与 schema 初始化。
- `workflows/comfyui`: 未来真实工作流定义接入位。

## 关键设计原则
1. Provider 与 Model 分离：provider 提供能力与运行环境，model 是 provider 下可选模型。
2. AI 逻辑不与存储逻辑混合：Provider 抽象在 `providers/`，SQLite 在 `db/`。
3. 旧版流水线模块保留价值：后续通过服务层逐步桥接。

## 旧实现接入说明
- 旧版代码目录：仓库根 `backend/backend/*`。
- 后续接入点：
  - `backend/services/` 可新增适配器，调用旧版 frame_extractor/tagger 等能力。
  - `backend/api/` 逐步新增素材工厂操作接口并映射到旧模块。


## ComfyUI 接入说明
- `backend/providers/comfyui/provider.py` 已接入 ComfyUI HTTP API（health/models/submit/status/outputs）。
- `backend/services/provider_jobs.py` 负责任务状态流转与 provider_jobs 落库。
