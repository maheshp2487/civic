"use client";
import { useState, useEffect, useRef } from "react";
import { CaseResponse } from "@/lib/api";
import {
  Send,
  Paperclip,
  AlertCircle,
  AlertTriangle,
  File,
  X,
  Loader2,
} from "lucide-react";
import { ChatMessage } from "@/app/cases/[id]/page";

interface UploadedDoc {
  name: string;
  size: string;
  status: "parsed" | "uploaded";
  detail: string;
}

interface Props {
  data: CaseResponse | null;
  loading: boolean;
  statusText: string;
  errorText?: string;
  messages: ChatMessage[];
  uploadedDocs: UploadedDoc[];
  onSendMessage: (msg: string) => void;
  onFileUpload: (file: File) => void;
  onIntakeSubmit: (values: Record<string, string>) => void;
}

export default function ConversationFeed({
  data,
  loading,
  statusText,
  errorText,
  messages,
  uploadedDocs,
  onSendMessage,
  onFileUpload,
  onIntakeSubmit,
}: Props) {
  const [input, setInput] = useState("");
  const [intakeValues, setIntakeValues] = useState<Record<string, string>>({});
  const chatScrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (
      data?.workflow_state === "NEEDS_INTAKE" &&
      data?.intake_form
    ) {
      setIntakeValues({});
    }
  }, [data?.intake_form, data?.workflow_state]);

  // When a user message or initial prompt is added, ensure the view starts at the TOP so the prompt is visible
  useEffect(() => {
    if (messages.length > 0) {
      if (messages.length <= 2) {
        // Initial user prompt and first response: keep scrolled to the top
        chatScrollRef.current?.scrollTo({ top: 0, behavior: "smooth" });
      }
    }
  }, [messages]);

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
      const missing = data.intake_form.fields.filter(
        (f) => f.required && (!intakeValues[f.id] || !intakeValues[f.id].trim())
      );
      if (missing.length > 0) {
        alert(
          `Please fill required fields: ${missing
            .map((f) => f.label.replace(" *", ""))
            .join(", ")}`
        );
        return;
      }
    }
    onIntakeSubmit(intakeValues);
  };

  const unresolvedConflicts =
    data?.situation?.conflicts?.filter(
      (c) => c.resolution_status === "Unresolved"
    ) || [];

  /* ── Case detail pills from situation ── */
  const sit = data?.situation;
  const dateVal =
    sit?.dates && sit.dates.length > 0 ? sit.dates[0] : null;
  const locationVal = sit?.jurisdiction
    ? [sit.jurisdiction.district, sit.jurisdiction.state]
        .filter(Boolean)
        .join(", ")
    : null;
  const caseTypeVal = sit?.subcategory || sit?.category || null;

  return (
    <div className="flex-1 flex flex-col h-full w-full bg-surface min-h-0 relative overflow-hidden">

      {/* ── ERROR BANNER ── */}
      {errorText && (
        <div className="mx-5 mt-4 p-3.5 bg-error-bg border border-error-border rounded-xl flex items-start gap-3 text-sm shrink-0">
          <AlertCircle className="w-4 h-4 text-error-text shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold text-error-text">Unable to continue</p>
            <p className="text-error-text mt-0.5">{errorText}</p>
          </div>
        </div>
      )}

      {/* ── MESSAGES AREA ── */}
      <div ref={chatScrollRef} className="flex-1 overflow-y-auto px-6 pt-5 pb-6 space-y-5 min-h-0">

        {/* Case Details Row — appears once situation is known */}
        {sit && (
          <div className="mb-1">
            <p className="text-[10px] font-bold tracking-[0.14em] text-text-muted uppercase mb-3">
              Case Details
            </p>
            <div className="flex flex-wrap gap-3">
              <CaseDetailPill label="When did it happen?" value={dateVal} />
              <CaseDetailPill label="Case type" value={caseTypeVal} isDropdown />
              <CaseDetailPill label="Location" value={locationVal} />
            </div>
          </div>
        )}

        {/* Empty state */}
        {!data && !loading && (
          <div className="flex flex-col items-center justify-center h-full text-text-muted space-y-3 py-16 opacity-60">
            <Send className="w-8 h-8" />
            <p className="text-sm font-medium text-center">
              Describe your situation to begin.
            </p>
          </div>
        )}

        {/* Label for YOUR ACCOUNT messages */}
        {messages.length > 0 && (
          <p className="text-[10px] font-bold tracking-[0.14em] text-text-muted uppercase">
            Your Account
          </p>
        )}

        {/* Chat messages */}
        {messages.map((msg, i) => {
          if (msg.role === "user") {
            return (
              <div key={i} className="flex justify-end">
                <div className="bg-bubble-user text-bubble-user-text rounded-2xl rounded-br-sm px-4 py-3 max-w-[82%] text-sm leading-relaxed whitespace-pre-wrap">
                  {msg.content}
                </div>
              </div>
            );
          }
          return (
            <div key={i} className="flex flex-col gap-1">
              <p className="text-[10px] font-bold tracking-[0.14em] text-[#b8952a] uppercase">
                Vidhisetu
              </p>
              <div className="text-sm text-text-secondary leading-relaxed whitespace-pre-wrap max-w-[90%]">
                {msg.content}
              </div>
            </div>
          );
        })}

        {/* Conflict resolution */}
        {unresolvedConflicts.map((c, i) => (
          <div
            key={i}
            className="bg-error-bg border border-error-border rounded-xl p-5 space-y-4"
          >
            <div className="flex items-center gap-2 text-error-text font-semibold text-sm">
              <AlertTriangle className="w-4 h-4" />
              <span>We found a difference in the facts</span>
            </div>
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="p-3 bg-surface rounded-lg border border-border-subtle">
                <div className="text-text-muted mb-1 font-semibold uppercase tracking-wide">
                  Your message
                </div>
                <div className="font-medium text-text-primary">{c.user_value}</div>
              </div>
              <div className="p-3 bg-surface rounded-lg border border-border-subtle">
                <div className="text-text-muted mb-1 font-semibold uppercase tracking-wide">
                  {c.document_source}
                </div>
                <div className="font-medium text-text-primary">
                  {c.document_value}
                </div>
              </div>
            </div>
            <div>
              <p className="text-xs text-text-secondary font-medium mb-2">
                Which value is correct?
              </p>
              <div className="flex flex-wrap gap-2">
                {[c.user_value, c.document_value, "Neither"].map((opt) => (
                  <button
                    key={opt}
                    onClick={() => onSendMessage(opt)}
                    className="px-4 py-2 bg-surface hover:bg-surface-hover border border-border-subtle rounded-lg text-xs font-medium transition-colors text-text-primary"
                  >
                    {opt}
                  </button>
                ))}
              </div>
            </div>
          </div>
        ))}

        {/* Intake Form */}
        {data?.workflow_state === "NEEDS_INTAKE" && data.intake_form && (
          <div className="bg-surface border border-border-subtle rounded-xl p-5 mt-2 shadow-sm">
            <h3 className="text-sm font-semibold text-text-primary mb-1">
              {data.intake_form.title}
            </h3>
            <p className="text-xs text-text-secondary mb-5">
              We need a few more details to assess your situation accurately.
            </p>
            <form onSubmit={handleIntakeFormSubmit} className="space-y-4">
              {data.intake_form.fields.map((f) => (
                <div key={f.id} className="flex flex-col gap-1.5">
                  <label className="text-xs font-semibold text-text-primary">
                    {f.label}{" "}
                    {f.required && (
                      <span className="text-error-text">*</span>
                    )}
                  </label>
                  {f.type === "select" ? (
                    <select
                      required={f.required}
                      value={intakeValues[f.id] || ""}
                      onChange={(e) =>
                        setIntakeValues({
                          ...intakeValues,
                          [f.id]: e.target.value,
                        })
                      }
                      className="bg-page border border-border-strong rounded-lg px-3 py-2.5 text-xs text-text-primary focus:ring-2 focus:ring-[#b8952a]/30 outline-none transition-all"
                    >
                      <option value="">Select an option...</option>
                      {f.options?.map((o) => (
                        <option key={o} value={o}>
                          {o}
                        </option>
                      ))}
                    </select>
                  ) : f.type === "radio" || f.type === "checkbox" ? (
                    <div className="flex flex-wrap gap-3 bg-page p-3 rounded-lg border border-border-subtle">
                      {f.options?.map((o) => (
                        <label
                          key={o}
                          className="flex items-center gap-2 text-xs text-text-secondary cursor-pointer hover:text-text-primary transition-colors"
                        >
                          <input
                            type={f.type}
                            name={f.id}
                            value={o}
                            checked={
                              f.type === "checkbox"
                                ? intakeValues[f.id]
                                    ?.split(",")
                                    .includes(o)
                                : intakeValues[f.id] === o
                            }
                            onChange={(e) => {
                              if (f.type === "checkbox") {
                                const cur = intakeValues[f.id]
                                  ? intakeValues[f.id].split(",")
                                  : [];
                                setIntakeValues({
                                  ...intakeValues,
                                  [f.id]: e.target.checked
                                    ? [...cur, o].join(",")
                                    : cur.filter((v) => v !== o).join(","),
                                });
                              } else {
                                setIntakeValues({
                                  ...intakeValues,
                                  [f.id]: o,
                                });
                              }
                            }}
                            className="w-3.5 h-3.5 accent-[#111827]"
                          />
                          {o}
                        </label>
                      ))}
                    </div>
                  ) : (
                    <input
                      type={f.type}
                      required={f.required}
                      placeholder={f.placeholder || "Your answer..."}
                      value={intakeValues[f.id] || ""}
                      onChange={(e) =>
                        setIntakeValues({
                          ...intakeValues,
                          [f.id]: e.target.value,
                        })
                      }
                      className="bg-page border border-border-strong rounded-lg px-3.5 py-2.5 text-xs text-text-primary placeholder:text-text-muted focus:ring-2 focus:ring-[#b8952a]/30 focus:border-[#b8952a]/50 outline-none transition-all"
                    />
                  )}
                </div>
              ))}
              <div className="pt-3 flex justify-end">
                <button
                  type="submit"
                  disabled={loading}
                  className="px-6 py-2.5 bg-text-primary hover:bg-accent-hover text-white text-xs font-semibold rounded-lg transition-colors disabled:opacity-50"
                >
                  Continue →
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Loading indicator */}
        {loading && (
          <div className="flex items-center gap-2 text-text-muted py-2">
            <Loader2 className="w-3.5 h-3.5 animate-spin text-[#b8952a]" />
            <span className="text-xs font-medium">{statusText}</span>
          </div>
        )}
      </div>

      {/* ── DOCUMENTS & EVIDENCE ── */}
      {uploadedDocs.length > 0 && (
        <div className="px-6 py-3 border-t border-border-subtle shrink-0">
          <p className="text-[10px] font-bold tracking-[0.14em] text-text-muted uppercase mb-2.5">
            Documents &amp; Evidence
          </p>
          <div className="flex flex-wrap gap-2">
            {uploadedDocs.map((doc, i) => (
              <div
                key={i}
                className="flex items-center gap-2 px-3 py-2 bg-page border border-border-subtle rounded-lg text-xs"
              >
                <File className="w-3.5 h-3.5 text-[#b8952a] shrink-0" />
                <div className="min-w-0">
                  <p className="font-medium text-text-primary truncate max-w-[120px]">
                    {doc.name}
                  </p>
                  <p className="text-text-muted">{doc.detail}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── COMPOSER (LIFTED) ── */}
      <div className="px-6 pt-3 pb-8 border-t border-border-subtle shrink-0 bg-surface shadow-[0_-2px_10px_rgba(0,0,0,0.02)]">
        <form
          onSubmit={handleSubmit}
          className="flex items-end gap-2.5 bg-page rounded-xl border border-border-subtle px-3.5 py-2.5 shadow-sm focus-within:ring-2 focus-within:ring-[#b8952a]/20 focus-within:border-[#b8952a]/40 transition-all"
        >
          {/* File upload */}
          <label
            className="p-1.5 text-text-muted hover:text-text-primary cursor-pointer transition-colors rounded-lg hover:bg-surface-hover shrink-0 self-center"
            title="Attach document"
          >
            <input
              type="file"
              className="hidden"
              accept="image/jpeg,image/png,application/pdf"
              onChange={(e) =>
                e.target.files && onFileUpload(e.target.files[0])
              }
              disabled={loading}
            />
            <Paperclip className="w-4 h-4" />
          </label>

          {/* Text input */}
          <textarea
            value={input}
            onChange={(e) => {
              setInput(e.target.value);
              e.target.style.height = "auto";
              e.target.style.height = `${Math.min(e.target.scrollHeight, 120)}px`;
            }}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                if (input.trim() && !loading) {
                  onSendMessage(input);
                  setInput("");
                }
              }
            }}
            disabled={loading}
            placeholder="Add more details or ask a follow-up question..."
            rows={1}
            className="flex-1 bg-transparent border-none resize-none focus:outline-none text-sm text-text-primary placeholder:text-text-muted py-1.5 max-h-[120px]"
            style={{ height: "36px" }}
          />

          {/* Send button */}
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="p-2.5 bg-text-primary hover:bg-accent-hover text-white rounded-lg transition-all disabled:opacity-40 shrink-0 self-end"
          >
            {loading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </button>
        </form>
        <p className="text-[10px] text-text-muted mt-2 text-center">
          Your information is used to understand this matter and retrieve relevant sources.
        </p>
      </div>
    </div>
  );
}

/* Small helper component */
function CaseDetailPill({
  label,
  value,
  isDropdown = false,
}: {
  label: string;
  value: string | null;
  isDropdown?: boolean;
}) {
  return (
    <div className="flex flex-col gap-0.5">
      <span className="text-[9px] font-semibold tracking-wider text-text-muted uppercase">
        {label}
      </span>
      <div className="bg-page border border-border-subtle rounded-lg px-3 py-2 text-xs text-text-primary font-medium flex items-center gap-1">
        {value ?? <span className="text-text-muted">—</span>}
        {isDropdown && (
          <svg
            className="w-3 h-3 text-text-muted ml-0.5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 9l-7 7-7-7"
            />
          </svg>
        )}
      </div>
    </div>
  );
}
