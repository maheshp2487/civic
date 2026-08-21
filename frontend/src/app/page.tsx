"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { FileText, CheckCircle, Scale, ArrowUpRight } from "lucide-react";

/* ────────────────────────────────────────────────────────────
   Inline Nav — uses router inside the same client component
───────────────────────────────────────────────────────────── */
function LandingNav({ onNewCase }: { onNewCase: () => void }) {
  return (
    <header className="w-full px-8 py-4 flex items-center justify-between bg-page shrink-0">
      {/* Logo */}
      <Link href="/" className="flex items-center gap-2.5">
        <svg
          width="28"
          height="28"
          viewBox="0 0 28 28"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="text-[#b8952a]"
        >
          <rect x="4" y="8" width="4" height="16" rx="1" fill="currentColor" opacity="0.8" />
          <rect x="12" y="4" width="4" height="20" rx="1" fill="currentColor" />
          <rect x="20" y="8" width="4" height="16" rx="1" fill="currentColor" opacity="0.8" />
          <rect x="2" y="6" width="24" height="2.5" rx="1" fill="currentColor" />
        </svg>
        <div className="flex flex-col leading-none">
          <span className="font-bold text-base tracking-wide text-text-primary">
            VidhiSetu
          </span>
          <span className="text-[9px] tracking-[0.18em] text-[#b8952a] font-semibold uppercase">
            Legal Navigation
          </span>
        </div>
      </Link>

      {/* Centre links */}
      <nav className="hidden md:flex items-center gap-8">
        <a
          href="#how-it-works"
          className="text-sm text-text-secondary hover:text-text-primary transition-colors font-medium text-center leading-tight"
        >
          How it<br />works
        </a>
        <a
          href="#safety"
          className="text-sm text-text-secondary hover:text-text-primary transition-colors font-medium"
        >
          Safety
        </a>
        <a
          href="#privacy"
          className="text-sm text-text-secondary hover:text-text-primary transition-colors font-medium"
        >
          Privacy
        </a>
      </nav>

      {/* CTA */}
      <button
        onClick={onNewCase}
        className="px-5 py-2.5 bg-text-primary text-white text-sm font-semibold rounded-lg hover:bg-accent-hover transition-colors shadow-sm"
      >
        New Case
      </button>
    </header>
  );
}

