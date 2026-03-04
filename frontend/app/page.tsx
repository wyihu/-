"use client";

import { useEffect, useState } from "react";

function Dot({ ok }: { ok: boolean }) {
  return (
    <span
      className={`inline-block w-2.5 h-2.5 rounded-full ${ok ? "bg-green-600" : "bg-red-600"}`}
      aria-label={ok ? "ok" : "bad"}
    />
  );
}

export default function DashboardPage() {
  const base = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";
  const [status, setStatus] = useState<any>(null);
  const [health, setHealth] = useState<any>(null);

  async function refresh() {
    const s = await fetch(`${base}/status`, { cache: "no-store" }).then((r) => r.json());
    setStatus(s);
    const h = await fetch(`${base}/health`, { cache: "no-store" }).then((r) => r.json());
    setHealth(h);
  }

  useEffect(() => {
    refresh();
    const t = setInterval(refresh, 10_000);
    return () => clearInterval(t);
  }, []);

  const oll = health?.details?.ollama;
  const ollRunning = oll?.status === "running";
  const modelOk = ollRunning && oll?.model !== "missing";

  return (
    <main className="grid gap-4">
      <div className="card p-5">
        <div className="text-lg font-semibold mb-2">Dashboard</div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <div className="label">Clips dir</div>
            <div className="font-mono text-sm break-all">{status?.clips_dir ?? "(loading)"}</div>
          </div>
          <div>
            <div className="label">Current model</div>
            <div className="text-sm">{status?.active_provider ?? "(loading)"}</div>
          </div>
          <div>
            <div className="label">Queue</div>
            <div className="text-sm">
              running: {status?.running ?? "-"} · done: {status?.done ?? "-"}
            </div>
          </div>
        </div>
      </div>

      <div className="card p-5">
        <div className="text-lg font-semibold mb-2">System Status</div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
          <div className="flex items-center gap-2">
            <Dot ok={ollRunning} />
            <div>
              <div className="font-medium">Ollama</div>
              <div className="text-gray-600">{ollRunning ? "running" : "offline"}</div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Dot ok={modelOk} />
            <div>
              <div className="font-medium">Model</div>
              <div className="text-gray-600">
                {modelOk ? (oll?.models?.includes("llava:13b") ? "llava:13b" : "ok") : "missing"}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Dot ok={health?.ffmpeg === "ok"} />
            <div>
              <div className="font-medium">ffmpeg</div>
              <div className="text-gray-600">{health?.ffmpeg ?? "(loading)"}</div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Dot ok={health?.storage === "ok"} />
            <div>
              <div className="font-medium">storage</div>
              <div className="text-gray-600">{health?.storage ?? "(loading)"}</div>
            </div>
          </div>
        </div>

        {health?.clips !== "ok" ? (
          <div className="mt-3 text-sm text-red-700">clips dir missing: {status?.clips_dir}</div>
        ) : null}
        {oll?.status === "offline" ? (
          <div className="mt-3 text-sm text-red-700">Hint: run <code>ollama serve</code></div>
        ) : null}
        {oll?.model === "missing" ? (
          <div className="mt-3 text-sm text-red-700">Hint: run <code>ollama pull llava:13b</code></div>
        ) : null}
      </div>

      <div className="card p-5">
        <div className="text-lg font-semibold mb-2">Ingest Pipeline</div>
        {status?.ingest ? (
          <>
            <div className="text-sm text-gray-700">
              running: {String(status.ingest.running)} · failed: {status.ingest.failed_count}
            </div>
            <div className="mt-2 text-sm">
              <span className="label">Current</span>
              <div className="font-mono text-xs break-all mt-1">{status.ingest.current ?? "(idle)"}</div>
            </div>
            <div className="mt-3 text-sm">
              <span className="label">Queue</span>
              <pre className="text-xs mt-1 bg-gray-50 border border-gray-200 rounded-lg p-3 overflow-auto max-h-48">
                {JSON.stringify(status.ingest.queue ?? [], null, 2)}
              </pre>
            </div>
            {status.ingest.last_error ? (
              <div className="mt-3 text-sm text-red-700">Last ingest error: {status.ingest.last_error}</div>
            ) : null}
          </>
        ) : (
          <div className="text-sm text-gray-600">Watcher not started. Call POST /watch/start or run CLI: video-clip-tagger watch</div>
        )}
      </div>

      <div className="card p-5">
        <div className="text-lg font-semibold mb-2">Task Queue</div>
        <div className="text-sm text-gray-700">{(status?.queue || []).length} queued</div>
        <pre className="text-xs mt-2 bg-gray-50 border border-gray-200 rounded-lg p-3 overflow-auto max-h-64">
          {JSON.stringify(status?.queue ?? [], null, 2)}
        </pre>
        {status?.last_error ? (
          <div className="mt-3 text-sm text-red-700">Last error: {status.last_error}</div>
        ) : null}
      </div>
    </main>
  );
}
