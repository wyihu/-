"use client";

import { useEffect, useState } from "react";

type Status = {
  active_provider: string;
};

export default function SettingsPage() {
  const base = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";
  const [status, setStatus] = useState<Status | null>(null);
  const [provider, setProvider] = useState("local");
  const [msg, setMsg] = useState<string | null>(null);

  async function load() {
    const res = await fetch(`${base}/status`, { cache: "no-store" });
    const json = await res.json();
    setStatus(json);
    setProvider(json.active_provider);
  }

  useEffect(() => {
    load();
  }, []);

  async function save() {
    setMsg(null);
    const res = await fetch(`${base}/models/switch?provider=${provider}`, { method: "POST" });
    if (!res.ok) {
      setMsg(`Failed: ${res.status}`);
      return;
    }
    const json = await res.json();
    setMsg(`Switched to ${json.active_provider}`);
    await load();
  }

  return (
    <main className="grid gap-4">
      <div className="card p-5">
        <div className="text-lg font-semibold">Model Settings</div>
        <div className="text-sm text-gray-700 mt-1">Switch provider (also editable in config/models.yaml).</div>

        <div className="mt-4 flex items-center gap-3">
          <select className="btn" value={provider} onChange={(e) => setProvider(e.target.value)}>
            <option value="local">Local</option>
            <option value="openai">OpenAI</option>
            <option value="google">Google</option>
            <option value="deepseek">DeepSeek</option>
            <option value="qwen">Qwen</option>
          </select>
          <button className="btn btn-primary" onClick={save}>Save</button>
          <button className="btn" onClick={load}>Refresh</button>
        </div>
        <div className="mt-3 text-sm text-gray-600">
          Current: <span className="font-mono">{status?.active_provider ?? "(loading)"}</span>
        </div>
        {msg ? <div className="mt-2 text-sm">{msg}</div> : null}
      </div>
    </main>
  );
}
