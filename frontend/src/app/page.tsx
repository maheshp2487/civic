"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowRight, Scale, FileText, CheckCircle, Navigation, ShieldCheck } from "lucide-react";
import { Footer } from "@/components/Footer";

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

  return (
    <div className="flex-1 w-full">
      {/* HERO SECTION */}
      <section className="relative w-full py-24 md:py-32 overflow-hidden bg-page">
        {/* Abstract Background Elements */}
        <div className="absolute top-0 right-0 -mr-20 -mt-20 w-[40rem] h-[40rem] bg-accent-primary/5 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-0 -ml-20 -mb-20 w-[30rem] h-[30rem] bg-accent-primary/10 rounded-full blur-3xl pointer-events-none" />
        
        <div className="container mx-auto px-6 relative z-10">
          <div className="max-w-4xl mx-auto text-center space-y-8">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-surface border border-border-subtle text-accent-primary text-sm font-medium mb-4 shadow-sm">
              <ShieldCheck className="w-4 h-4" />
              <span>Safe, Official Legal Navigation</span>
            </div>
            
            <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-text-primary leading-tight">
              Navigate your legal situation <span className="text-accent-primary">with clarity.</span>
            </h1>
            
            <p className="text-xl text-text-secondary max-w-2xl mx-auto leading-relaxed">
              Tell us what happened. We&apos;ll help you understand your legal context, identify relevant evidence, and map out your next steps safely.
            </p>

            <form onSubmit={handleSubmit} className="mt-12 max-w-2xl mx-auto relative group">
              <div className="absolute -inset-1 bg-gradient-to-r from-accent-primary/50 to-accent-primary/20 rounded-2xl blur opacity-25 group-focus-within:opacity-50 transition duration-500" />
              <div className="relative">
                <textarea
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  placeholder="e.g. My landlord refused to return my ₹30,000 deposit in Pune..."
                  className="w-full h-40 md:h-48 p-6 bg-surface border border-border-subtle rounded-2xl resize-none focus:outline-none focus:ring-2 focus:ring-accent-primary/50 text-lg shadow-xl text-text-primary placeholder:text-text-muted transition-all"
                  required
                />
                <button
                  type="submit"
                  className="absolute bottom-6 right-6 bg-accent-primary hover:bg-accent-hover text-white px-6 py-3 rounded-xl flex items-center gap-2 transition-all font-medium disabled:opacity-50 disabled:cursor-not-allowed shadow-md"
                  disabled={!text.trim()}
                >
                  Start a Case <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </form>
          </div>
        </div>
      </section>

      {/* HOW IT WORKS SECTION */}
      <section className="w-full py-24 bg-surface border-t border-border-subtle">
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-text-primary mb-4">How it works</h2>
            <p className="text-text-secondary max-w-2xl mx-auto">A simple, transparent process to understand your legal standing without the confusion.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 max-w-6xl mx-auto">
            {/* Step 1 */}
            <div className="bg-page border border-border-subtle p-8 rounded-2xl relative overflow-hidden group hover:border-accent-primary/50 transition-colors">
              <div className="text-6xl font-black text-text-muted absolute top-4 right-6 opacity-25 group-hover:text-accent-primary group-hover:opacity-20 transition-colors">01</div>
              <div className="w-12 h-12 bg-surface border border-border-subtle rounded-xl flex items-center justify-center text-accent-primary mb-6 shadow-sm relative z-10">
                <FileText className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-semibold text-text-primary mb-3">Describe your situation</h3>
              <p className="text-text-secondary text-sm leading-relaxed">Tell us what happened in plain language. You don&apos;t need to know the legal terms.</p>
            </div>

            {/* Step 2 */}
            <div className="bg-page border border-border-subtle p-8 rounded-2xl relative overflow-hidden group hover:border-accent-primary/50 transition-colors">
              <div className="text-6xl font-black text-text-muted absolute top-4 right-6 opacity-25 group-hover:text-accent-primary group-hover:opacity-20 transition-colors">02</div>
              <div className="w-12 h-12 bg-surface border border-border-subtle rounded-xl flex items-center justify-center text-accent-primary mb-6 shadow-sm relative z-10">
                <CheckCircle className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-semibold text-text-primary mb-3">Answer questions</h3>
              <p className="text-text-secondary text-sm leading-relaxed">We may ask a few targeted questions to gather the exact details needed for a legal assessment.</p>
            </div>

            {/* Step 3 */}
            <div className="bg-page border border-border-subtle p-8 rounded-2xl relative overflow-hidden group hover:border-accent-primary/50 transition-colors">
              <div className="text-6xl font-black text-text-muted absolute top-4 right-6 opacity-25 group-hover:text-accent-primary group-hover:opacity-20 transition-colors">03</div>
              <div className="w-12 h-12 bg-surface border border-border-subtle rounded-xl flex items-center justify-center text-accent-primary mb-6 shadow-sm relative z-10">
                <Scale className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-semibold text-text-primary mb-3">Review information</h3>
              <p className="text-text-secondary text-sm leading-relaxed">We match your facts against official legal sources and present the relevant information clearly.</p>
            </div>

            {/* Step 4 */}
            <div className="bg-page border border-border-subtle p-8 rounded-2xl relative overflow-hidden group hover:border-accent-primary/50 transition-colors">
              <div className="text-6xl font-black text-text-muted absolute top-4 right-6 opacity-25 group-hover:text-accent-primary group-hover:opacity-20 transition-colors">04</div>
              <div className="w-12 h-12 bg-surface border border-border-subtle rounded-xl flex items-center justify-center text-accent-primary mb-6 shadow-sm relative z-10">
                <Navigation className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-semibold text-text-primary mb-3">Understand next steps</h3>
              <p className="text-text-secondary text-sm leading-relaxed">Receive a clear, actionable pathway and links to official legal aid resources if you qualify.</p>
            </div>
          </div>
        </div>
      </section>
      
      <Footer />
    </div>
  );
}
