# video-clip-tagger — 会话重置后继续用的交接文档（wyh-2 / macOS）

> 目的：你 reset 会话后，把本文件内容粘贴给助手，助手就能在同一台远端机器（wyh-2）继续改/升级软件。

## 0. 一句话定位
这是一个“视频素材工厂”：自动抽帧→多模型识别→打标签→重命名→入库索引；并提供 CLI / API / Web UI / Desktop(Electron)。

## 1. 远端位置（关键路径）
- 代码仓库（远端）：`/Users/ye/projects/video-clip-tagger`
- Desktop App（已安装）：`/Applications/Video Clip Tagger.app`
- DMG 构建产物：`~/projects/video-clip-tagger/desktop/dist/Video Clip Tagger-1.0.0-arm64.dmg`
- 数据目录（约定）：`~/ai-video-factory/{clips,processing,failed}`
- 库索引：`backend/storage/library/index.json`
- Electron 运行日志（我们新增）：`~/ai-video-factory/logs/desktop-electron.log`

## 2. 模块/分层（不要混写职责）
后端 Python：`backend/backend/*`
- `scanner/`：扫描 clips / processing
- `frame_extractor/`：ffmpeg 抽帧
- `model_provider/`：模型提供方（可插拔）
- `tagger/`：调用 provider 产出标签结构
- `renamer/`：按 action_id 规则重命名
- `indexer/`：写入 `storage/library/index.json`
- `embedding/`：CLIP embedding + FAISS 语义检索
- `watcher/`：watchdog 自动 ingest pipeline
- `api/main.py`：FastAPI
- `cli.py`：Typer CLI（命令名：`video-clip-tagger`）

Provider 统一接口（关键约束）：
- `analyze_image(image_path) -> {"scene":"", "action":"", "object":""}`

前端 Next.js：`frontend/`（Dashboard/Library/Tagging/Settings）

桌面 Electron：`desktop/`
- `main.js`：启动 Ollama/后端/前端、打开窗口
- `runtime_bins.js`：解决 packaged app PATH 干净导致找不到 python/npm 的问题
- `renderer/index.html`：内嵌 Web UI + 顶部状态栏

## 3. 关键端口
- 后端：`127.0.0.1:8000`（`/health`, `/docs`）
- 前端：`127.0.0.1:3000`
- Ollama：`127.0.0.1:11434`

## 4. 常用命令（远端执行）
在 repo 根目录：`cd ~/projects/video-clip-tagger`

启动/停止（脚本）：
- `./scripts/start.sh`
- `./scripts/stop.sh`

CLI：
- `video-clip-tagger doctor`
- `video-clip-tagger watch --scan-existing`
- `video-clip-tagger search "xxx"`

桌面构建：
- `cd desktop && npm run build`  → 生成 DMG

安装 DMG 到 Applications（手动/脚本都行）：
- 挂载 dmg → 拷贝 `.app` 到 `/Applications`

## 5. 当前状态（截至本交接文档生成时）
- Electron App 已修复：
  - 解决 `spawn python3 ENOENT`
  - 解决 `Cannot find module ./runtime_bins`
  - Electron 会写运行日志到：`~/ai-video-factory/logs/desktop-electron.log`
  - App 启动后应能拉起 8000/3000 监听
- 仍未做：代码签名/公证；图标仍为占位符

## 6. 已知坑（别再踩）
- 远端 `uvicorn` 不在 PATH：用 `python3 -m uvicorn ...`
- 前端 `node_modules` 可能损坏：必要时删掉重装 `npm install`
- electron/npm 下载可能抽风：需要时设置代理环境变量（之前用过 `ELECTRON_GET_USE_PROXY=1` + `HTTP_PROXY/HTTPS_PROXY/ALL_PROXY`）
- Gatekeeper：未签名 DMG/.app 可能需要“右键打开/隐私与安全性允许”

## 7. 文件结构快照（精简 tree；排除 node_modules/.next/dist 等）
（见仓库根目录 tree，必要时可重新生成）

## 8. reset 后你要粘贴给助手的内容
把这份 HANDOFF.md 全部粘贴过去即可。
