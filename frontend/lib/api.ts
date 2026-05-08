export const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type ScanStatus = "pending" | "running" | "completed" | "failed";
export type Severity = "low" | "medium" | "high";

export interface Scan {
  scan_id: string;
  status: ScanStatus;
  url: string;
  final_url: string | null;
  page_title: string | null;
  started_at: string;
  completed_at: string | null;
  error_message: string | null;
  full_page_screenshot_url: string | null;
  viewport_screenshot_url: string | null;
  total_patterns_found: number | null;
  overall_severity: Severity | null;
}

export interface Detection {
  id: string;
  pattern_type: string;
  evidence_text: string;
  evidence_selector: string | null;
  confidence: number;
  severity: Severity;
  explanation: string;
  suggested_fix: string;
  method: "rule" | "dom" | "hybrid" | "llm";
}

async function jsonFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const r = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { "content-type": "application/json", ...(init?.headers || {}) },
    cache: "no-store",
  });
  if (!r.ok) {
    const body = await r.text().catch(() => "");
    throw new Error(`HTTP ${r.status}: ${body || r.statusText}`);
  }
  return r.json() as Promise<T>;
}

export function startScan(url: string): Promise<Scan> {
  return jsonFetch<Scan>("/scan", {
    method: "POST",
    body: JSON.stringify({ url }),
  });
}

export function getScan(id: string): Promise<Scan> {
  return jsonFetch<Scan>(`/scan/${id}`);
}

export function getDetections(id: string): Promise<Detection[]> {
  return jsonFetch<Detection[]>(`/scan/${id}/detections`);
}

export function screenshotURL(id: string, kind: "full_page" | "viewport"): string {
  return `${API_BASE}/scan/${id}/screenshot/${kind}`;
}
