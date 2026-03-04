Video Clip Tagger

Video Clip Tagger is a system designed to automatically organize video assets.

Purpose:
Convert raw video files into a structured and searchable asset library.

Pipeline:
Video file
↓
Frame extraction
↓
AI vision recognition
↓
Semantic tag generation
↓
File rename
↓
Library indexing

Storage structure:
~/ai-video-factory
  clips
  processing
  failed
storage/library

Index file:
storage/library/index.json

Example entry:
{ "file": "pour_001.mp4", "scene": "desk", "action": "pour", "object": "cup" }

The system is intended to become the asset management layer of an AI Video Factory.
