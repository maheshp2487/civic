"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { sendMessage, uploadDocument, CaseResponse } from "@/lib/api";
import ConversationFeed from "@/components/ConversationFeed";
import SituationPanel from "@/components/SituationPanel";
import PathwayPanel from "@/components/PathwayPanel";

export default function CasePage() {
  const { id } = useParams();
  const [data, setData] = useState<CaseResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [statusText, setStatusText] = useState("");
  
  useEffect(() => {
    const initialMessage = sessionStorage.getItem("initial_message");
    if (initialMessage) {
      sessionStorage.removeItem("initial_message");
      handleSendMessage(initialMessage);
    }
  }, []);

  const [errorText, setErrorText] = useState("");

  const handleSendMessage = async (content: string) => {
    setLoading(true);
    setStatusText("Understanding your situation...");
    setErrorText("");
    try {
      const res = await sendMessage(id as string, content);
      setData(res);
    } catch (e) {
      console.error(e);
      setErrorText("Error communicating with server. Please try again.");
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
    } catch (e) {
      console.error(e);
      setErrorText("Error processing document. Please check the file and try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleReset = async () => {
    try {
      await fetch("http://127.0.0.1:8000/api/v1/cases/reset", { method: "POST" });
      setData(null);
      setStatusText("");
    } catch (e) {
      console.error(e);
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
          onSendMessage={handleSendMessage}
          onFileUpload={handleFileUpload}
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
