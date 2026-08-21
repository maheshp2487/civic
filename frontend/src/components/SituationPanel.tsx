import { CaseResponse } from "@/lib/api";
import { ExternalLink, CheckCircle2, ShieldCheck } from "lucide-react";

export default function LegalAssessmentPanel({
  data,
}: {
  data: CaseResponse | null;
}) {
  const out = data?.output;
  const sit = data?.situation;

  /* ── Nothing to show yet ── */
  if (!data || (!sit && !out)) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-text-muted py-16 opacity-50">
        <ShieldCheck className="w-8 h-8 mb-3" />
        <p className="text-xs text-center font-medium">
          Legal assessment will appear here once your situation is analysed.
        </p>
      </div>
    );
  }

  const hasSources =
    out?.source_citations && out.source_citations.length > 0;
  const hasPathway =
    out?.action_plan && out.action_plan.length > 0;
  const allVerified = hasSources;

  return (
    <div className="space-y-6">

      {/* ── CURRENT UNDERSTANDING ── */}
      {out?.situation_summary && (
        <div>
          <p className="text-[10px] font-bold tracking-[0.14em] text-text-muted uppercase mb-2.5">
            Current Understanding
          </p>
          <div className="bg-panel-dark rounded-xl p-4">
            <p className="text-panel-dark-text text-sm leading-relaxed">
              {out.situation_summary}
            </p>
          </div>
        </div>
      )}

      {/* Also show situation facts if no summary yet */}
      {!out?.situation_summary && sit && (
        <div>
          <p className="text-[10px] font-bold tracking-[0.14em] text-text-muted uppercase mb-2.5">
            Current Understanding
          </p>
          <div className="bg-panel-dark rounded-xl p-4">
            <p className="text-panel-dark-text text-sm leading-relaxed">
              {sit.category}
              {sit.subcategory ? ` — ${sit.subcategory}` : ""}
              {sit.jurisdiction?.state
                ? `. Jurisdiction: ${sit.jurisdiction.district ? `${sit.jurisdiction.district}, ` : ""}${sit.jurisdiction.state}`
                : ""}
              .
            </p>
          </div>
        </div>
      )}

      {/* ── MISSING CONTEXT ── */}
      {sit?.missing_information && sit.missing_information.length > 0 && (
        <div className="p-4 bg-error-bg border border-error-border rounded-xl">
          <p className="text-xs font-semibold text-error-text mb-2 flex items-center gap-1.5">
            Missing Context
          </p>
          <ul className="list-disc pl-4 text-xs text-error-text/90 space-y-1">
            {sit.missing_information.map((m, i) => (
              <li key={i}>{m}</li>
            ))}
          </ul>
        </div>
      )}

      {/* ── RELEVANT LEGAL SOURCES ── */}
      {hasSources && (
        <div>
          <h3 className="text-sm font-semibold text-text-primary mb-3">
            Relevant legal sources
          </h3>
          <div className="space-y-3">
            {out!.source_citations.map((cite, i) => (
              <div
                key={i}
                className="border border-border-subtle rounded-xl p-4 bg-surface hover:border-[#b8952a]/30 transition-colors"
              >
                {/* Act title */}
                <p className="text-sm font-semibold text-text-primary mb-0.5">
                  {cite.title}
                </p>

                {/* Section — gold link */}
                {cite.section && (
                  <p className="text-xs text-[#b8952a] font-medium mb-2">
                    {cite.section}
                  </p>
                )}

                {/* Description / verified info matched to this source */}
                {out?.verified_information && out.verified_information[i] && (
                  <p className="text-xs text-text-secondary leading-relaxed mb-3">
                    {out.verified_information[i]}
                  </p>
                )}

                {/* Source URL */}
                <div className="flex items-center gap-3 pt-2 border-t border-border-subtle">
                  {cite.url ? (
                    <a
                      href={cite.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1.5 text-[10px] font-semibold text-text-secondary hover:text-[#b8952a] transition-colors"
                    >
                      <span className="underline underline-offset-2">
                        {new URL(cite.url).hostname}
                      </span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  ) : null}
                  <div className="flex items-center gap-1 text-[10px] text-success-text font-semibold">
                    <CheckCircle2 className="w-3 h-3" />
                    Verified source
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── SUGGESTED LEGAL PATHWAY ── */}
      {hasPathway && (
        <div>
          <h3 className="text-sm font-semibold text-text-primary mb-3">
            Suggested legal pathway
          </h3>
          <div className="space-y-3">
            {out!.action_plan.map((step, i) => (
              <div key={i} className="flex items-start gap-3">
                {/* Numbered circle — dark */}
                <div className="w-7 h-7 rounded-full bg-text-primary text-white flex items-center justify-center shrink-0 text-[10px] font-bold mt-0.5">
                  {String(step.step).padStart(2, "0")}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-text-primary leading-snug">
                    {step.action_type}
                  </p>
                  <p className="text-xs text-text-secondary leading-relaxed mt-0.5">
                    {step.description}
                  </p>
                  {step.limitation && (
                    <p className="text-[10px] text-text-muted mt-1 italic">
                      {step.limitation}
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── LEGAL AID RESOURCES ── */}
      {out?.legal_aid_resources && out.legal_aid_resources.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-text-primary mb-3">
            Official Legal Assistance
          </h3>
          <div className="space-y-3">
            {out.legal_aid_resources.map((res, i) => (
              <div
                key={i}
                className="border border-border-subtle rounded-xl p-4 bg-surface relative overflow-hidden"
              >
                <div className="absolute top-0 left-0 w-0.5 h-full bg-[#b8952a]" />
                <p className="text-sm font-bold text-text-primary">
                  {res.name}
                </p>
                <p className="text-[10px] text-[#b8952a] font-semibold uppercase tracking-wide mt-0.5 mb-2">
                  {res.level} Authority
                </p>
                <p className="text-xs text-text-secondary leading-relaxed mb-3">
                  {res.description}
                </p>
                <div className="flex flex-wrap gap-2">
                  <a
                    href={res.official_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-3 py-1.5 bg-text-primary hover:bg-accent-hover text-white text-[10px] font-semibold rounded-lg transition-colors"
                  >
                    Visit Official Site
                  </a>
                  <span className="px-3 py-1.5 bg-page border border-border-subtle text-[10px] font-medium text-text-primary rounded-lg">
                    {res.contact_info}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── CITATION STATUS ── */}
      {allVerified && (
        <div className="flex items-center justify-between pt-3 border-t border-border-subtle">
          <p className="text-[10px] font-bold tracking-[0.14em] text-text-muted uppercase">
            Citation Status
          </p>
          <div className="flex items-center gap-1.5 text-[10px] font-semibold text-success-text">
            <CheckCircle2 className="w-3 h-3" />
            All displayed sources verified
          </div>
        </div>
      )}

      {/* Disclaimer */}
      {out?.disclaimer && (
        <p className="text-[10px] text-text-muted leading-relaxed">
          {out.disclaimer}
        </p>
      )}
    </div>
  );
}
