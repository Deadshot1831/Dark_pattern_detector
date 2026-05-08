"use client";

import { useState } from "react";
import type { Detection } from "@/lib/api";
import { SeverityBadge } from "./SeverityBadge";

const PATTERN_LABELS: Record<string, { name: string; emoji: string }> = {
  fake_urgency: { name: "Fake Urgency", emoji: "⏱" },
  scarcity: { name: "Scarcity", emoji: "📉" },
  confirmshaming: { name: "Confirmshaming", emoji: "💢" },
  preselected_options: { name: "Preselected Options", emoji: "☑️" },
  cookie_manipulation: { name: "Cookie Manipulation", emoji: "🍪" },
};

const METHOD_LABELS: Record<Detection["method"], string> = {
  rule: "regex",
  dom: "DOM",
  hybrid: "regex+DOM",
  llm: "LLM",
};

export function DetectionCard({ detection }: { detection: Detection }) {
  const [showFix, setShowFix] = useState(false);
  const meta = PATTERN_LABELS[detection.pattern_type] ?? {
    name: detection.pattern_type.replace(/_/g, " "),
    emoji: "⚠️",
  };
  const confPct = Math.round(detection.confidence * 100);

  return (
    <article className="rounded-xl border border-zinc-200 bg-white p-5 shadow-sm transition hover:shadow">
      <header className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3">
          <span className="text-2xl leading-none" aria-hidden>
            {meta.emoji}
          </span>
          <div>
            <h3 className="text-base font-semibold text-zinc-900">{meta.name}</h3>
            <p className="text-xs uppercase tracking-wide text-zinc-500">
              detected via {METHOD_LABELS[detection.method]}
            </p>
          </div>
        </div>
        <SeverityBadge severity={detection.severity} />
      </header>

      <blockquote className="mt-4 border-l-4 border-zinc-200 bg-zinc-50 px-4 py-3 text-sm italic text-zinc-700">
        “{detection.evidence_text}”
      </blockquote>

      <div className="mt-4">
        <div className="flex items-center justify-between text-xs text-zinc-500">
          <span>Confidence</span>
          <span className="font-mono">{confPct}%</span>
        </div>
        <div className="mt-1 h-1.5 w-full overflow-hidden rounded-full bg-zinc-100">
          <div
            className="h-full rounded-full bg-zinc-900 transition-all"
            style={{ width: `${confPct}%` }}
          />
        </div>
      </div>

      <p className="mt-4 text-sm leading-relaxed text-zinc-700">{detection.explanation}</p>

      <button
        type="button"
        onClick={() => setShowFix((v) => !v)}
        className="mt-3 inline-flex items-center gap-1 text-xs font-medium text-zinc-600 hover:text-zinc-900"
      >
        <span>{showFix ? "▾" : "▸"}</span>
        How to fix this
      </button>
      {showFix && (
        <p className="mt-2 rounded-md bg-emerald-50 p-3 text-sm leading-relaxed text-emerald-900">
          {detection.suggested_fix}
        </p>
      )}
    </article>
  );
}
