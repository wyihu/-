Codex Context

This repository implements an AI-powered video asset organization system.

The system processes raw video clips and converts them into structured assets.

Main processing flow:
video
↓
frame extraction
↓
AI recognition
↓
tag generation
↓
rename
↓
library index

Backend stack:
Python FastAPI

Frontend stack:
React Next.js

AI model:
Ollama + LLaVA

Expected AI output:
{ "scene": "", "action": "", "object": "" }

Processed videos are renamed using:
action_id.mp4

Example:
pour_001.mp4

All metadata is stored in:
storage/library/index.json

This project is part of a larger AI Video Factory system.
