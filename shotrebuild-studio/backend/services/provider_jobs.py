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
JOB_STATUS_RETRYING = "RETRYING"


def _now_iso() -> str:
    return datetime.utcnow().isoformat()


def _get_provider_row(provider_name: str) -> dict[str, Any]:
    rows = fetch_all("SELECT id, name FROM providers WHERE name = ?", (provider_name,))
    if not rows:
        raise HTTPException(status_code=404, detail=f"Provider not found: {provider_name}")
    return rows[0]


def _append_history(job_id: int, status: str, message: str) -> None:
    rows = fetch_all("SELECT status_history_json FROM provider_jobs WHERE id = ?", (job_id,))
    if not rows:
        return
    history = json.loads(rows[0].get("status_history_json") or "[]")
    history.append({"at": _now_iso(), "status": status, "message": message})
    execute("UPDATE provider_jobs SET status_history_json = ?, updated_at = ? WHERE id = ?", (json.dumps(history, ensure_ascii=False), _now_iso(), job_id))


def _attempt_submit(provider_name: str, payload: dict[str, Any]) -> dict[str, Any]:
    impl = PROVIDERS.get(provider_name)
    if not impl:
        raise RuntimeError(f"Provider implementation not found: {provider_name}")
    result = impl.submit_job(payload)
    return {"provider_job_id": result.get("provider_job_id"), "raw": result}


def create_provider_job(
    provider_name: str,
    payload: dict[str, Any],
    workflow_id: int | None = None,
    model_key: str | None = None,
    fallback_provider: str | None = None,
    fallback_model_key: str | None = None,
    max_retries: int = 0,
) -> dict[str, Any]:
    provider_row = _get_provider_row(provider_name)

    local_job_id = execute(
        """
        INSERT INTO provider_jobs(
            provider_id, workflow_id, status, request_json, response_json, outputs_json,
            retry_count, max_retries, fallback_provider, fallback_model_key,
            active_provider, active_model_key, status_history_json, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            provider_row["id"],
            workflow_id,
            JOB_STATUS_PENDING,
            json.dumps(payload, ensure_ascii=False),
            "{}",
            "[]",
            0,
            max_retries,
            fallback_provider or "",
            fallback_model_key or "",
            provider_name,
            model_key or "",
            "[]",
            _now_iso(),
        ),
    )
    _append_history(local_job_id, JOB_STATUS_PENDING, f"Job created with provider={provider_name}, model={model_key or ''}")

    attempts: list[tuple[str, str | None]] = [(provider_name, model_key)]
    if fallback_provider and fallback_provider != provider_name:
        attempts.append((fallback_provider, fallback_model_key))

    total_tries = max(1, max_retries + 1)
    last_error = ""
    retry_count = 0

    for provider_try, model_try in attempts:
        for _ in range(total_tries):
            payload_with_model = {**payload}
            if model_try:
                payload_with_model["model_key"] = model_try
            try:
                submitted = _attempt_submit(provider_try, payload_with_model)
                provider_job_id = submitted.get("provider_job_id") or str(local_job_id)
                execute(
                    """
                    UPDATE provider_jobs
                    SET provider_job_id = ?, status = ?, response_json = ?, retry_count = ?,
                        active_provider = ?, active_model_key = ?, error_message = '', updated_at = ?
                    WHERE id = ?
                    """,
                    (
                        provider_job_id,
                        JOB_STATUS_PENDING,
                        json.dumps(submitted["raw"], ensure_ascii=False),
                        retry_count,
                        provider_try,
                        model_try or "",
                        _now_iso(),
                        local_job_id,
                    ),
                )
                _append_history(local_job_id, JOB_STATUS_PENDING, f"Submitted to provider={provider_try}, model={model_try or ''}")
                return {
                    "job_id": local_job_id,
                    "provider_job_id": provider_job_id,
                    "status": JOB_STATUS_PENDING,
                    "provider": provider_try,
                    "retry_count": retry_count,
                }
            except Exception as exc:  # noqa: BLE001
                retry_count += 1
                last_error = str(exc)
                execute(
                    """
                    UPDATE provider_jobs
                    SET status = ?, error_message = ?, retry_count = ?,
                        active_provider = ?, active_model_key = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (JOB_STATUS_RETRYING, last_error, retry_count, provider_try, model_try or "", _now_iso(), local_job_id),
                )
                _append_history(local_job_id, JOB_STATUS_RETRYING, f"Attempt failed on provider={provider_try}, reason={last_error}")

    execute("UPDATE provider_jobs SET status = ?, error_message = ?, updated_at = ? WHERE id = ?", (JOB_STATUS_FAILED, f"Retries exhausted: {last_error}", _now_iso(), local_job_id))
    _append_history(local_job_id, JOB_STATUS_FAILED, f"Retries exhausted: {last_error}")
    raise HTTPException(status_code=502, detail=f"Provider submit failed after retries: {last_error}")


