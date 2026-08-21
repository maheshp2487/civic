"use client";
import { useEffect, useState, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import {
  sendMessage,
  uploadDocument,
  submitIntake,
  CaseResponse,
} from "@/lib/api";
import ConversationFeed from "@/components/ConversationFeed";
import LegalAssessmentPanel from "@/components/SituationPanel";
import {
  Plus,
  Briefcase,
  Users,
  Settings,
  MoreHorizontal,
  CheckCircle2,
} from "lucide-react";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

interface UploadedDoc {
  name: string;
  size: string;
  status: "parsed" | "uploaded";
  detail: string;
}

interface HistoryCase {
  id: string;
  title: string;
  date: string;
}

/* ─────────────────────────────────────────────────────
   Helpers
───────────────────────────────────────────────────── */
function formatDate(d: Date) {
  const now = new Date();
  const diff = now.getTime() - d.getTime();
  const day = 86400000;
  if (diff < day) return "Today";
  if (diff < 2 * day) return "Yesterday";
  return d.toLocaleDateString("en-IN", { day: "numeric", month: "short" });
}

function deriveTitle(data: CaseResponse | null, fallback = "New matter"): string {
  if (!data?.situation) return fallback;
  const s = data.situation;
  if (s.title && s.title !== "New Case") return s.title;
  if (s.subcategory) return s.subcategory;
  if (s.category) return s.category;
  return fallback;
}

/* ─────────────────────────────────────────────────────
   Sidebar
───────────────────────────────────────────────────── */
function Sidebar({
  currentId,
  currentTitle,
  history,
  onNewCase,
}: {
  currentId: string;
  currentTitle: string;
  history: HistoryCase[];
  onNewCase: () => void;
}) {
  const legalTopics = [
    "Landlord",
    "Employment",
    "Consumer",
    "Women's rights",
    "Property",
    "Family",
  ];

  return (
    <aside className="w-60 flex flex-col bg-sidebar h-full shrink-0 overflow-hidden">
      {/* Logo */}
      <div className="px-5 py-5 border-b border-border-sidebar">
        <Link href="/" className="flex items-center gap-2.5">
          <svg
            width="22"
            height="22"
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
            <span className="font-bold text-xs tracking-wide text-white uppercase">
              VidhiSetu
            </span>
            <span className="text-[8px] tracking-[0.16em] text-[#b8952a] font-semibold uppercase">
              Legal Navigation
            </span>
          </div>
        </Link>
      </div>

      {/* New matter button */}
      <div className="px-4 py-4">
        <button
          onClick={onNewCase}
          className="w-full flex items-center gap-2 px-3 py-2.5 bg-sidebar-btn hover:bg-sidebar-hover border border-border-sidebar rounded-lg text-xs font-semibold text-text-on-dark transition-colors"
        >
          <Plus className="w-3.5 h-3.5 text-[#b8952a]" />
          New legal matter
        </button>
      </div>

      {/* Case history */}
      <div className="px-4 flex-1 overflow-y-auto">
        <p className="text-[9px] font-bold tracking-[0.16em] text-[#4b5563] uppercase mb-2 px-1">
          Case History
        </p>
        <div className="space-y-0.5">
          {/* Current case — always first */}
          <SidebarCaseItem
            id={currentId}
            title={currentTitle}
            date="Today"
            active
          />

          {/* Historical cases from localStorage */}
          {history
            .filter((h) => h.id !== currentId)
            .map((h) => (
              <SidebarCaseItem
                key={h.id}
                id={h.id}
                title={h.title}
                date={h.date}
                active={false}
              />
            ))}
        </div>
      </div>

      {/* Legal topics */}
      <div className="px-4 pb-3 border-t border-border-sidebar pt-3">
        <p className="text-[9px] font-bold tracking-[0.16em] text-[#4b5563] uppercase mb-2 px-1">
          Legal topics
        </p>
        <div className="flex flex-wrap gap-1.5 px-1">
          {legalTopics.map((t) => (
            <span
              key={t}
              className="text-[10px] text-[#6b7280] hover:text-text-on-dark cursor-pointer transition-colors"
            >
              {t}
            </span>
          ))}
        </div>
      </div>

      {/* Settings */}
      <div className="px-4 pb-5 border-t border-border-sidebar pt-3">
        <button className="flex items-center gap-2 text-xs text-[#6b7280] hover:text-text-on-dark transition-colors">
          <Settings className="w-3.5 h-3.5" />
          Settings
        </button>
      </div>
    </aside>
  );
}

function SidebarCaseItem({
  id,
  title,
  date,
  active,
}: {
  id: string;
  title: string;
  date: string;
  active: boolean;
}) {
  const router = useRouter();
  return (
    <button
      onClick={() => !active && router.push(`/cases/${id}`)}
      className={`w-full text-left px-2.5 py-2 rounded-lg transition-colors ${
        active
          ? "bg-sidebar-active"
          : "hover:bg-sidebar-hover"
      }`}
    >
      <p
        className={`text-xs font-semibold leading-snug truncate ${
          active ? "text-white" : "text-[#9ca3af]"
        }`}
      >
        {title}
      </p>
      <p className="text-[10px] text-[#4b5563] mt-0.5">{date}</p>
    </button>
  );
}

/* ─────────────────────────────────────────────────────
   Main Page
───────────────────────────────────────────────────── */
export default function CasePage() {
  const { id } = useParams();
  const router = useRouter();
  const [data, setData] = useState<CaseResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [statusText, setStatusText] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [errorText, setErrorText] = useState("");
  const [uploadedDocs, setUploadedDocs] = useState<UploadedDoc[]>([]);
  const [history, setHistory] = useState<HistoryCase[]>([]);
  const hasInitialized = useRef(false);

  /* Load history from localStorage */
  useEffect(() => {
    try {
      const raw = localStorage.getItem("vs_case_history");
      if (raw) setHistory(JSON.parse(raw));
    } catch {
      /* ignore */
    }
  }, []);

  /* Persist current case to history when title becomes available */
  useEffect(() => {
    if (!data?.situation) return;
    const title = deriveTitle(data);
    const entry: HistoryCase = {
      id: id as string,
      title,
      date: formatDate(new Date()),
    };
    setHistory((prev) => {
      const filtered = prev.filter((h) => h.id !== id);
      const next = [entry, ...filtered].slice(0, 10);
      try {
        localStorage.setItem("vs_case_history", JSON.stringify(next));
      } catch {
        /* ignore */
      }
      return next;
    });
  }, [data?.situation?.category, data?.situation?.subcategory]);

  /* Initial message */
  useEffect(() => {
    if (hasInitialized.current) return;
    const initial = sessionStorage.getItem("initial_message");
    if (initial) {
      sessionStorage.removeItem("initial_message");
      hasInitialized.current = true;
      handleSendMessage(initial, true);
    }
  }, []);

  /* ── API Handlers ── */
  const handleSendMessage = async (content: string, isInitial = false) => {
    if (loading) return;
    setLoading(true);
    setStatusText("Understanding your situation...");
    setErrorText("");

    setMessages((prev) => [...prev, { role: "user", content }]);

    try {
      const res = await sendMessage(id as string, content);
      setData(res);

      let reply = "";
      if (res.output?.clarification_questions?.length) {
        reply = res.output.clarification_questions[0];
      } else if (res.workflow_state === "NEEDS_INTAKE") {
        reply = "I need a few more details to find the correct legal pathway.";
      } else if (res.output?.situation_summary && isInitial) {
        reply = res.output.situation_summary;
      } else if (res.output?.action_plan?.length) {
        reply =
          "I have analysed your situation and prepared a legal assessment. Please review it on the right panel.";
      }

      if (reply) {
        setMessages((prev) => [...prev, { role: "assistant", content: reply }]);
      }
    } catch (err) {
      const e = err as Error;
      setErrorText(
        e.message || "Error communicating with server. Please try again."
      );
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
      /* Add chip */
      const sizeKB = Math.round(file.size / 1024);
      setUploadedDocs((prev) => [
        ...prev,
        {
          name: file.name,
          size: `${sizeKB} KB`,
          status: "parsed",
          detail:
            file.type === "application/pdf"
              ? "Parsed · no conflict"
              : `Uploaded · ${sizeKB > 500 ? Math.round(sizeKB / 100) * 100 : sizeKB} KB`,
        },
      ]);
    } catch (err) {
      const e = err as Error;
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

    const summary = Object.entries(values)
      .filter(
        ([_, v]) =>
          v &&
          v.trim() !== "" &&
          v.toLowerCase() !== "no" &&
          v.toLowerCase() !== "none"
      )
      .map(([k, v]) => {
        const field = data?.intake_form?.fields.find((f) => f.id === k);
        const label = field
          ? field.label.replace(" *", "")
          : k.split("__").pop()?.replace(/_/g, " ") || k;
        return `• ${label}\n  ↳ ${v}`;
      })
      .join("\n\n");

    setMessages((prev) => [
      ...prev,
      { role: "user", content: `I have provided the additional details:\n${summary}` },
    ]);

    try {
      const res = await submitIntake(id as string, values);
      setData(res);

      let reply = "";
      if (res.output?.action_plan?.length) {
        reply =
          "I have analysed your complete situation and prepared a legal assessment. Please review it on the right panel.";
      }
      if (reply) {
        setMessages((prev) => [...prev, { role: "assistant", content: reply }]);
      }
    } catch (err) {
      const e = err as Error;
      setErrorText(e.message || "Error submitting form. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleNewCase = async () => {
    try {
      await fetch("http://127.0.0.1:8001/api/v1/cases/reset", {
        method: "POST",
      });
    } catch {
      /* ignore */
    }
    router.push("/");
  };

  /* ── Derived values ── */
  const caseTitle = deriveTitle(data, "New matter");
  const isComplete = data?.workflow_state === "READY" && data?.output?.action_plan?.length;

  const jurisdiction = data?.situation?.jurisdiction
    ? [data.situation.jurisdiction.state].filter(Boolean).join(", ") || "India"
    : "India";

  return (
    <div className="flex h-screen w-full overflow-hidden bg-page">

      {/* ── LEFT: Dark Sidebar ── */}
      <Sidebar
        currentId={id as string}
        currentTitle={caseTitle}
        history={history}
        onNewCase={handleNewCase}
      />

      {/* ── MAIN WORKSPACE AREA + FULL BOTTOM FOOTER ── */}
      <div className="flex-1 flex flex-col h-full min-w-0 overflow-hidden">

        {/* 2-COLUMN PANELS (Centre Conversation + Right Legal Assessment) */}
        <div className="flex-1 flex flex-row min-h-0 overflow-hidden">

          {/* ── CENTRE: Conversation ── */}
          <div className="flex-1 flex flex-col h-full min-w-0 bg-surface border-r border-border-subtle overflow-hidden">

            {/* Centre header */}
            <div className="px-6 py-4 border-b border-border-subtle flex items-start justify-between shrink-0">
              <div>
                <h1 className="text-base font-bold text-text-primary leading-tight">
                  {caseTitle}
                </h1>
                <p className="text-xs text-text-muted mt-0.5">
                  Case workspace · {jurisdiction}
                </p>
              </div>
              {/* Status badge */}
              {isComplete ? (
                <div className="flex items-center gap-1.5 px-3 py-1.5 bg-page border border-border-subtle rounded-lg text-[10px] font-semibold text-text-secondary shrink-0">
                  <CheckCircle2 className="w-3.5 h-3.5 text-success-text" />
                  Evidence review complete
                </div>
              ) : null}
            </div>

            {/* Tell us what happened — sub-header */}
            <div className="px-6 pt-4 pb-0 shrink-0">
              <p className="text-sm font-semibold text-text-primary mb-0.5">
                Tell us what happened
              </p>
              <p className="text-xs text-text-muted">
                Describe the situation in your own words. VidhiSetu will identify the relevant facts before suggesting a legal pathway.
              </p>
              <div className="mt-4 border-t border-border-subtle" />
            </div>

            {/* Scrollable conversation */}
            <div className="flex-1 flex flex-col min-h-0 overflow-hidden">
              <ConversationFeed
                data={data}
                loading={loading}
                statusText={statusText}
                errorText={errorText}
                messages={messages}
                uploadedDocs={uploadedDocs}
                onSendMessage={handleSendMessage}
                onFileUpload={handleFileUpload}
                onIntakeSubmit={handleIntakeSubmit}
              />
            </div>
          </div>

          {/* ── RIGHT: Legal Assessment ── */}
          <aside className="w-80 xl:w-96 bg-surface shrink-0 flex flex-col h-full border-l border-border-subtle overflow-hidden">
            {/* Right header */}
            <div className="px-5 py-4 border-b border-border-subtle flex items-start justify-between shrink-0">
              <div>
                <h2 className="text-sm font-bold text-text-primary">
                  Legal assessment
                </h2>
                <p className="text-[10px] text-text-muted mt-0.5">
                  Grounded findings from the facts and retrieved sources
                </p>
              </div>
              <button className="p-1 text-text-muted hover:text-text-primary transition-colors rounded-md hover:bg-surface-hover">
                <MoreHorizontal className="w-4 h-4" />
              </button>
            </div>

            {/* Right scrollable content */}
            <div className="flex-1 overflow-y-auto px-5 py-5 min-h-0">
              <LegalAssessmentPanel data={data} />
            </div>
          </aside>
        </div>

        {/* ── FULL-WIDTH BOTTOM DISCLAIMER FOOTER ── */}
        <footer className="w-full px-6 py-2.5 bg-[#191c27] border-t border-[#2e3247] shrink-0 z-20 flex items-center gap-3">
          <span className="text-[9px] font-bold tracking-[0.18em] text-[#b8952a] uppercase shrink-0">
            DISCLAIMER
          </span>
          <p className="text-[10px] text-[#9ca3af] leading-tight">
            VidhiSetu provides legal information and navigation support, not legal representation or a substitute for a qualified lawyer. Always verify the applicable law and facts before taking action.
          </p>
        </footer>
      </div>
    </div>
  );
}
