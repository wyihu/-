# Backend-only container (frontend optional; see README)
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# copy backend + config + storage scaffolding
COPY backend/ /app/backend/
COPY config/ /app/config/
COPY storage/ /app/storage/

RUN python -m pip install --no-cache-dir -e /app/backend

EXPOSE 8000

CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
