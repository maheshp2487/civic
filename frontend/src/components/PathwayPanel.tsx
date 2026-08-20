import { CaseResponse } from "@/lib/api";
import { CheckCircle2, FileText, Info, ShieldAlert, ExternalLink } from "lucide-react";

export default function PathwayPanel({ data }: { data: CaseResponse | null }) {
  if (!data || !data.output) return null;
  const out = data.output;

  if (!out.action_plan.length && !out.verified_information.length && !out.evidence_checklist.length) {
    return null;
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-700">
      <div className="border-b border-border-subtle pb-4">
        <h2 className="text-2xl font-bold tracking-tight text-text-primary">Your Legal Pathway</h2>
      </div>

      {out.verified_information.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-xs font-bold text-text-muted uppercase tracking-wider">Verified Information</h3>
          <div className="space-y-3">
            {out.verified_information.map((info, i) => (
              <div key={i} className="p-5 bg-surface border border-border-subtle rounded-xl flex gap-4 text-sm shadow-sm transition-all hover:border-accent-primary/50 hover:shadow-md">
                <Info className="w-5 h-5 text-accent-primary shrink-0 mt-0.5" />
                <span className="text-text-primary leading-relaxed font-medium">{info}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {out.evidence_checklist.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-xs font-bold text-text-muted uppercase tracking-wider">Evidence to Collect</h3>
          <div className="grid grid-cols-1 gap-4">
            {out.evidence_checklist.map((item, i) => (
              <div key={i} className="flex items-start gap-4 p-5 bg-surface rounded-xl border border-border-subtle shadow-sm transition-all hover:border-accent-primary/50">
                <div className="p-2 bg-surface-hover rounded-lg shrink-0">
                  <FileText className="w-5 h-5 text-text-secondary" />
                </div>
                <div>
                  <div className="font-semibold text-text-primary">{item.type}</div>
                  <div className="text-text-secondary text-sm mt-1 leading-relaxed">{item.description}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {out.action_plan.length > 0 && (
        <div className="space-y-4 pt-4">
          <h3 className="text-xs font-bold text-text-muted uppercase tracking-wider">Your Next Steps</h3>
          <div className="space-y-6 relative before:absolute before:inset-0 before:ml-6 before:-translate-x-px before:h-full before:w-0.5 before:bg-border-subtle">
            {out.action_plan.map((action, i) => (
              <div key={i} className="relative flex items-start gap-5">
                <div className="w-12 h-12 rounded-full bg-page border-2 border-accent-primary flex items-center justify-center shrink-0 z-10 text-accent-primary font-bold shadow-sm">
                  {action.step}
                </div>
                <div className="bg-surface border border-border-subtle rounded-xl p-6 flex-1 min-w-0 shadow-sm transition-all hover:border-accent-primary/50">
                  <div className="font-bold text-text-primary mb-2 text-lg">{action.action_type}</div>
                  <div className="text-text-secondary text-sm leading-relaxed">{action.description}</div>
                  
                  {action.basis_source_ids && action.basis_source_ids.length > 0 && (
                    <div className="mt-5 pt-4 border-t border-border-subtle flex flex-col gap-2">
                      <span className="text-xs font-semibold uppercase tracking-wider text-text-muted">Sources</span>
                      <div className="flex flex-wrap gap-2">
                        {action.basis_source_ids.map(id => {
                          const cite = out.source_citations.find(c => c.chunk_id === id);
                          if (!cite) return null;
                          
                          const inner = (
                            <>
                              <CheckCircle2 className="w-3.5 h-3.5 text-success-text shrink-0" />
                              <span className="truncate flex-1 min-w-0" title={cite.title}>{cite.title}</span> 
                              {cite.section && <span className="text-text-muted shrink-0 truncate max-w-[120px]" title={cite.section}>· {cite.section}</span>}
                              {cite.url && <ExternalLink className="w-3 h-3 text-text-muted ml-1 shrink-0" />}
                            </>
                          );

                          return cite.url ? (
                            <a 
                              key={id} 
                              href={cite.url} 
                              target="_blank" 
                              rel="noopener noreferrer" 
                              className="bg-page px-3 py-1.5 rounded-lg border border-border-strong text-xs font-medium text-text-primary flex items-center gap-2 hover:bg-surface-hover hover:border-accent-primary/50 hover:text-accent-primary transition-colors group cursor-pointer max-w-full"
                            >
                              {inner}
                            </a>
                          ) : (
                            <span key={id} className="bg-page px-3 py-1.5 rounded-lg border border-border-strong text-xs font-medium text-text-primary flex items-center gap-2 max-w-full">
                              {inner}
                            </span>
                          );
                        })}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {out.legal_aid_resources && out.legal_aid_resources.length > 0 && (
        <div className="space-y-4 pt-4">
          <h3 className="text-xs font-bold text-text-muted uppercase tracking-wider">Official Legal Assistance</h3>
          <div className="space-y-4">
            {out.legal_aid_resources.map((resource, i) => (
              <div key={i} className="p-6 bg-surface border-2 border-accent-primary/20 rounded-xl shadow-md relative overflow-hidden">
                <div className="absolute top-0 left-0 w-1 h-full bg-accent-primary" />
                <div className="flex items-start justify-between gap-4 mb-3">
                  <div>
                    <h4 className="text-text-primary font-bold text-lg">{resource.name}</h4>
                    <div className="text-xs text-accent-primary mt-1 font-semibold uppercase tracking-wider">{resource.level} Authority</div>
                  </div>
                </div>
                <p className="text-text-secondary text-sm leading-relaxed">{resource.description}</p>
                <div className="mt-5 flex flex-wrap gap-3">
                  <a href={resource.official_url} target="_blank" rel="noopener noreferrer" className="px-5 py-2.5 bg-accent-primary hover:bg-accent-hover rounded-lg text-sm font-medium text-white transition-colors shadow-sm">
                    Visit Official Site
                  </a>
                  <span className="px-5 py-2.5 bg-page border border-border-strong rounded-lg text-sm font-medium text-text-primary">
                    {resource.contact_info}
                  </span>
                </div>
                <div className="mt-5 pt-4 border-t border-border-subtle flex items-center justify-between">
                  <div className="flex items-center gap-1.5 text-xs text-success-text font-semibold uppercase tracking-wide">
                    <ShieldAlert className="w-4 h-4" />
                    Verified Official Source
                  </div>
                  <a href={resource.source_url} target="_blank" rel="noopener noreferrer" className="text-xs text-text-muted hover:text-accent-primary transition-colors font-medium">
                    View Data Source &rarr;
                  </a>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="pt-8 mt-12 border-t border-border-subtle">
        <p className="text-sm text-text-muted text-center font-medium">
          {out.disclaimer || "Legal information, not legal advice."}
        </p>
      </div>
    </div>
  );
}
