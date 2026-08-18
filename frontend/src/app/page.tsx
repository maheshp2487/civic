"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowRight, Scale } from "lucide-react";

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
    <main className="min-h-screen flex flex-col items-center justify-center p-6 bg-[#0a0a0a] text-[#ededed]">
      <div className="absolute top-6 left-6 flex items-center gap-2 text-indigo-400 font-medium">
        <Scale className="w-5 h-5" />
        <span>InnoAi Legal Navigation</span>
      </div>

      <div className="max-w-3xl w-full space-y-8 text-center mt-[-10vh]">
        <h1 className="text-5xl md:text-6xl font-semibold tracking-tight text-white leading-tight">
          Tell us what happened.
        </h1>
        <p className="text-xl text-neutral-400 max-w-2xl mx-auto">
          We'll help you understand the situation, find relevant official information, identify useful evidence, and plan your next steps.
        </p>

        <form onSubmit={handleSubmit} className="relative mt-12 max-w-2xl mx-auto">
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="e.g. My landlord refused to return my ₹30,000 deposit in Pune..."
            className="w-full h-48 p-5 bg-neutral-900 border border-neutral-800 rounded-2xl resize-none focus:outline-none focus:ring-1 focus:ring-indigo-500 text-lg shadow-xl"
            required
          />
          <button
            type="submit"
            className="absolute bottom-5 right-5 bg-indigo-600 hover:bg-indigo-500 text-white px-5 py-2.5 rounded-xl flex items-center gap-2 transition-all font-medium disabled:opacity-50"
            disabled={!text.trim()}
          >
            Start Pathway <ArrowRight className="w-4 h-4" />
          </button>
        </form>
      </div>
    </main>
  );
}
