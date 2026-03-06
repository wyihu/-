from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from fastapi import HTTPException

from backend.db.database import execute, fetch_all
from backend.services.provider_registry import PROVIDERS

JOB_STATUS_PENDING = "PENDING"
JOB_STATUS_RUNNING = "RUNNING"
JOB_STATUS_SUCCEEDED = "SUCCEEDED"
JOB_STATUS_FAILED = "FAILED"
JOB_STATUS_UNKNOWN = "UNKNOWN"


def _now_iso() -> str:
    return datetime.utcnow().isoformat()


def _get_provider_row(provider_name: str) -> dict[str, Any]:
    rows = fetch_all("SELECT id, name FROM providers WHERE name = ?", (provider_name,))
    if not rows:
        raise HTTPException(status_code=404, detail=f"Provider not found: {provider_name}")
    return rows[0]


def create_provider_job(provider_name: str, payload: dict[str, Any], workflow_id: int | None = None) -> dict[str, Any]:
    provider_impl = PROVIDERS.get(provider_name)
    if not provider_impl:
        raise HTTPException(status_code=404, detail="Provider implementation not found")

    provider_row = _get_provider_row(provider_name)

    local_job_id = execute(
        """
        INSERT INTO provider_jobs(provider_id, workflow_id, status, request_json, response_json, outputs_json, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            provider_row["id"],
            workflow_id,
            JOB_STATUS_PENDING,
            json.dumps(payload, ensure_ascii=False),
            "{}",
            "[]",
            _now_iso(),
        ),
    )

    try:
        submit_response = provider_impl.submit_job(payload)
        provider_job_id = submit_response.get("provider_job_id") or str(local_job_id)
        execute(
            """
            UPDATE provider_jobs
            SET provider_job_id = ?, status = ?, response_json = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                provider_job_id,
                JOB_STATUS_PENDING,
                json.dumps(submit_response, ensure_ascii=False),
                _now_iso(),
                local_job_id,
            ),
        )
        return {
            "job_id": local_job_id,
            "provider_job_id": provider_job_id,
            "status": JOB_STATUS_PENDING,
            "provider": provider_name,
        }
    except Exception as exc:  # noqa: BLE001
        execute(
            """
            UPDATE provider_jobs
            SET status = ?, error_message = ?, updated_at = ?
            WHERE id = ?
            """,
            (JOB_STATUS_FAILED, str(exc), _now_iso(), local_job_id),
        )
        raise HTTPException(status_code=502, detail=f"Provider submit failed: {exc}") from exc


def get_provider_job_status(job_id: int) -> dict[str, Any]:
    rows = fetch_all(
        """
        SELECT j.id, j.provider_job_id, j.status, j.response_json, j.error_message, p.name AS provider
        FROM provider_jobs j
        JOIN providers p ON p.id = j.provider_id
        WHERE j.id = ?
        """,
        (job_id,),
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Job not found")

    row = rows[0]
    provider_impl = PROVIDERS.get(row["provider"])
    if not provider_impl:
        return {"job_id": row["id"], "provider": row["provider"], "status": row["status"], "error": row["error_message"]}

    provider_job_id = row["provider_job_id"] or str(job_id)
    try:
        provider_state = provider_impl.get_job_status(provider_job_id)
        mapped = provider_state.get("status", JOB_STATUS_UNKNOWN)
        if mapped == "UNKNOWN" and row["status"] in [JOB_STATUS_PENDING, JOB_STATUS_RUNNING]:
            mapped = JOB_STATUS_RUNNING
        execute(
            "UPDATE provider_jobs SET status = ?, response_json = ?, updated_at = ? WHERE id = ?",
            (mapped, json.dumps(provider_state, ensure_ascii=False), _now_iso(), job_id),
        )
        return {
            "job_id": row["id"],
            "provider": row["provider"],
            "provider_job_id": provider_job_id,
            "status": mapped,
            "raw": provider_state,
        }
    except Exception as exc:  # noqa: BLE001
        execute(
            "UPDATE provider_jobs SET status = ?, error_message = ?, updated_at = ? WHERE id = ?",
            (JOB_STATUS_FAILED, str(exc), _now_iso(), job_id),
        )
        return {
            "job_id": row["id"],
            "provider": row["provider"],
            "provider_job_id": provider_job_id,
            "status": JOB_STATUS_FAILED,
            "error": str(exc),
        }


def fetch_provider_job_outputs(job_id: int) -> dict[str, Any]:
    rows = fetch_all(
        """
        SELECT j.id, j.provider_job_id, j.outputs_json, p.name AS provider
        FROM provider_jobs j
        JOIN providers p ON p.id = j.provider_id
        WHERE j.id = ?
        """,
        (job_id,),
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Job not found")

    row = rows[0]
    provider_impl = PROVIDERS.get(row["provider"])
    if not provider_impl:
        return {"job_id": row["id"], "outputs": []}

    provider_job_id = row["provider_job_id"] or str(job_id)
    try:
        outputs = provider_impl.fetch_outputs(provider_job_id)
        execute(
            "UPDATE provider_jobs SET outputs_json = ?, status = ?, updated_at = ? WHERE id = ?",
            (json.dumps(outputs, ensure_ascii=False), JOB_STATUS_SUCCEEDED, _now_iso(), job_id),
        )
        return {"job_id": row["id"], "provider_job_id": provider_job_id, "status": JOB_STATUS_SUCCEEDED, "outputs": outputs}
    except Exception as exc:  # noqa: BLE001
        execute(
            "UPDATE provider_jobs SET status = ?, error_message = ?, updated_at = ? WHERE id = ?",
            (JOB_STATUS_FAILED, str(exc), _now_iso(), job_id),
        )
        raise HTTPException(status_code=502, detail=f"Fetch outputs failed: {exc}") from exc