/* ────────────────────────────────────────────────────────────
   Main Page
───────────────────────────────────────────────────────────── */
export default function Home() {
  const [text, setText] = useState("");
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim()) return;
    const caseId = crypto.randomUUID();
    sessionStorage.setItem("initial_message", text);
    router.push(`/cases/${caseId}`);
  };

  const handleNewCase = () => {
    router.push("/");
  };

  return (
    <div className="w-full bg-page">
      <LandingNav onNewCase={handleNewCase} />

      {/* ── HERO ── */}
      <section className="flex flex-col items-center justify-center px-6 pt-16 pb-20">
        {/* Badge */}
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-border-subtle bg-surface text-[#b8952a] text-xs font-semibold tracking-widest uppercase mb-10 shadow-sm">
          <span>✦</span>
          Safe, Official Legal Navigation
        </div>

        {/* Headline */}
        <h1 className="text-4xl md:text-5xl lg:text-[3.5rem] font-black text-text-primary text-center leading-tight tracking-tight max-w-3xl mb-5">
          Navigate your legal situation
          <br />
          with clarity.
        </h1>

        {/* Subtext */}
        <p className="text-sm text-text-secondary text-center max-w-xl leading-relaxed mb-10">
          Understand what happened, identify the relevant legal context,
          <br className="hidden sm:block" />
          and find a grounded path forward — without needing legal terminology.
        </p>

        {/* Input Card */}
        <div className="w-full max-w-2xl bg-surface rounded-2xl border border-border-subtle shadow-sm p-6">
          <p className="text-sm font-semibold text-text-primary mb-1">
            Tell us what happened
          </p>
          <p className="text-xs text-text-muted mb-4">
            Describe your situation in plain language. You do not need to know the legal terms.
          </p>
          <form onSubmit={handleSubmit} className="flex items-center gap-3">
            <input
              type="text"
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="e.g. My landlord refused to return my ₹30,000 deposit in Pune..."
              className="flex-1 bg-page border border-border-subtle rounded-lg px-4 py-3 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-[#b8952a]/30 focus:border-[#b8952a]/50 transition-all"
            />
            <button
              type="submit"
              disabled={!text.trim()}
              className="shrink-0 px-5 py-3 bg-text-primary hover:bg-accent-hover text-white text-sm font-semibold rounded-lg transition-colors disabled:opacity-40 disabled:cursor-not-allowed whitespace-nowrap"
            >
              Start a Case →
            </button>
          </form>
        </div>

        {/* Feature tags */}
        <p className="mt-6 text-xs text-text-muted tracking-wide">
          Facts first · Official sources · Clear next steps · Legal-aid routing
        </p>
      </section>

      {/* ── HOW IT WORKS ── */}
      <section id="how-it-works" className="bg-surface border-t border-border-subtle py-20 px-6">
        <div className="max-w-5xl mx-auto">
          {/* Section heading */}
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-text-primary mb-3">How it works</h2>
            <p className="text-sm text-text-secondary max-w-lg mx-auto">
              A simple, transparent process to understand your legal standing without the confusion.
            </p>
            <div className="mt-5 mx-auto w-12 h-0.5 bg-[#b8952a] rounded-full" />
          </div>

          {/* Cards grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            {[
              {
                num: "01",
                Icon: FileText,
                title: "Describe your situation",
                desc: "Tell us what happened in plain language. You do not need to know the legal terms.",
              },
              {
                num: "02",
                Icon: CheckCircle,
                title: "Answer targeted questions",
                desc: "We may ask a few focused questions to establish the exact details needed for assessment.",
              },
              {
                num: "03",
                Icon: Scale,
                title: "Review information",
                desc: "Your facts are matched against relevant official legal sources and presented clearly.",
              },
              {
                num: "04",
                Icon: ArrowUpRight,
                title: "Understand next steps",
                desc: "Receive a clear, actionable pathway and links to official legal-aid resources where relevant.",
              },
            ].map(({ num, Icon, title, desc }) => (
              <div
                key={num}
                className="relative bg-page border border-border-subtle rounded-2xl p-6 overflow-hidden group hover:border-[#b8952a]/30 transition-colors"
              >
                {/* Step number (top-right, faded) */}
                <span className="absolute top-4 right-5 text-5xl font-black text-text-muted/20 select-none group-hover:text-[#b8952a]/15 transition-colors">
                  {num}
                </span>

                {/* Icon box */}
                <div className="w-10 h-10 bg-surface border border-border-subtle rounded-xl flex items-center justify-center text-text-secondary mb-5 relative z-10">
                  <Icon className="w-4.5 h-4.5" strokeWidth={1.5} />
                </div>

                <h3 className="font-semibold text-text-primary text-sm mb-2">{title}</h3>
                <p className="text-xs text-text-secondary leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── FOOTER ── */}
      <footer className="bg-[#191c27] text-white px-8 pt-12 pb-5">
        <div className="max-w-6xl mx-auto">
          <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-10">
            {/* Left */}
            <div className="max-w-md">
              <p className="text-[10px] font-bold tracking-[0.18em] text-[#b8952a] uppercase mb-3">
                Built for Legal Clarity
              </p>
              <h3 className="text-xl font-bold text-white leading-snug">
                Structured understanding. Evidence-aware review.
                <br />
                Grounded explanations with traceable official sources.
              </h3>
            </div>

            {/* Right */}
            <div className="text-right">
              <p className="text-[10px] tracking-[0.15em] text-[#6b7280] uppercase mb-1">
                Jurisdiction · India
              </p>
              <p className="text-sm text-[#9ca3af]">Citation-first navigation</p>
            </div>
          </div>

          {/* Disclaimer strip */}
          <div className="mt-10 pt-4 border-t border-[#2e3247] flex items-center gap-4">
            <span className="text-[9px] font-bold tracking-[0.18em] text-[#b8952a] uppercase shrink-0">
              Disclaimer
            </span>
            <p className="text-[10px] text-[#6b7280] leading-relaxed">
              VidhiSetu provides legal information and navigation support, not legal representation or a substitute for a qualified lawyer. Always verify the applicable law and facts before taking action.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
