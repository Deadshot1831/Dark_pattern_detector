import { ScanForm } from "@/components/ScanForm";

const PATTERNS = [
  { emoji: "⏱", name: "Fake Urgency", desc: "Countdown timers, 'ends in 5 minutes'" },
  { emoji: "📉", name: "Scarcity", desc: "'Only 2 left in stock', 'selling fast'" },
  { emoji: "💢", name: "Confirmshaming", desc: "'No thanks, I don't like saving money'" },
  { emoji: "☑️", name: "Preselected Options", desc: "Pre-checked marketing emails / paid add-ons" },
  { emoji: "🍪", name: "Cookie Manipulation", desc: "Hidden or de-emphasised reject button" },
];

export default function Home() {
  return (
    <div className="space-y-12">
      <section className="space-y-6">
        <div className="space-y-3">
          <h1 className="text-4xl font-semibold tracking-tight">Audit a website for dark patterns</h1>
          <p className="max-w-2xl text-zinc-600">
            Paste any public URL. DeceptiTech opens it in a real browser, captures the page, and runs five detectors
            (rule-based + a local LLM) to surface manipulative UI/UX with evidence and suggested fixes.
          </p>
        </div>
        <ScanForm />
      </section>

      <section className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {PATTERNS.map((p) => (
          <div key={p.name} className="rounded-lg border border-zinc-200 bg-white p-4">
            <div className="flex items-center gap-2">
              <span className="text-xl" aria-hidden>{p.emoji}</span>
              <h2 className="text-sm font-semibold">{p.name}</h2>
            </div>
            <p className="mt-1 text-sm text-zinc-600">{p.desc}</p>
          </div>
        ))}
      </section>
    </div>
  );
}
