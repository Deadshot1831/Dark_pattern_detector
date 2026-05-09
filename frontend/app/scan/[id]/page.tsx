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
import { Card } from "@/components/Card";
import { DetectionCard } from "@/components/DetectionCard";
import { SeverityBadge } from "@/components/SeverityBadge";
import { StatusBadge } from "@/components/StatusBadge";
import { buttonClasses } from "@/components/Button";

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
          return;
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
        <BackLink />
        <Card className="p-6 ring-1 ring-rose-500/30 border-rose-500/30">
          <p className="text-sm text-rose-300">{error}</p>
        </Card>
      </div>
    );
  }

  if (!scan) {
    return (
      <div className="space-y-6">
        <BackLink />
        <div className="font-mono text-xs uppercase tracking-[0.12em] text-muted-foreground">
          <span className="inline-block h-1.5 w-1.5 animate-pulse rounded-full bg-accent shadow-glow-sm align-middle" />
          <span className="ml-2 align-middle">Loading scan…</span>
        </div>
      </div>
    );
  }

  const isDone = scan.status === "completed";
  const isFailed = scan.status === "failed";

  return (
    <div className="space-y-10">
      <BackLink />

      {/* Scan header card — uses the highlighted Card variant when complete to
          give it a soft amber glow that anchors the page. */}
      <Card variant={isDone ? "highlighted" : "glass"} className="p-6 md:p-8">
        <div className="flex flex-wrap items-center gap-2">
          <StatusBadge status={scan.status} />
          {isDone && scan.overall_severity && (
            <SeverityBadge severity={scan.overall_severity} />
          )}
          {isDone && scan.total_patterns_found != null && (
            <span className="rounded-full bg-white/[0.04] px-2.5 py-1 font-mono text-[10px] uppercase tracking-[0.08em] text-muted-foreground ring-1 ring-inset ring-white/10">
              {scan.total_patterns_found} pattern
              {scan.total_patterns_found === 1 ? "" : "s"} detected
            </span>
          )}
        </div>
        <h1 className="mt-4 font-display text-2xl font-semibold leading-tight tracking-tight text-foreground md:text-3xl">
          {scan.page_title || scan.url}
        </h1>
        <a
          href={scan.final_url || scan.url}
          target="_blank"
          rel="noreferrer noopener"
          className="mt-1.5 inline-block break-all font-mono text-xs text-muted-foreground transition-colors hover:text-accent focus-visible:text-accent focus-visible:outline-none"
        >
          {scan.final_url || scan.url} ↗
        </a>
        {isFailed && scan.error_message && (
          <div className="mt-4 rounded-md bg-rose-500/10 px-4 py-3 ring-1 ring-inset ring-rose-500/30">
            <p className="font-mono text-[10px] uppercase tracking-[0.08em] text-rose-300">
              Error
            </p>
            <p className="mt-1 text-sm text-rose-200">{scan.error_message}</p>
          </div>
        )}
        {isDone && (
          <div className="mt-6 flex flex-wrap gap-2">
            <a href={exportURL(id, "pdf")} className={buttonClasses("primary", "sm")}>
              <span aria-hidden>↓</span> Download PDF
            </a>
            <a href={exportURL(id, "json")} className={buttonClasses("secondary", "sm")}>
              <span aria-hidden>{ }</span> JSON
            </a>
            <a
              href={exportURL(id, "html")}
              target="_blank"
              rel="noreferrer noopener"
              className={buttonClasses("ghost", "sm")}
            >
              Print view ↗
            </a>
          </div>
        )}
      </Card>

      {/* In-progress shimmer */}
      {!isDone && !isFailed && (
        <Card className="p-10 text-center">
          <p className="font-mono text-[11px] uppercase tracking-[0.12em] text-muted-foreground">
            <span className="inline-block h-1.5 w-1.5 animate-pulse rounded-full bg-accent shadow-glow-sm align-middle" />
            <span className="ml-2 align-middle">Working</span>
          </p>
          <p className="mt-3 text-sm text-muted-foreground">
            Opening the page in a headless browser, capturing screenshots, and running detectors…
          </p>
        </Card>
      )}

      {/* Two-column layout: screenshot on the left, detection list on the right */}
      {isDone && (
        <div className="grid gap-6 lg:grid-cols-[1fr_1.2fr]">
          <aside className="space-y-3">
            <SectionEyebrow>Captured page</SectionEyebrow>
            <Card className="overflow-hidden p-0">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={screenshotURL(id, "viewport")}
                alt="Viewport screenshot of the scanned page"
                className="block w-full"
              />
            </Card>
            <a
              href={screenshotURL(id, "full_page")}
              target="_blank"
              rel="noreferrer noopener"
              className="inline-block font-mono text-[11px] uppercase tracking-[0.08em] text-muted-foreground transition-colors hover:text-accent focus-visible:text-accent focus-visible:outline-none"
            >
              View full-page screenshot ↗
            </a>
          </aside>

          <section className="space-y-3">
            <SectionEyebrow>Findings ({detections.length})</SectionEyebrow>
            {detections.length === 0 ? (
              <Card className="p-6">
                <p className="font-display text-base font-semibold text-foreground">
                  ✓ No dark patterns detected
                </p>
                <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                  This page passes the 5 MVP checks (urgency, scarcity, confirmshaming,
                  preselected options, cookie consent).
                </p>
              </Card>
            ) : (
              <div className="space-y-4">
                {detections
                  .slice()
                  .sort(
                    (a, b) =>
                      sevRank(b.severity) - sevRank(a.severity) ||
                      b.confidence - a.confidence,
                  )
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

function BackLink() {
  return (
    <Link
      href="/"
      className="inline-flex items-center gap-1.5 font-mono text-[11px] uppercase tracking-[0.08em] text-muted-foreground transition-colors hover:text-accent focus-visible:text-accent focus-visible:outline-none"
    >
      <span aria-hidden>←</span> New scan
    </Link>
  );
}

function SectionEyebrow({ children }: { children: React.ReactNode }) {
  return (
    <h2 className="font-mono text-[11px] uppercase tracking-[0.12em] text-muted-foreground">
      {children}
    </h2>
  );
}

function sevRank(s: Detection["severity"]): number {
  return s === "high" ? 2 : s === "medium" ? 1 : 0;
}
