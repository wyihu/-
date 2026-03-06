# 本地运行

## 1) 启动后端
```bash
cd shotrebuild-studio
python -m venv .venv
source .venv/bin/activate
pip install -e ./backend
export COMFYUI_BASE_URL=http://127.0.0.1:8188
PYTHONPATH=. python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8000 --reload
```

## 2) 启动前端（Web 开发模式）
```bash
cd shotrebuild-studio/apps/desktop
cp .env.example .env
npm install
npm run dev
```

### npm 403 / 网络受限排查
若 `npm install` 报 `403 Forbidden`：

1. 检查 registry 与代理：
```bash
npm config get registry
npm config get proxy
npm config get https-proxy
```

2. 企业代理场景（建议由网络管理员统一配置白名单）：
- 放行 `https://registry.npmjs.org`（或企业镜像源）；
- 放行 `@types/*`, `react*`, `vite*`, `typescript*`, `@vitejs/*` 等依赖命名空间。

3. 直连场景（若代理导致 403，可临时关闭代理验证网络）：
```bash
env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u npm_config_http_proxy -u npm_config_https_proxy npm install --verbose
```
若出现 `ENETUNREACH`，说明当前网络无法直连 npm，需要切回可用代理或更换网络。

4. 可联网机器预装方案：
- 在可联网环境执行 `npm install`；
- 将 `node_modules` 与 lockfile 带回内网环境运行（短期方案）。

## 3) 验证任务状态展示（前端）
1. 打开 `Workflow 管理页`。
2. 提交 ComfyUI 任务（可配置 fallback provider / model / max_retries）。
3. 观察：
   - 任务状态每 2 秒轮询更新；
   - 失败时显示失败原因；
   - 可点击“重试任务”；
   - “任务状态历史”和“任务列表”显示重试与回退记录。

## 4) 启动桌面端（Tauri）
```bash
cd shotrebuild-studio/apps/desktop
npm run tauri:dev
```

> `tauri:dev` 使用 `cargo tauri dev`，需本机已安装 Rust/Tauri CLI。
