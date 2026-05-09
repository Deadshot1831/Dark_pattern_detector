import type { Severity } from "@/lib/api";

const STYLES: Record<Severity, string> = {
  low: "bg-emerald-500/10 text-emerald-300 ring-emerald-500/25",
  medium: "bg-accent/15 text-accent ring-accent/30",
  high: "bg-rose-500/15 text-rose-300 ring-rose-500/30",
};

export function SeverityBadge({
  severity,
  className = "",
}: {
  severity: Severity;
  className?: string;
}) {
  return (
    <span
      className={
        "inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 " +
        "font-mono text-[10px] font-medium uppercase tracking-[0.08em] " +
        "ring-1 ring-inset " +
        STYLES[severity] +
        " " +
        className
      }
    >
      <span className="h-1.5 w-1.5 rounded-full bg-current shadow-[0_0_8px_currentColor]" />
      {severity}
    </span>
  );
}
