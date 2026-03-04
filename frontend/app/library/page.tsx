"use client";

import { useState } from "react";

type Hit = { file: string; score: number };

export default function LibraryPage() {
  const base = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";
  const [query, setQuery] = useState("");
  const [hits, setHits] = useState<Hit[]>([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  async function runSearch() {
    setErr(null);
    setLoading(true);
    setHits([]);
    try {
      const res = await fetch(`${base}/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, top_k: 10 }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();
      setHits(json);
    } catch (e: any) {
      setErr(e?.message || "search failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="grid gap-4">
      <div className="card p-5">
        <div className="text-lg font-semibold">Library Search</div>
        <div className="text-sm text-gray-700 mt-1">Semantic search: input text → find closest videos.</div>

        <div className="mt-4 flex items-center gap-3">
          <input
            className="btn w-full max-w-xl text-left"
            placeholder='e.g. "pour tea"'
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") runSearch();
            }}
          />
          <button className="btn btn-primary" onClick={runSearch} disabled={!query || loading}>
            {loading ? "Searching…" : "Search"}
          </button>
        </div>

        {err ? <div className="mt-3 text-sm text-red-700">{err}</div> : null}
      </div>

      <div className="card p-5">
        <div className="text-sm font-medium mb-2">Matches</div>
        {hits.length === 0 ? (
          <div className="text-sm text-gray-600">{loading ? "…" : "No results"}</div>
        ) : (
          <ul className="text-sm grid gap-2">
            {hits.map((h) => (
              <li key={h.file} className="flex items-center justify-between border-b border-gray-200 pb-2">
                <span className="font-mono">{h.file}</span>
                <span className="text-gray-600">{h.score}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </main>
  );
}
