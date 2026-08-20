import { useState, useEffect, useRef } from "react";
import { CaseResponse } from "@/lib/api";
import { Send, Paperclip, AlertTriangle, AlertCircle, RefreshCcw } from "lucide-react";
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
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (data?.workflow_state === "NEEDS_INTAKE" && data?.intake_form) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setIntakeValues({});
    }
  }, [data?.intake_form, data?.workflow_state]);

  // Smooth scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, data?.intake_form, data?.output?.clarification_questions]);

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

  return (
    <div className="flex-1 flex flex-col h-full w-full bg-page relative">
      {/* HEADER */}
      <div className="px-6 py-4 border-b border-border-subtle flex items-center justify-between bg-surface/90 backdrop-blur shrink-0 z-10 shadow-sm">
        <h2 className="font-semibold text-lg tracking-tight text-text-primary">Conversation</h2>
      </div>
      
      {/* ERROR UI */}
      {errorText && (
        <div className="mx-6 mt-4 p-4 bg-error-bg border border-error-border rounded-xl flex items-start gap-3 shadow-sm animate-in slide-in-from-top-2">
          <AlertCircle className="w-5 h-5 text-error-text shrink-0 mt-0.5" />
          <div className="flex-1">
            <h3 className="text-sm font-semibold text-error-text mb-1">Unable to continue</h3>
            <p className="text-error-text text-sm leading-relaxed">{errorText}</p>
          </div>
        </div>
      )}
      
      {/* MESSAGES AREA */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {!data && !loading && (
          <div className="flex flex-col items-center justify-center h-full text-text-muted space-y-4 opacity-50">
            <Send className="w-12 h-12" />
            <p className="text-center font-medium">Start by explaining your situation below.</p>
          </div>
        )}
        
        {data && data.output?.situation_summary && (
          <div className="bg-surface border border-border-subtle rounded-xl p-5 text-text-secondary leading-relaxed shadow-sm">
            {data.output.situation_summary}
          </div>
        )}
        
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`${
              msg.role === 'user' 
                ? 'bg-accent-primary text-text-on-accent shadow-md rounded-br-sm' 
                : 'bg-surface border border-border-subtle text-text-primary shadow-sm rounded-bl-sm'
              } rounded-2xl p-4 max-w-[85%] md:max-w-[75%] leading-relaxed text-sm md:text-base whitespace-pre-wrap`}
            >
              {msg.content}
            </div>
          </div>
        ))}

        {unresolvedConflicts.map((c, i) => (
          <div key={i} className="bg-error-bg border border-error-border rounded-xl p-5 space-y-5 shadow-sm">
            <div className="flex items-center gap-2 text-error-text font-semibold">
              <AlertTriangle className="w-5 h-5" />
              <span>We found a difference in the facts</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
              <div className="p-4 bg-surface rounded-lg border border-border-subtle">
                <div className="text-text-muted mb-1 font-medium text-xs uppercase tracking-wider">Your message:</div>
                <div className="font-medium text-text-primary text-base">{c.user_value}</div>
              </div>
              <div className="p-4 bg-surface rounded-lg border border-border-subtle">
                <div className="text-text-muted mb-1 font-medium text-xs uppercase tracking-wider">{c.document_source}:</div>
                <div className="font-medium text-text-primary text-base">{c.document_value}</div>
              </div>
            </div>
            <div className="pt-2">
              <div className="text-text-secondary text-sm mb-3 font-medium">Which value is correct?</div>
              <div className="flex flex-wrap gap-2">
                <button onClick={() => onSendMessage(c.user_value)} className="px-5 py-2.5 bg-surface hover:bg-surface-hover border border-border-subtle rounded-lg text-sm font-medium transition-colors text-text-primary shadow-sm">
                  {c.user_value}
                </button>
                <button onClick={() => onSendMessage(c.document_value)} className="px-5 py-2.5 bg-surface hover:bg-surface-hover border border-border-subtle rounded-lg text-sm font-medium transition-colors text-text-primary shadow-sm">
                  {c.document_value}
                </button>
                <button onClick={() => onSendMessage("Neither")} className="px-5 py-2.5 bg-transparent border border-border-strong hover:bg-surface-hover rounded-lg text-sm font-medium transition-colors text-text-secondary">
                  Neither / Check again
                </button>
              </div>
            </div>
          </div>
        ))}
        
        {data?.workflow_state === "NEEDS_INTAKE" && data.intake_form && (
          <div className="bg-surface border border-border-subtle rounded-xl p-6 md:p-8 shadow-md mt-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="mb-6 pb-4 border-b border-border-subtle">
              <h3 className="text-xl font-semibold text-text-primary tracking-tight">{data.intake_form.title}</h3>
              <p className="text-text-secondary text-sm mt-1">We need a few more details to understand your situation accurately.</p>
            </div>
            
            <form onSubmit={handleIntakeFormSubmit} className="space-y-6">
              <div className="grid grid-cols-1 gap-6">
                {data.intake_form.fields.map(f => (
                  <div key={f.id} className="flex flex-col">
                    <label className="text-sm text-text-primary font-semibold mb-2">{f.label} {f.required && <span className="text-error-text ml-1">*</span>}</label>
                    {f.type === "select" ? (
                      <select 
                        required={f.required}
                        value={intakeValues[f.id] || ""}
                        onChange={e => setIntakeValues({...intakeValues, [f.id]: e.target.value})}
                        className="bg-page border border-border-strong rounded-lg px-4 py-3 text-text-primary focus:ring-2 focus:ring-accent-primary/50 focus:border-accent-primary outline-none transition-all shadow-sm"
                      >
                        <option value="">Select an option...</option>
                        {f.options?.map(o => <option key={o} value={o}>{o}</option>)}
                      </select>
                    ) : f.type === "radio" || f.type === "checkbox" ? (
                      <div className="flex flex-wrap gap-4 mt-1 bg-page p-4 rounded-lg border border-border-subtle">
                        {f.options?.map(o => (
                          <label key={o} className="flex items-center gap-3 text-sm text-text-secondary font-medium cursor-pointer hover:text-text-primary transition-colors">
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
                              className="w-4 h-4 text-accent-primary border-border-strong focus:ring-accent-primary/50 cursor-pointer"
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
                        className="bg-page border border-border-strong rounded-lg px-4 py-3 text-text-primary focus:ring-2 focus:ring-accent-primary/50 focus:border-accent-primary outline-none placeholder:text-text-muted transition-all shadow-sm"
                      />
                    )}
                  </div>
                ))}
              </div>
              <div className="pt-6 mt-6 border-t border-border-subtle flex justify-end">
                <button type="submit" disabled={loading} className="w-full sm:w-auto px-8 py-3 bg-accent-primary hover:bg-accent-hover text-white font-medium rounded-xl transition-all shadow-md disabled:opacity-50">
                  Continue &rarr;
                </button>
              </div>
            </form>
          </div>
        )}
        
        {loading && (
          <div className="flex items-center gap-2 text-text-muted animate-pulse">
            <RefreshCcw className="w-4 h-4 animate-spin text-accent-primary" />
            <span className="text-sm font-medium">{statusText}</span>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* COMPOSER */}
      <div className="p-4 md:p-6 bg-surface border-t border-border-subtle shrink-0 shadow-lg relative z-20">
        <form onSubmit={handleSubmit} className="relative flex items-center gap-3 max-w-4xl mx-auto">
          <label className="p-3 text-text-muted hover:text-accent-primary cursor-pointer transition-colors rounded-xl hover:bg-surface-hover border border-transparent hover:border-border-subtle group" title="Upload Document">
            <input type="file" className="hidden" accept="image/jpeg,image/png,application/pdf" onChange={(e) => e.target.files && onFileUpload(e.target.files[0])} disabled={loading}/>
            <Paperclip className="w-5 h-5 group-hover:scale-110 transition-transform" />
          </label>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
            placeholder="Reply to continue the conversation..."
            className="flex-1 bg-page border border-border-strong rounded-xl px-5 py-3.5 focus:outline-none focus:ring-2 focus:ring-accent-primary/50 focus:border-accent-primary text-text-primary placeholder:text-text-muted shadow-sm transition-all text-sm md:text-base"
          />
          <button type="submit" disabled={loading || !input.trim()} className="p-3.5 bg-accent-primary hover:bg-accent-hover text-white rounded-xl transition-all disabled:opacity-50 shadow-md group">
            <Send className="w-5 h-5 group-hover:-translate-y-0.5 group-hover:translate-x-0.5 transition-transform" />
          </button>
        </form>
      </div>
    </div>
  );
}
