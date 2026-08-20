"use client";
import { useEffect, useState, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import { sendMessage, uploadDocument, submitIntake, CaseResponse } from "@/lib/api";
import ConversationFeed from "@/components/ConversationFeed";
import SituationPanel from "@/components/SituationPanel";
import PathwayPanel from "@/components/PathwayPanel";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export default function CasePage() {
  const { id } = useParams();
  const router = useRouter();
  const [data, setData] = useState<CaseResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [statusText, setStatusText] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const hasInitialized = useRef(false);
  
  useEffect(() => {
    if (hasInitialized.current) return;
    const initialMessage = sessionStorage.getItem("initial_message");
    if (initialMessage) {
      sessionStorage.removeItem("initial_message");
      hasInitialized.current = true;
      handleSendMessage(initialMessage, true);
    }
  }, []);

  const [errorText, setErrorText] = useState("");

  const handleSendMessage = async (content: string, isInitial = false) => {
    if (loading) return; // Prevent duplicate concurrent requests
    setLoading(true);
    setStatusText("Understanding your situation...");
    setErrorText("");
    
    setMessages(prev => [...prev, { role: "user", content }]);
    
    try {
      const res = await sendMessage(id as string, content);
      setData(res);
      
      let assistantReply = "";
      if (res.output?.clarification_questions?.length) {
        assistantReply = res.output.clarification_questions[0];
      } else if (res.output?.situation_summary && isInitial) {
        assistantReply = res.output.situation_summary;
      } else if (res.output?.action_plan?.length) {
        assistantReply = "I have analyzed your situation and prepared a legal pathway. Please review it on the right panel.";
      }

      if (assistantReply) {
        setMessages(prev => [...prev, { role: "assistant", content: assistantReply }]);
      }
    } catch (err) {
      const e = err as Error;
      console.warn("API Request Failed:", e.message);
      setErrorText(e.message || "Error communicating with server. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (file: File) => {
    setLoading(true);
    setStatusText("Processing document...");
    setErrorText("");
    try {
      const res = await uploadDocument(id as string, file);
      setData(res);
    } catch (err) {
      const e = err as Error;
      console.warn("Document Upload Failed:", e.message);
      setErrorText("Error processing document. Please check the file and try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleIntakeSubmit = async (values: Record<string, string>) => {
    if (loading) return;
    setLoading(true);
    setStatusText("Processing your details...");
    setErrorText("");
    
    // Convert structured values to a display string for the chat history
    const summary = Object.entries(values)
        .filter(([_, v]) => v && v.trim() !== "" && v.toLowerCase() !== "no" && v.toLowerCase() !== "none")
        .map(([k, v]) => {
          const field = data?.intake_form?.fields.find(f => f.id === k);
          const label = field ? field.label.replace(' *', '') : k.split('__').pop()?.replace(/_/g, ' ') || k;
          return `• ${label}\n  ↳ ${v}`;
        })
        .join("\n\n");
        
    setMessages(prev => [...prev, { role: "user", content: `I have provided the additional details:\n${summary}` }]);
    
    try {
      const res = await submitIntake(id as string, values);
      setData(res);
      
      let assistantReply = "";
      if (res.output?.action_plan?.length) {
        assistantReply = "I have analyzed your complete situation and prepared a legal pathway. Please review it on the right panel.";
      }

      if (assistantReply) {
        setMessages(prev => [...prev, { role: "assistant", content: assistantReply }]);
      }
    } catch (err) {
      const e = err as Error;
      console.warn("Intake Submit Failed:", e.message);
      setErrorText(e.message || "Error submitting form. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleReset = async () => {
    try {
      await fetch("http://127.0.0.1:8001/api/v1/cases/reset", { method: "POST" });
      setData(null);
      setMessages([]);
      setStatusText("");
      router.push("/"); // Redirect to home
    } catch (err) {
      const e = err as Error;
      console.warn("Reset Failed:", e.message);
    }
  };

  return (
    <div className="flex-1 flex flex-col lg:flex-row w-full h-full overflow-hidden bg-page">
      {/* 3-ZONE LAYOUT */}

      {/* LEFT ZONE: Case Sidebar (Hidden on mobile, small on desktop) */}
      <aside className="hidden lg:flex flex-col w-64 border-r border-border-subtle bg-surface p-6 shrink-0 z-10">
        <div className="mb-8">
          <h2 className="text-sm font-bold tracking-wider text-text-muted uppercase">Case Workspace</h2>
          <div className="mt-3">
            <span 
              className="inline-block text-xs font-medium text-text-secondary bg-surface-hover px-2.5 py-1.5 rounded-md border border-border-subtle truncate max-w-full"
              title={data?.situation?.title || "New Case"}
            >
              {data?.situation?.title || "New Case"}
            </span>
          </div>
        </div>
        
        <div className="mt-auto space-y-4">
          <div className="p-4 bg-accent-primary-muted/20 border border-accent-primary-muted rounded-xl">
            <h3 className="text-xs font-semibold text-accent-primary mb-1">Secure Session</h3>
            <p className="text-xs text-text-secondary leading-relaxed">Your data is processed securely and is not stored permanently.</p>
          </div>
          <button 
            onClick={handleReset} 
            className="w-full px-4 py-2.5 bg-surface hover:bg-surface-hover border border-border-subtle text-status-error-text rounded-xl text-sm font-medium transition-colors shadow-sm"
          >
            End & Reset Case
          </button>
        </div>
      </aside>

      {/* CENTER ZONE: Conversation (Takes remaining space, prioritized) */}
      <section className="flex-1 flex flex-col h-full bg-page relative min-w-0 lg:border-r border-border-subtle">
        <ConversationFeed 
          data={data} 
          loading={loading} 
          statusText={statusText}
          errorText={errorText}
          messages={messages}
          onSendMessage={handleSendMessage}
          onFileUpload={handleFileUpload}
          onIntakeSubmit={handleIntakeSubmit}
        />
      </section>

      {/* RIGHT ZONE: Evidence & Action Plan (Stacks below chat on mobile, side panel on desktop) */}
      <aside className="w-full lg:w-[26rem] xl:w-[30rem] bg-surface/50 shrink-0 overflow-y-auto overflow-x-hidden h-[50vh] lg:h-full border-t lg:border-t-0 border-border-subtle">
        <div className="p-6 md:p-8 space-y-8">
          <div className="lg:hidden flex items-center justify-between mb-2">
            <h2 className="text-lg font-semibold text-text-primary">Case Analysis</h2>
            <button onClick={handleReset} className="text-xs font-medium text-status-error-text px-3 py-1.5 border border-status-error-border rounded-lg bg-surface">Reset</button>
          </div>
          <SituationPanel data={data} />
          <PathwayPanel data={data} />
        </div>
      </aside>
    </div>
  );
}
