import { useState, useEffect } from "react";
import { CaseResponse } from "@/lib/api";
import { Send, Paperclip, AlertTriangle } from "lucide-react";
import { ChatMessage } from "@/app/cases/[id]/page";

interface Props {
  data: CaseResponse | null;
  loading: boolean;
  statusText: string;
  errorText?: string;
  messages: ChatMessage[];
  onSendMessage: (msg: string) => void;
  onFileUpload: (file: File) => void;
  onIntakeSubmit: (values: Record<string, string>) => void;
}

export default function ConversationFeed({ data, loading, statusText, errorText, messages, onSendMessage, onFileUpload, onIntakeSubmit }: Props) {
  const [input, setInput] = useState("");
  const [intakeValues, setIntakeValues] = useState<Record<string, string>>({});

  // Reset intake form when new one arrives
  useEffect(() => {
    if (data?.workflow_state === "NEEDS_INTAKE" && data?.intake_form) {
      setIntakeValues({});
    }
  }, [data?.intake_form]);

  // Handle form submit

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;
    onSendMessage(input);
    setInput("");
  };

  const handleIntakeFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (loading) return;
    
    if (data?.intake_form) {
      const missingFields = data.intake_form.fields.filter(
        f => f.required && (!intakeValues[f.id] || !intakeValues[f.id].trim())
      );
      if (missingFields.length > 0) {
        alert(`Please fill out all required fields. Missing: ${missingFields.map(f => f.label.replace(' *', '')).join(", ")}`);
        return;
      }
    }
    
    onIntakeSubmit(intakeValues);
  };

  const unresolvedConflicts = data?.situation?.conflicts?.filter(c => c.resolution_status === "Unresolved") || [];
  
  // Show only the first clarification question to make it interactive step-by-step
  const activeQuestion = data?.output?.clarification_questions?.[0];

  return (
    <div className="flex flex-col h-[50vh] md:h-screen">
      <div className="p-6 border-b border-neutral-800 flex items-center justify-between bg-[#0a0a0a] shrink-0">
        <h2 className="font-semibold text-lg tracking-tight">Conversation</h2>
        {loading && <span className="text-sm text-indigo-400 animate-pulse font-medium">{statusText}</span>}
      </div>
      
      {errorText && (
        <div className="mx-6 mt-4 p-4 bg-red-950/30 border border-red-900/50 rounded-xl text-red-400 text-sm flex items-center gap-2">
          <AlertTriangle className="w-4 h-4" />
          {errorText}
        </div>
      )}
      
      <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-[#0a0a0a]">
        {!data && !loading && (
          <div className="text-neutral-500 text-center mt-10">Start by explaining your situation.</div>
        )}
        
        {data && data.output?.situation_summary && (
          <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-4 text-neutral-300 leading-relaxed shadow-sm">
            {data.output.situation_summary}
          </div>
        )}
        
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`${
              msg.role === 'user' 
                ? 'bg-indigo-600 text-white' 
                : 'bg-indigo-950/20 border border-indigo-900/50 text-indigo-200'
              } rounded-xl p-4 max-w-[85%] leading-relaxed shadow-sm`}
            >
              {msg.content}
            </div>
          </div>
        ))}

        {unresolvedConflicts.map((c, i) => (
          <div key={i} className="bg-amber-950/10 border border-amber-900/50 rounded-xl p-5 space-y-5">
            <div className="flex items-center gap-2 text-amber-500 font-medium">
              <AlertTriangle className="w-5 h-5" />
              <span>We found a difference</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
              <div className="p-4 bg-neutral-900/50 rounded-lg">
                <div className="text-neutral-500 mb-1 font-medium">Your message:</div>
                <div className="font-medium text-white text-base">{c.user_value}</div>
              </div>
              <div className="p-4 bg-neutral-900/50 rounded-lg border border-neutral-800">
                <div className="text-neutral-500 mb-1 font-medium">{c.document_source}:</div>
                <div className="font-medium text-white text-base">{c.document_value}</div>
              </div>
            </div>
            <div className="pt-2">
              <div className="text-neutral-400 text-sm mb-3">Which value is correct?</div>
              <div className="flex flex-wrap gap-2">
                <button onClick={() => onSendMessage(c.user_value)} className="px-5 py-2.5 bg-neutral-800 hover:bg-neutral-700 rounded-lg text-sm font-medium transition-colors">
                  {c.user_value}
                </button>
                <button onClick={() => onSendMessage(c.document_value)} className="px-5 py-2.5 bg-neutral-800 hover:bg-neutral-700 rounded-lg text-sm font-medium transition-colors">
                  {c.document_value}
                </button>
                <button onClick={() => onSendMessage("Neither")} className="px-5 py-2.5 bg-transparent border border-neutral-700 hover:bg-neutral-800 rounded-lg text-sm font-medium transition-colors text-neutral-400">
                  Neither / Check again
                </button>
              </div>
            </div>
          </div>
        ))}
        
        {data?.workflow_state === "NEEDS_INTAKE" && data.intake_form && (
          <div className="bg-indigo-950/10 border border-indigo-900/50 rounded-xl p-5 shadow-sm mt-4">
            <h3 className="text-indigo-400 font-semibold mb-4">{data.intake_form.title}</h3>
            <form onSubmit={handleIntakeFormSubmit} className="space-y-4">
              {data.intake_form.fields.map(f => (
                <div key={f.id} className="flex flex-col">
                  <label className="text-sm text-neutral-300 font-medium mb-1">{f.label} {f.required && <span className="text-red-400">*</span>}</label>
                  {f.type === "select" ? (
                    <select 
                      required={f.required}
                      value={intakeValues[f.id] || ""}
                      onChange={e => setIntakeValues({...intakeValues, [f.id]: e.target.value})}
                      className="bg-neutral-900 border border-neutral-700 rounded-lg px-3 py-2 text-white focus:ring-1 focus:ring-indigo-500"
                    >
                      <option value="">Select an option...</option>
                      {f.options?.map(o => <option key={o} value={o}>{o}</option>)}
                    </select>
                  ) : f.type === "radio" || f.type === "checkbox" ? (
                    <div className="flex flex-wrap gap-4 mt-1">
                      {f.options?.map(o => (
                        <label key={o} className="flex items-center gap-2 text-sm text-neutral-300 cursor-pointer">
                          <input 
                            type={f.type} 
                            name={f.id} 
                            value={o}
                            checked={f.type === "checkbox" ? intakeValues[f.id]?.split(',').includes(o) : intakeValues[f.id] === o}
                            onChange={(e) => {
                              if (f.type === "checkbox") {
                                const current = intakeValues[f.id] ? intakeValues[f.id].split(',') : [];
                                if (e.target.checked) {
                                  setIntakeValues({...intakeValues, [f.id]: [...current, o].join(',')});
                                } else {
                                  setIntakeValues({...intakeValues, [f.id]: current.filter(val => val !== o).join(',')});
                                }
                              } else {
                                setIntakeValues({...intakeValues, [f.id]: o});
                              }
                            }}
                            className="bg-neutral-900 border-neutral-700 text-indigo-500 rounded focus:ring-indigo-500"
                          />
                          {o}
                        </label>
                      ))}
                    </div>
                  ) : (
                    <input 
                      type={f.type}
                      required={f.required}
                      placeholder={f.placeholder}
                      value={intakeValues[f.id] || ""}
                      onChange={e => setIntakeValues({...intakeValues, [f.id]: e.target.value})}
                      className="bg-neutral-900 border border-neutral-700 rounded-lg px-3 py-2 text-white focus:ring-1 focus:ring-indigo-500 placeholder-neutral-600"
                    />
                  )}
                </div>
              ))}
              <div className="pt-2">
                <button type="submit" disabled={loading} className="w-full sm:w-auto px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-medium rounded-lg transition-colors">
                  Submit Details
                </button>
              </div>
            </form>
          </div>
        )}
      </div>

      <div className="p-4 bg-[#0a0a0a] border-t border-neutral-800 shrink-0">
        <form onSubmit={handleSubmit} className="relative flex items-center gap-2">
          <label className="p-3 text-neutral-400 hover:text-white cursor-pointer transition-colors rounded-xl hover:bg-neutral-900">
            <input type="file" className="hidden" accept="image/jpeg,image/png,application/pdf" onChange={(e) => e.target.files && onFileUpload(e.target.files[0])} disabled={loading}/>
            <Paperclip className="w-5 h-5" />
          </label>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
            placeholder="Type your message..."
            className="flex-1 bg-neutral-900 border border-neutral-800 rounded-xl px-4 py-3 focus:outline-none focus:ring-1 focus:ring-indigo-500 text-white placeholder-neutral-500 shadow-sm"
          />
          <button type="submit" disabled={loading || !input.trim()} className="p-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl transition-colors disabled:opacity-50 shadow-sm">
            <Send className="w-5 h-5" />
          </button>
        </form>
      </div>
    </div>
  );
}
