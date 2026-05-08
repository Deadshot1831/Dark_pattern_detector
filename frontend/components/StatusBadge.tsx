import type { ScanStatus } from "@/lib/api";

const STYLES: Record<ScanStatus, string> = {
  pending: "bg-zinc-100 text-zinc-700 ring-zinc-200",
  running: "bg-blue-100 text-blue-700 ring-blue-200",
  completed: "bg-emerald-100 text-emerald-800 ring-emerald-200",
  failed: "bg-rose-100 text-rose-800 ring-rose-200",
};

const LABEL: Record<ScanStatus, string> = {
  pending: "Queued",
  running: "Scanning…",
  completed: "Completed",
  failed: "Failed",
};

export function StatusBadge({ status }: { status: ScanStatus }) {
  const animate = status === "pending" || status === "running" ? "animate-pulse" : "";
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium ring-1 ${STYLES[status]} ${animate}`}
    >
      {LABEL[status]}
    </span>
  );
}
