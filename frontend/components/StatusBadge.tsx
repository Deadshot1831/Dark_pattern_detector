import type { ScanStatus } from "@/lib/api";

const STYLES: Record<ScanStatus, string> = {
  pending: "bg-white/[0.04] text-muted-foreground ring-white/10",
  running: "bg-accent/15 text-accent ring-accent/30",
  completed: "bg-emerald-500/10 text-emerald-300 ring-emerald-500/25",
  failed: "bg-rose-500/15 text-rose-300 ring-rose-500/30",
};

const LABEL: Record<ScanStatus, string> = {
  pending: "Queued",
  running: "Scanning",
  completed: "Completed",
  failed: "Failed",
};

export function StatusBadge({ status }: { status: ScanStatus }) {
  const animate = status === "pending" || status === "running" ? "animate-pulse" : "";
  return (
    <span
      className={
        "inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 " +
        "font-mono text-[10px] font-medium uppercase tracking-[0.08em] " +
        "ring-1 ring-inset " +
        STYLES[status] +
        " " +
        animate
      }
    >
      <span className="h-1.5 w-1.5 rounded-full bg-current shadow-[0_0_8px_currentColor]" />
      {LABEL[status]}
    </span>
  );
}
