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
import { Card } from "@/components/Card";
import { buttonClasses } from "@/components/Button";

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
    <div className="space-y-10">
      <header className="flex items-end justify-between gap-4">
        <div className="space-y-2">
          <p className="font-mono text-[11px] uppercase tracking-[0.12em] text-muted-foreground">
            Activity
          </p>
          <h1 className="font-display text-3xl font-semibold tracking-tight text-foreground md:text-4xl">
            Scan history
          </h1>
          <p className="font-mono text-xs text-muted-foreground">
            {loading ? "Loading…" : `${total} total scan${total === 1 ? "" : "s"}`}
          </p>
        </div>
        <Link href="/" className={buttonClasses("primary", "md")}>
          New scan <span aria-hidden>→</span>
        </Link>
      </header>

      {error && (
        <Card className="p-4 ring-1 ring-rose-500/30 border-rose-500/30">
          <p className="text-sm text-rose-300">{error}</p>
        </Card>
      )}

      {!loading && items.length === 0 && (
        <Card className="p-10 text-center">
          <p className="font-display text-base font-semibold text-foreground">
            No scans yet.
          </p>
          <p className="mt-2 text-sm text-muted-foreground">
            Start your first scan from the home page.
          </p>
          <Link href="/" className={`${buttonClasses("secondary", "sm")} mt-5`}>
            Go to home
          </Link>
        </Card>
      )}

      {items.length > 0 && (
        <Card className="overflow-hidden p-0">
          <ul role="list">
            {items.map((s, i) => (
              <li
                key={s.scan_id}
                className={`group flex flex-wrap items-center justify-between gap-4 px-5 py-4 transition-colors hover:bg-white/[0.025] md:px-6 ${
                  i > 0 ? "border-t border-border" : ""
                }`}
              >
                <Link
                  href={`/scan/${s.scan_id}`}
                  className="min-w-0 flex-1 focus-visible:outline-none"
                >
                  <div className="flex flex-wrap items-center gap-2">
                    <StatusBadge status={s.status} />
                    {s.overall_severity && <SeverityBadge severity={s.overall_severity} />}
                    {s.total_patterns_found != null && s.total_patterns_found > 0 && (
                      <span className="rounded-full bg-white/[0.04] px-2.5 py-1 font-mono text-[10px] uppercase tracking-[0.08em] text-muted-foreground ring-1 ring-inset ring-white/10">
                        {s.total_patterns_found} finding
                        {s.total_patterns_found === 1 ? "" : "s"}
                      </span>
                    )}
                  </div>
                  <p className="mt-2 truncate font-display text-base font-semibold tracking-tight text-foreground transition-colors group-hover:text-accent">
                    {s.page_title || s.url}
                  </p>
                  <p className="truncate font-mono text-[11px] tracking-tight text-muted-foreground">
                    {s.url} <span className="opacity-50">·</span>{" "}
                    {new Date(s.started_at).toLocaleString()}
                  </p>
                </Link>
                <button
                  type="button"
                  onClick={() => onDelete(s.scan_id)}
                  disabled={busyId === s.scan_id}
                  className={[
                    "rounded-md px-3 py-1.5 font-mono text-[10px] uppercase tracking-[0.08em]",
                    "border border-border text-muted-foreground bg-transparent",
                    "transition-all duration-200",
                    "hover:border-rose-500/40 hover:bg-rose-500/10 hover:text-rose-300",
                    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-rose-500/40",
                    "disabled:opacity-50 disabled:pointer-events-none",
                  ].join(" ")}
                >
                  {busyId === s.scan_id ? "Deleting…" : "Delete"}
                </button>
              </li>
            ))}
          </ul>
        </Card>
      )}
    </div>
  );
}
