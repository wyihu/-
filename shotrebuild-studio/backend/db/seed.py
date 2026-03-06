from backend.db.database import execute, fetch_all


def _exists(table: str) -> bool:
    row = fetch_all(f"SELECT COUNT(1) AS cnt FROM {table}")
    return bool(row and row[0]["cnt"] > 0)


def seed_initial_data() -> None:
    if not _exists("providers"):
        execute(
            "INSERT INTO providers(name, provider_type, enabled, config_json) VALUES (?, ?, ?, ?)",
            ("comfyui", "comfyui", 1, "{}"),
        )
        execute(
            "INSERT INTO providers(name, provider_type, enabled, config_json) VALUES (?, ?, ?, ?)",
            ("jimeng", "jimeng", 1, "{}"),
        )
        execute(
            "INSERT INTO providers(name, provider_type, enabled, config_json) VALUES (?, ?, ?, ?)",
            ("kling", "kling", 1, "{}"),
        )

    provider_rows = fetch_all("SELECT id, name FROM providers")
    provider_id_map = {row["name"]: row["id"] for row in provider_rows}

    if not _exists("provider_models"):
        execute(
            "INSERT INTO provider_models(provider_id, model_key, display_name, capabilities, is_default) VALUES (?, ?, ?, ?, ?)",
            (provider_id_map.get("comfyui"), "comfyui/mock-sd", "ComfyUI Mock SD", '["text_to_image"]', 1),
        )
        execute(
            "INSERT INTO provider_models(provider_id, model_key, display_name, capabilities, is_default) VALUES (?, ?, ?, ?, ?)",
            (provider_id_map.get("jimeng"), "jimeng/mock-v1", "Jimeng Mock V1", '["text_to_video"]', 1),
        )
        execute(
            "INSERT INTO provider_models(provider_id, model_key, display_name, capabilities, is_default) VALUES (?, ?, ?, ?, ?)",
            (provider_id_map.get("kling"), "kling/mock-1.6", "Kling Mock 1.6", '["image_to_video"]', 1),
        )

    if not _exists("workflows"):
        execute(
            "INSERT INTO workflows(provider_id, workflow_key, name, definition_json) VALUES (?, ?, ?, ?)",
            (provider_id_map.get("comfyui"), "comfyui-basic-mock", "ComfyUI Basic (Mock)", "{}"),
        )
        execute(
            "INSERT INTO workflows(provider_id, workflow_key, name, definition_json) VALUES (?, ?, ?, ?)",
            (provider_id_map.get("jimeng"), "jimeng-basic-mock", "即梦 Basic (Mock)", "{}"),
        )
        execute(
            "INSERT INTO workflows(provider_id, workflow_key, name, definition_json) VALUES (?, ?, ?, ?)",
            (provider_id_map.get("kling"), "kling-basic-mock", "可灵 Basic (Mock)", "{}"),
        )