def retry_provider_job(job_id: int, max_retries_override: int | None = None) -> dict[str, Any]:
    rows = fetch_all(
        """
        SELECT j.id, j.workflow_id, j.request_json, j.max_retries, j.fallback_provider, j.fallback_model_key,
               j.active_provider, j.active_model_key, p.name AS provider
        FROM provider_jobs j
        JOIN providers p ON p.id = j.provider_id
        WHERE j.id = ?
        """,
        (job_id,),
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Job not found")

    row = rows[0]
    payload = json.loads(row["request_json"] or "{}")
    return create_provider_job(
        provider_name=row["provider"],
        payload=payload,
        workflow_id=row["workflow_id"],
        model_key=row["active_model_key"] or None,
        fallback_provider=row["fallback_provider"] or None,
        fallback_model_key=row["fallback_model_key"] or None,
        max_retries=max_retries_override if max_retries_override is not None else int(row["max_retries"] or 0),
    )


def list_provider_jobs() -> list[dict[str, Any]]:
    return fetch_all(
        """
        SELECT j.id, j.status, j.retry_count, j.max_retries, j.error_message,
               j.active_provider, j.active_model_key, j.created_at, j.updated_at
        FROM provider_jobs j
        ORDER BY j.id DESC
        """
    )


def get_provider_job_status(job_id: int) -> dict[str, Any]:
    rows = fetch_all(
        """
        SELECT j.id, j.provider_job_id, j.status, j.response_json, j.error_message,
               j.retry_count, j.max_retries, j.active_provider, j.active_model_key,
               j.status_history_json, p.name AS provider
        FROM provider_jobs j
        JOIN providers p ON p.id = j.provider_id
        WHERE j.id = ?
        """,
        (job_id,),
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Job not found")

    row = rows[0]
    target_provider = row["active_provider"] or row["provider"]
    provider_impl = PROVIDERS.get(target_provider)
    if not provider_impl:
        return {
            "job_id": row["id"],
            "provider": target_provider,
            "status": row["status"],
            "error": row["error_message"],
            "retry_count": row["retry_count"],
            "history": json.loads(row.get("status_history_json") or "[]"),
        }

    provider_job_id = row["provider_job_id"] or str(job_id)
    try:
        provider_state = provider_impl.get_job_status(provider_job_id)
        mapped = provider_state.get("status", row["status"])
        if mapped not in [JOB_STATUS_PENDING, JOB_STATUS_RUNNING, JOB_STATUS_SUCCEEDED, JOB_STATUS_FAILED]:
            mapped = row["status"]
        execute("UPDATE provider_jobs SET status = ?, response_json = ?, updated_at = ? WHERE id = ?", (mapped, json.dumps(provider_state, ensure_ascii=False), _now_iso(), job_id))
        _append_history(job_id, mapped, f"Polled provider status from {target_provider}")
        latest = fetch_all("SELECT status_history_json FROM provider_jobs WHERE id = ?", (job_id,))[0]
        return {
            "job_id": row["id"],
            "provider": target_provider,
            "provider_job_id": provider_job_id,
            "status": mapped,
            "retry_count": row["retry_count"],
            "max_retries": row["max_retries"],
            "error": row["error_message"],
            "history": json.loads(latest.get("status_history_json") or "[]"),
            "raw": provider_state,
        }
    except Exception as exc:  # noqa: BLE001
        execute("UPDATE provider_jobs SET status = ?, error_message = ?, updated_at = ? WHERE id = ?", (JOB_STATUS_FAILED, str(exc), _now_iso(), job_id))
        _append_history(job_id, JOB_STATUS_FAILED, f"Status polling failed: {exc}")
        latest = fetch_all("SELECT status_history_json FROM provider_jobs WHERE id = ?", (job_id,))[0]
        return {
            "job_id": row["id"],
            "provider": target_provider,
            "provider_job_id": provider_job_id,
            "status": JOB_STATUS_FAILED,
            "retry_count": row["retry_count"],
            "max_retries": row["max_retries"],
            "error": str(exc),
            "history": json.loads(latest.get("status_history_json") or "[]"),
        }


def fetch_provider_job_outputs(job_id: int) -> dict[str, Any]:
    rows = fetch_all(
        """
        SELECT j.id, j.provider_job_id, j.outputs_json, j.active_provider, p.name AS provider
        FROM provider_jobs j
        JOIN providers p ON p.id = j.provider_id
        WHERE j.id = ?
        """,
        (job_id,),
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Job not found")

    row = rows[0]
    target_provider = row["active_provider"] or row["provider"]
    provider_impl = PROVIDERS.get(target_provider)
    if not provider_impl:
        return {"job_id": row["id"], "outputs": []}

    provider_job_id = row["provider_job_id"] or str(job_id)
    try:
        outputs = provider_impl.fetch_outputs(provider_job_id)
        execute("UPDATE provider_jobs SET outputs_json = ?, status = ?, updated_at = ? WHERE id = ?", (json.dumps(outputs, ensure_ascii=False), JOB_STATUS_SUCCEEDED, _now_iso(), job_id))
        _append_history(job_id, JOB_STATUS_SUCCEEDED, "Outputs fetched successfully")
        return {"job_id": row["id"], "provider_job_id": provider_job_id, "status": JOB_STATUS_SUCCEEDED, "outputs": outputs}
    except Exception as exc:  # noqa: BLE001
        execute("UPDATE provider_jobs SET status = ?, error_message = ?, updated_at = ? WHERE id = ?", (JOB_STATUS_FAILED, str(exc), _now_iso(), job_id))
        _append_history(job_id, JOB_STATUS_FAILED, f"Fetch outputs failed: {exc}")
        raise HTTPException(status_code=502, detail=f"Fetch outputs failed: {exc}") from exc
