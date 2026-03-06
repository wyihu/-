# 重构计划（本批次）

## 现状分析
- 现有仓库包含旧版 `backend/backend/*` 流水线模块（scanner/frame_extractor/tagger/renamer/indexer）。
- 现有桌面端目录主要为历史 Electron/前端实现，不符合本批次 Tauri + React + TypeScript 冻结栈。

## 本批次重构策略
1. 新建 `shotrebuild-studio/` 作为新版工程根，并按目标目录骨架搭建。
2. 在 `backend/` 下实现 FastAPI 最小可运行服务、SQLite schema 初始化、Provider 抽象与三个 provider 占位实现。
3. 在 `apps/desktop/` 下实现 Tauri + React + TypeScript 页面壳、路由与后端健康检查联通。
4. 保留旧实现，不删除；通过文档标注后续接入点。

## 范围控制
- 仅实现素材工厂基础框架与最小数据读写。
- 所有 provider/comfyui/jimeng/kling 均为 mock 占位，不提交真实任务。
- 不实现成片工厂、不实现自动化网页流程、不实现真实 ComfyUI 调用。
