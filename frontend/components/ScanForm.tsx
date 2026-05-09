"use client";

import { useState, FormEvent } from "react";
import { useRouter } from "next/navigation";
import { startScan } from "@/lib/api";
import { Button } from "./Button";

export function ScanForm() {
  const router = useRouter();
  const [url, setUrl] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      const trimmed = url.trim();
      const final = /^https?:\/\//i.test(trimmed) ? trimmed : `https://${trimmed}`;
      const scan = await startScan(final);
      router.push(`/scan/${scan.scan_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
      setBusy(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="w-full">
      <div className="flex flex-col gap-3 sm:flex-row">
        <input
          type="text"
          required
          inputMode="url"
          autoComplete="url"
          placeholder="https://example.com"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          disabled={busy}
          className={[
            "h-12 flex-1 rounded-lg px-4 text-base",
            "bg-card backdrop-blur-md border border-border text-foreground",
            "placeholder:text-muted-foreground placeholder:font-mono placeholder:text-sm",
            "transition-all duration-200",
            "focus:border-accent/50 focus:outline-none focus:ring-2 focus:ring-accent/20",
            "focus:shadow-[0_0_24px_rgb(245_158_11_/_0.10)]",
            "disabled:opacity-60",
          ].join(" ")}
        />
        <Button type="submit" disabled={busy || !url.trim()} size="lg">
          {busy ? (
            <>
              <span className="h-2 w-2 animate-pulse rounded-full bg-accent-foreground/70" />
              Starting
            </>
          ) : (
            <>
              Scan website <span aria-hidden>→</span>
            </>
          )}
        </Button>
      </div>
      {error && (
        <p
          role="alert"
          className="mt-3 rounded-md bg-rose-500/10 px-3 py-2 text-sm text-rose-300 ring-1 ring-inset ring-rose-500/25"
        >
          {error}
        </p>
      )}
    </form>
  );
}
