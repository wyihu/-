AGENTS

This repository contains the project Video Clip Tagger.
Video Clip Tagger is an AI-powered video asset organization system.

Main pipeline:
Video → Frame Extraction → AI Vision Recognition → Tag Generation → Rename → Library Index

The system converts raw video clips into a structured asset library.

Key modules:
- backend/scanner
- backend/frame_extractor
- backend/model_provider
- backend/tagger
- backend/renamer
- backend/indexer
- backend/api

The default vision model provider is Ollama using the LLaVA model.

All model providers must implement:
- analyze_image(image_path)

Expected output format:
{ "scene": "", "action": "", "object": "" }

Development rules:
1. Keep modules independent.
2. Do not mix AI logic with storage logic.
3. Avoid hardcoded paths.
4. Maintain pipeline structure.
