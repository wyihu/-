"use client";

import { useState } from "react";

export default function TaggingPage() {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const base = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

  async function submit() {
    if (!file) return;
    setLoading(true);
    setResult(null);
    const fd = new FormData();
    fd.append("file", file);
    const res = await fetch(`${base}/analyze`, { method: "POST", body: fd });
    const json = await res.json();
    setResult(json);
    setLoading(false);
  }

  return (
    <main className="grid gap-4">
      <div className="card p-5">
        <div className="text-lg font-semibold">Tagging</div>
        <div className="text-sm text-gray-700 mt-1">Upload a video and run recognition.</div>

        <div className="mt-4 flex items-center gap-3">
          <input
            type="file"
            accept="video/mp4"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
          />
          <button className="btn btn-primary" onClick={submit} disabled={!file || loading}>
            {loading ? "Analyzing…" : "Analyze"}
          </button>
        </div>
      </div>

      <div className="card p-5">
        <div className="text-sm font-medium mb-2">Result</div>
        <pre className="text-xs bg-gray-50 border border-gray-200 rounded-lg p-3 overflow-auto">
          {result ? JSON.stringify(result, null, 2) : "(no result)"}
        </pre>
      </div>
    </main>
  );
}
