"use client";
import { useEffect, useState, useRef } from "react";
import { useParams } from "next/navigation";
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
        .map(([k, v]) => `${k.replace(/_/g, ' ')}: ${v}`)
        .join(", ");
        
    setMessages(prev => [...prev, { role: "user", content: `[Form Submitted] ${summary}` }]);
    
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
    } catch (err) {
      const e = err as Error;
      console.warn("Reset Failed:", e.message);
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-[#ededed] flex flex-col md:flex-row relative">
      <button 
        onClick={handleReset} 
        className="absolute top-4 right-4 z-50 px-3 py-1 bg-neutral-900 border border-neutral-800 text-neutral-500 hover:text-white rounded text-xs opacity-50 hover:opacity-100 transition-opacity"
      >
        Demo Reset
      </button>

      {/* Left / Main: Conversation */}
      <div className="w-full md:w-1/2 lg:w-5/12 flex flex-col border-b md:border-b-0 md:border-r border-neutral-800">
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
      </div>

      {/* Right: Situation and Pathway */}
      <div className="w-full md:w-1/2 lg:w-7/12 flex flex-col overflow-y-auto">
        <div className="p-6 md:p-10 space-y-12">
          <SituationPanel data={data} />
          <PathwayPanel data={data} />
        </div>
      </div>
    </div>
  );
}
