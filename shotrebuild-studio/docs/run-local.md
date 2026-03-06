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

若公司网络对 npm registry 有 403 限制：
1. 联系网络管理员放行 `registry.npmjs.org`（或企业白名单镜像）；
2. 或在可访问 npm 的网络环境执行 `npm install` 后打包 `node_modules` 供内网使用。

## 3) 启动桌面端（Tauri）
```bash
cd shotrebuild-studio/apps/desktop
npm run tauri:dev
```

> `tauri:dev` 当前使用 `cargo tauri dev`，需本机已安装 Rust/Tauri CLI。
