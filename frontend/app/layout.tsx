import type { Metadata } from "next";
import { Space_Grotesk, Inter, JetBrains_Mono } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const display = Space_Grotesk({
  subsets: ["latin"],
  variable: "--font-space-grotesk",
  display: "swap",
});
const sans = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});
const mono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "DeceptiTech — Dark Pattern Detector",
  description:
    "Scan a website URL and identify manipulative UI/UX patterns: fake urgency, scarcity, confirmshaming, preselected options, and cookie manipulation.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="en"
      className={`${display.variable} ${sans.variable} ${mono.variable}`}
    >
      <body className="min-h-screen bg-background font-sans text-foreground">
        {/* Ambient orbs — fixed, very low opacity, large blur. Mobile sizes
            stay smaller for performance; the atmosphere survives either way. */}
        <div aria-hidden className="pointer-events-none fixed inset-0 z-0 overflow-hidden">
          <div className="absolute -top-40 left-1/2 h-[400px] w-[400px] -translate-x-1/2 rounded-full bg-accent/[0.05] blur-[120px] md:h-[600px] md:w-[600px]" />
          <div className="absolute -bottom-40 -right-32 h-[400px] w-[400px] rounded-full bg-accent/[0.04] blur-[140px] md:h-[600px] md:w-[600px]" />
        </div>

        <div className="relative z-10 flex min-h-screen flex-col">
          <header className="sticky top-0 z-20 border-b border-border bg-background/70 backdrop-blur-xl">
            <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4 md:px-8 lg:px-12">
              <Link
                href="/"
                className="group flex items-center gap-2.5 transition-opacity hover:opacity-90 focus-visible:outline-none"
              >
                <span className="grid h-8 w-8 place-items-center rounded-md bg-accent font-display text-sm font-bold text-accent-foreground shadow-glow-sm transition-shadow duration-200 group-hover:shadow-glow-md">
                  D
                </span>
                <span className="font-display text-lg font-semibold tracking-tight text-foreground">
                  DeceptiTech
                </span>
              </Link>
              <nav className="hidden items-center gap-1 md:flex" aria-label="Primary">
                <NavLink href="/">New scan</NavLink>
                <NavLink href="/history">History</NavLink>
              </nav>
              {/* Mobile: just History link; "New scan" is the home page */}
              <Link
                href="/history"
                className="rounded-md px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-white/5 hover:text-foreground md:hidden"
              >
                History
              </Link>
            </div>
          </header>
          <main className="mx-auto w-full max-w-6xl flex-1 px-6 py-16 md:px-8 md:py-20 lg:px-12 lg:py-24">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}

function NavLink({ href, children }: { href: string; children: React.ReactNode }) {
  return (
    <Link
      href={href}
      className="rounded-md px-3 py-2 text-sm text-muted-foreground transition-colors duration-150 hover:bg-white/5 hover:text-foreground focus-visible:text-accent focus-visible:outline-none"
    >
      {children}
    </Link>
  );
}
