"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import {
  deleteScan,
  getHistory,
  type HistoryItem,
} from "@/lib/api";
import { SeverityBadge } from "@/components/SeverityBadge";
import { StatusBadge } from "@/components/StatusBadge";

export default function HistoryPage() {
  const [items, setItems] = useState<HistoryItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const r = await getHistory(1, 50);
      setItems(r.items);
      setTotal(r.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  async function onDelete(id: string) {
    if (!confirm("Delete this scan? Screenshots and detections will be removed.")) return;
    setBusyId(id);
    try {
      await deleteScan(id);
      setItems((prev) => prev.filter((s) => s.scan_id !== id));
      setTotal((t) => Math.max(0, t - 1));
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusyId(null);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-end justify-between gap-3">
        <div>
          <h1 className="text-3xl font-semibold tracking-tight">Scan history</h1>
          <p className="mt-1 text-sm text-zinc-600">
            {loading ? "Loading…" : `${total} total scan${total === 1 ? "" : "s"}`}
          </p>
        </div>
        <Link
          href="/"
          className="rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-800"
        >
          New scan
        </Link>
      </div>

      {error && (
        <div className="rounded-md border border-rose-200 bg-rose-50 p-3 text-sm text-rose-800">{error}</div>
      )}

      {!loading && items.length === 0 && (
        <div className="rounded-xl border border-zinc-200 bg-white p-8 text-center">
          <p className="text-zinc-600">No scans yet. Start one from the home page.</p>
        </div>
      )}

      {items.length > 0 && (
        <ul className="overflow-hidden rounded-xl border border-zinc-200 bg-white">
          {items.map((s, i) => (
            <li
              key={s.scan_id}
              className={`flex flex-wrap items-center justify-between gap-3 px-5 py-4 ${
                i > 0 ? "border-t border-zinc-100" : ""
              }`}
            >
              <Link href={`/scan/${s.scan_id}`} className="min-w-0 flex-1 group">
                <div className="flex items-center gap-2">
                  <StatusBadge status={s.status} />
                  {s.overall_severity && <SeverityBadge severity={s.overall_severity} />}
                  {s.total_patterns_found != null && s.total_patterns_found > 0 && (
                    <span className="rounded-full bg-zinc-100 px-2 py-0.5 text-xs font-medium text-zinc-700">
                      {s.total_patterns_found} finding{s.total_patterns_found === 1 ? "" : "s"}
                    </span>
                  )}
                </div>
                <p className="mt-1 truncate text-base font-medium text-zinc-900 group-hover:underline">
                  {s.page_title || s.url}
                </p>
                <p className="truncate text-xs text-zinc-500">
                  {s.url} · {new Date(s.started_at).toLocaleString()}
                </p>
              </Link>
              <button
                type="button"
                onClick={() => onDelete(s.scan_id)}
                disabled={busyId === s.scan_id}
                className="rounded-md border border-zinc-200 bg-white px-3 py-1.5 text-xs font-medium text-zinc-600 hover:border-rose-200 hover:bg-rose-50 hover:text-rose-700 disabled:opacity-50"
              >
                {busyId === s.scan_id ? "Deleting…" : "Delete"}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
