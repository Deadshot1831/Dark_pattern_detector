import { ScanForm } from "@/components/ScanForm";

const PATTERNS = [
  {
    emoji: "⏱",
    name: "Fake Urgency",
    desc: "Countdown timers, “ends in 5 minutes”, fake deadlines that reset on refresh.",
  },
  {
    emoji: "📉",
    name: "Scarcity",
    desc: "“Only 2 left in stock”, “selling fast” — pressure built on fabricated supply.",
  },
  {
    emoji: "💢",
    name: "Confirmshaming",
    desc: "Decline buttons that mock the user (“No thanks, I don’t like saving money”).",
  },
  {
    emoji: "☑",
    name: "Preselected Options",
    desc: "Pre-checked marketing emails, paid add-ons, opt-outs disguised as opt-ins.",
  },
  {
    emoji: "🍪",
    name: "Cookie Manipulation",
    desc: "Hidden or de-emphasised reject button, dark patterns in consent banners.",
  },
];

export default function Home() {
  return (
    <div className="space-y-24 md:space-y-32">
      {/* ─── Hero ─── */}
      <section className="space-y-8 pt-4 md:pt-12">
        <div className="space-y-7">
          <div className="inline-flex items-center gap-2 rounded-full border border-border bg-card px-3 py-1 backdrop-blur-md shadow-glow-sm">
            <span className="relative flex h-1.5 w-1.5">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-accent opacity-75" />
              <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-accent" />
            </span>
            <span className="font-mono text-[10px] uppercase tracking-[0.12em] text-muted-foreground">
              5 detectors · rule + LLM hybrid
            </span>
          </div>
          <h1 className="font-display text-4xl font-semibold leading-[1.05] tracking-tight text-foreground sm:text-5xl md:text-6xl lg:text-7xl">
            Audit any website
            <br className="hidden sm:block" /> for{" "}
            <span className="text-accent">dark patterns</span>.
          </h1>
          <p className="max-w-2xl text-base leading-relaxed text-muted-foreground md:text-lg">
            Paste a public URL. DeceptiTech opens it in a real browser, captures the
            page, and runs five detectors — rule-based plus a local LLM second pass —
            to surface manipulative UI/UX with evidence and suggested fixes.
          </p>
        </div>
        <ScanForm />
      </section>

      {/* ─── Pattern grid ─── */}
      <section className="space-y-8">
        <header className="space-y-2">
          <p className="font-mono text-[11px] uppercase tracking-[0.12em] text-muted-foreground">
            What we detect
          </p>
          <h2 className="font-display text-2xl font-semibold tracking-tight text-foreground md:text-3xl">
            Five patterns. One scan.
          </h2>
        </header>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {PATTERNS.map((p) => (
            <article
              key={p.name}
              className="group rounded-xl border border-border bg-card p-6 backdrop-blur-md transition-all duration-300 ease-out hover:border-border-hover hover:bg-card-solid/80"
            >
              <span
                aria-hidden
                className="grid h-10 w-10 place-items-center rounded-lg bg-white/[0.04] text-xl ring-1 ring-inset ring-border transition-all duration-300 group-hover:bg-accent/10 group-hover:ring-accent/30"
              >
                {p.emoji}
              </span>
              <h3 className="mt-4 font-display text-base font-semibold tracking-tight text-foreground">
                {p.name}
              </h3>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{p.desc}</p>
            </article>
          ))}
        </div>
      </section>

      {/* ─── How it works ─── */}
      <section className="space-y-8">
        <header className="space-y-2">
          <p className="font-mono text-[11px] uppercase tracking-[0.12em] text-muted-foreground">
            How it works
          </p>
          <h2 className="font-display text-2xl font-semibold tracking-tight text-foreground md:text-3xl">
            From URL to evidence in seconds.
          </h2>
        </header>
        <ol className="grid gap-4 md:grid-cols-3">
          {[
            { n: "01", t: "Crawl", d: "Headless Chromium opens the URL, waits for JS to render, captures HTML + screenshots." },
            { n: "02", t: "Extract", d: "Buttons, checkboxes, modals, cookie banners, and countdowns are pulled out as structured data." },
            { n: "03", t: "Detect", d: "Five detectors run in parallel. Ambiguous text is sent to a local LLM for a second opinion." },
          ].map((s) => (
            <li
              key={s.n}
              className="rounded-xl border border-border bg-card p-6 backdrop-blur-md"
            >
              <span className="font-mono text-xs tracking-[0.08em] text-accent">{s.n}</span>
              <h3 className="mt-3 font-display text-lg font-semibold tracking-tight text-foreground">
                {s.t}
              </h3>
              <p className="mt-1.5 text-sm leading-relaxed text-muted-foreground">{s.d}</p>
            </li>
          ))}
        </ol>
      </section>
    </div>
  );
}
