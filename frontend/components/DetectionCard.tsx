"use client";

import { useState } from "react";
import type { Detection } from "@/lib/api";
import { Card } from "./Card";
import { SeverityBadge } from "./SeverityBadge";

const PATTERN_LABELS: Record<string, { name: string; emoji: string }> = {
  fake_urgency: { name: "Fake Urgency", emoji: "⏱" },
  scarcity: { name: "Scarcity", emoji: "📉" },
  confirmshaming: { name: "Confirmshaming", emoji: "💢" },
  preselected_options: { name: "Preselected Options", emoji: "☑" },
  cookie_manipulation: { name: "Cookie Manipulation", emoji: "🍪" },
};

const METHOD_LABELS: Record<Detection["method"], string> = {
  rule: "regex",
  dom: "DOM",
  hybrid: "regex + DOM",
  llm: "LLM",
};

export function DetectionCard({ detection }: { detection: Detection }) {
  const [showFix, setShowFix] = useState(false);
  const meta = PATTERN_LABELS[detection.pattern_type] ?? {
    name: detection.pattern_type.replace(/_/g, " "),
    emoji: "⚠",
  };
  const confPct = Math.round(detection.confidence * 100);

  return (
    <Card className="p-6">
      <header className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3">
          <span
            aria-hidden
            className="grid h-10 w-10 place-items-center rounded-lg bg-white/[0.04] text-xl ring-1 ring-inset ring-border"
          >
            {meta.emoji}
          </span>
          <div>
            <h3 className="font-display text-base font-semibold tracking-tight text-foreground">
              {meta.name}
            </h3>
            <p className="mt-0.5 font-mono text-[10px] uppercase tracking-[0.08em] text-muted-foreground">
              detected via {METHOD_LABELS[detection.method]}
            </p>
          </div>
        </div>
        <SeverityBadge severity={detection.severity} />
      </header>

      <blockquote className="mt-5 rounded-md border-l-2 border-accent/40 bg-white/[0.02] px-4 py-3 text-sm italic leading-relaxed text-foreground/80">
        “{detection.evidence_text}”
      </blockquote>

      <div className="mt-5">
        <div className="flex items-center justify-between font-mono text-[10px] uppercase tracking-[0.08em] text-muted-foreground">
          <span>Confidence</span>
          <span className="text-foreground">{confPct}%</span>
        </div>
        <div className="mt-2 h-1 w-full overflow-hidden rounded-full bg-white/[0.06]">
          <div
            className="h-full rounded-full bg-accent transition-all duration-500 ease-out"
            style={{
              width: `${confPct}%`,
              boxShadow: "0 0 12px rgb(245 158 11 / 0.45)",
            }}
          />
        </div>
      </div>

      <p className="mt-5 text-sm leading-relaxed text-foreground/85">
        {detection.explanation}
      </p>

      <button
        type="button"
        onClick={() => setShowFix((v) => !v)}
        aria-expanded={showFix}
        className={[
          "mt-4 inline-flex items-center gap-1.5 rounded-md px-1.5 py-1 -mx-1.5",
          "font-mono text-[11px] uppercase tracking-[0.08em] text-muted-foreground",
          "transition-colors hover:text-accent focus-visible:text-accent focus-visible:outline-none",
        ].join(" ")}
      >
        <span aria-hidden className={`transition-transform duration-200 ${showFix ? "rotate-90" : ""}`}>
          ▸
        </span>
        How to fix this
      </button>
      {showFix && (
        <div className="fade-in mt-3 rounded-md bg-accent/[0.06] px-4 py-3 ring-1 ring-inset ring-accent/15">
          <p className="font-mono text-[10px] uppercase tracking-[0.08em] text-accent">
            Suggested fix
          </p>
          <p className="mt-1.5 text-sm leading-relaxed text-foreground/90">
            {detection.suggested_fix}
          </p>
        </div>
      )}
    </Card>
  );
}
