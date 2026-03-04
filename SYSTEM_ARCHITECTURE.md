System Architecture

Project: Video Clip Tagger

Purpose:
Video Clip Tagger is the asset management engine for the AI Video Factory system.

Core Workflow
Video Input
↓
Frame Extraction
↓
AI Vision Recognition
↓
Tag Generation
↓
File Rename
↓
Library Storage
↓
Index Update

System Layers

1 Ingest Layer
Responsible for detecting and scanning incoming videos.
Module: scanner

2 Processing Layer
Responsible for video analysis.
Modules:
- frame_extractor
- model_provider
- tagger

3 Storage Layer
Responsible for asset organization.
Modules:
- renamer
- indexer
Files:
- storage/library/index.json

4 API Layer
Responsible for system control.
FastAPI endpoints:
- /scan
- /analyze
- /videos
- /models/switch
- /health

5 UI Layer
Frontend built with:
React Next.js
Pages:
- Dashboard
- Library
- Tagging
- Settings

Directory Structure

video-clip-tagger
  backend
  frontend
  config
  scripts
  storage
  frames

Future Modules
watcher
embedding_search
duplicate_detection
quality_filter
auto_edit

System Role
Video Clip Tagger is designed as the first module of the AI Video Factory pipeline.

Future pipeline:
Asset Library
↓
Script Generation
↓
Shot Planning
↓
Video Generation
↓
Auto Editing
