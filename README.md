# video-clip-tagger

Video Clip Tagger: **视频素材 → 自动抽帧 → AI识别 → 生成标签 → 重命名视频 → 更新索引**

> 说明：这是一个可运行的 MVP 脚手架，包含后端 FastAPI + CLI + 前端 Next.js/Tailwind。
> 多模型 Provider 已做成统一接口；除 OpenAI 外，其它 Provider 目前是占位实现（你填 API 调用即可）。

## 目录结构

```
video-clip-tagger
├── backend
│   └── backend
│       ├── scanner
│       ├── frame_extractor
│       ├── model_provider
│       ├── tagger
│       ├── renamer
│       ├── indexer
│       └── api
├── frontend
├── config
├── models
├── storage
└── scripts
```

## 依赖

- Python >= 3.10
- ffmpeg (含 ffprobe)
- Node.js 18+（仅前端需要）

## 快速启动（一键）

安装依赖后，直接：

```bash
cd video-clip-tagger
./scripts/install.sh

video-clip-tagger start
# 浏览器会自动打开 http://localhost:3000
```

停止：

```bash
video-clip-tagger stop
```

## 快速开始（后端 API + CLI）

```bash
cd video-clip-tagger

# 安装后端
./scripts/install.sh

# 启动 API
uvicorn backend.api.main:app --reload --port 8000

# CLI：扫描并识别（默认扫描 ~/ai-video-factory/clips 下 *.mp4）
video-clip-tagger scan

# CLI：识别单个视频
video-clip-tagger tag /path/to/video.mp4
```

### 模型切换

编辑 `config/models.yaml`：

- `active_provider: local | openai | google | deepseek | qwen`
- 或 API：`POST /models/switch?provider=openai`

OpenAI 需要设置：

```bash
export OPENAI_API_KEY=... 
```

## API

- `GET /videos` 扫描 clips 目录，返回 mp4 列表
- `POST /analyze` 上传单个 mp4 并分析
- `POST /scan` 扫描 clips 目录并并行分析全部
- `POST /models/switch?provider=...` 切换模型
- `GET /status` 当前状态（模型/队列/错误）

## 前端（Next.js + Tailwind）

```bash
cd video-clip-tagger/frontend
npm i
NEXT_PUBLIC_API_BASE=http://localhost:8000 npm run dev
```

页面：
- Dashboard: `/`
- Library: `/library`（MVP：需要你加一个后端 endpoint 读 index.json 才能展示）
- Tagging: `/tagging`
- Model Settings: `/settings`

## Docker

后端：

```bash
cd video-clip-tagger
docker compose up --build
# http://localhost:8000/docs
```

> volumes 中默认把 `${HOME}/ai-video-factory/clips` 以只读挂载到容器 `/clips`。
> 如需完全对齐 settings.clips_dir，可改 backend/settings.py 或 docker-compose.yml。

## 性能/并行

- `/scan` 使用 asyncio semaphore 做并发（默认 `max_workers=8`，在 `backend/settings.py`）。
- ffmpeg 抽帧很快；真正耗时在模型调用。
- 想达到「1000 视频 < 5 分钟」你需要：
  - 视觉模型足够快（本地/批处理）
  - 更激进的并行（进程池 + 限流）
  - 缓存（同视频/同帧不重复分析）

## TODO（你可以让我继续补全）

- [ ] 补齐 Google/DeepSeek/Qwen 的真实 API 调用
- [ ] 增加 `/library` / `/library/{file}` 等 endpoint（读写 index.json、视频流）
- [ ] Renamer 改成不移动原文件：复制/软链策略
- [ ] 加任务队列（Redis/RQ/Celery）与持久化
- [ ] 前端 Library 做成可播放、可编辑标签并保存
