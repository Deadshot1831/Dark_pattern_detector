"use client";

import { useEffect, useState, use } from "react";
import Link from "next/link";
import {
  exportURL,
  getDetections,
  getScan,
  screenshotURL,
  type Detection,
  type Scan,
} from "@/lib/api";
import { DetectionCard } from "@/components/DetectionCard";
import { SeverityBadge } from "@/components/SeverityBadge";
import { StatusBadge } from "@/components/StatusBadge";

const POLL_MS = 1500;

export default function ScanPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [scan, setScan] = useState<Scan | null>(null);
  const [detections, setDetections] = useState<Detection[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    let timer: ReturnType<typeof setTimeout> | null = null;

    async function tick() {
      try {
        const s = await getScan(id);
        if (cancelled) return;
        setScan(s);
        if (s.status === "completed") {
          const d = await getDetections(id);
          if (!cancelled) setDetections(d);
          return; // stop polling
        }
        if (s.status === "failed") return;
        timer = setTimeout(tick, POLL_MS);
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : String(err));
      }
    }

    tick();
    return () => {
      cancelled = true;
      if (timer) clearTimeout(timer);
    };
  }, [id]);

  if (error) {
    return (
      <div className="space-y-4">
        <Link href="/" className="text-sm text-zinc-500 hover:text-zinc-900">← Back</Link>
        <div className="rounded-md border border-rose-200 bg-rose-50 p-4 text-sm text-rose-800">{error}</div>
      </div>
    );
  }

  if (!scan) {
    return (
      <div className="text-zinc-500">Loading scan…</div>
    );
  }

  const isDone = scan.status === "completed";
  const isFailed = scan.status === "failed";

  return (
    <div className="space-y-8">
      <div>
        <Link href="/" className="text-sm text-zinc-500 hover:text-zinc-900">← New scan</Link>
      </div>

      <header className="rounded-xl border border-zinc-200 bg-white p-6">
        <div className="flex flex-wrap items-center gap-3">
          <StatusBadge status={scan.status} />
          {isDone && scan.overall_severity && (
            <SeverityBadge severity={scan.overall_severity} />
          )}
          {isDone && scan.total_patterns_found != null && (
            <span className="rounded-full bg-zinc-100 px-3 py-1 text-xs font-medium text-zinc-700">
              {scan.total_patterns_found} pattern{scan.total_patterns_found === 1 ? "" : "s"} detected
            </span>
          )}
        </div>
        <h1 className="mt-3 text-2xl font-semibold">
          {scan.page_title || scan.url}
        </h1>
        <a
          href={scan.final_url || scan.url}
          target="_blank"
          rel="noreferrer noopener"
          className="mt-1 inline-block break-all text-sm text-zinc-500 hover:text-zinc-900"
        >
          {scan.final_url || scan.url} ↗
        </a>
        {isFailed && scan.error_message && (
          <p className="mt-3 rounded-md border border-rose-200 bg-rose-50 p-3 text-sm text-rose-800">
            {scan.error_message}
          </p>
        )}
        {isDone && (
          <div className="mt-4 flex flex-wrap gap-2">
            <a
              href={exportURL(id, "pdf")}
              className="inline-flex items-center gap-1.5 rounded-lg border border-zinc-200 bg-white px-3 py-1.5 text-xs font-medium text-zinc-700 hover:border-zinc-300 hover:bg-zinc-50"
            >
              <span aria-hidden>📄</span> Download PDF
            </a>
            <a
              href={exportURL(id, "json")}
              className="inline-flex items-center gap-1.5 rounded-lg border border-zinc-200 bg-white px-3 py-1.5 text-xs font-medium text-zinc-700 hover:border-zinc-300 hover:bg-zinc-50"
            >
              <span aria-hidden>{ }</span> Download JSON
            </a>
            <a
              href={exportURL(id, "html")}
              target="_blank"
              rel="noreferrer noopener"
              className="inline-flex items-center gap-1.5 rounded-lg border border-zinc-200 bg-white px-3 py-1.5 text-xs font-medium text-zinc-700 hover:border-zinc-300 hover:bg-zinc-50"
            >
              <span aria-hidden>🔗</span> Open print view
            </a>
          </div>
        )}
      </header>

      {!isDone && !isFailed && (
        <div className="rounded-xl border border-zinc-200 bg-white p-8 text-center">
          <p className="text-sm text-zinc-500">
            Opening the page in a headless browser, capturing screenshots, and running detectors…
          </p>
        </div>
      )}

      {isDone && (
        <div className="grid gap-6 lg:grid-cols-[1fr_1.2fr]">
          <aside className="space-y-3">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-zinc-500">Captured page</h2>
            <div className="overflow-hidden rounded-xl border border-zinc-200 bg-white">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={screenshotURL(id, "viewport")}
                alt="Viewport screenshot of the scanned page"
                className="block w-full"
              />
            </div>
            <a
              href={screenshotURL(id, "full_page")}
              target="_blank"
              rel="noreferrer noopener"
              className="inline-block text-xs text-zinc-500 hover:text-zinc-900"
            >
              View full-page screenshot ↗
            </a>
          </aside>

          <section className="space-y-3">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-zinc-500">
              Findings ({detections.length})
            </h2>
            {detections.length === 0 ? (
              <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-6 text-emerald-900">
                <p className="font-medium">No dark patterns detected.</p>
                <p className="mt-1 text-sm text-emerald-800">
                  This page passes the 5 MVP checks (urgency, scarcity, confirmshaming, preselected options, cookie consent).
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {detections
                  .slice()
                  .sort((a, b) => sevRank(b.severity) - sevRank(a.severity) || b.confidence - a.confidence)
                  .map((d) => (
                    <DetectionCard key={d.id} detection={d} />
                  ))}
              </div>
            )}
          </section>
        </div>
      )}
    </div>
  );
}

function sevRank(s: Detection["severity"]): number {
  return s === "high" ? 2 : s === "medium" ? 1 : 0;
}
