import type { Severity } from "@/lib/api";

const STYLES: Record<Severity, string> = {
  low: "bg-emerald-100 text-emerald-800 ring-emerald-200",
  medium: "bg-amber-100 text-amber-900 ring-amber-200",
  high: "bg-rose-100 text-rose-800 ring-rose-200",
};

export function SeverityBadge({ severity, className = "" }: { severity: Severity; className?: string }) {
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-semibold uppercase tracking-wide ring-1 ${STYLES[severity]} ${className}`}
    >
      <span className="inline-block h-1.5 w-1.5 rounded-full bg-current opacity-70" />
      {severity}
    </span>
  );
}
