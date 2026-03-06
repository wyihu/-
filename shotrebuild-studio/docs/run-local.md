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

## 3) 启动桌面端（Tauri）
```bash
cd shotrebuild-studio/apps/desktop
npm run tauri:dev
```

> 若本机缺少 Rust/Tauri 依赖，可先用 `npm run dev` 验证页面与 API 联通。
