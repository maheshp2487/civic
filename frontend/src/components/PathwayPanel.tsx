import { CaseResponse } from "@/lib/api";
import { CheckCircle2, FileText, Info } from "lucide-react";

export default function PathwayPanel({ data }: { data: CaseResponse | null }) {
  if (!data || !data.output) return null;
  const out = data.output;

  if (!out.action_plan.length && !out.verified_information.length && !out.evidence_checklist.length) {
    return null;
  }

  return (
    <div className="space-y-8">
      <div className="border-b border-neutral-800 pb-4">
        <h2 className="text-2xl font-semibold tracking-tight text-white">Your Legal Pathway</h2>
      </div>

      {out.verified_information.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-sm font-semibold text-neutral-400 uppercase tracking-wider">Verified Information</h3>
          <div className="space-y-3">
            {out.verified_information.map((info, i) => (
              <div key={i} className="p-4 bg-neutral-900 border border-neutral-800 rounded-xl flex gap-3 text-sm shadow-sm">
                <Info className="w-5 h-5 text-indigo-400 shrink-0 mt-0.5" />
                <span className="text-neutral-300 leading-relaxed">{info}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {out.evidence_checklist.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-sm font-semibold text-neutral-400 uppercase tracking-wider">Evidence to Collect</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {out.evidence_checklist.map((item, i) => (
              <div key={i} className="flex items-start gap-3 p-4 bg-neutral-900 rounded-xl border border-neutral-800 text-sm shadow-sm">
                <FileText className="w-5 h-5 text-neutral-500 shrink-0 mt-0.5" />
                <div>
                  <div className="font-medium text-neutral-200">{item.type}</div>
                  <div className="text-neutral-500 mt-1">{item.description}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {out.action_plan.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-sm font-semibold text-neutral-400 uppercase tracking-wider">Your Next Steps</h3>
          <div className="space-y-6 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px before:h-full before:w-0.5 before:bg-neutral-800">
            {out.action_plan.map((action, i) => (
              <div key={i} className="relative flex items-start gap-4">
                <div className="w-10 h-10 rounded-full bg-indigo-900/50 border border-indigo-500/50 flex items-center justify-center shrink-0 z-10 text-indigo-300 font-semibold shadow-md">
                  {action.step}
                </div>
                <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-5 flex-1 shadow-sm">
                  <div className="font-medium text-white mb-2 text-base">{action.action_type}</div>
                  <div className="text-neutral-400 text-sm leading-relaxed">{action.description}</div>
                  {action.basis_source_ids && action.basis_source_ids.length > 0 && (
                    <div className="mt-4 pt-3 border-t border-neutral-800 text-xs text-neutral-500 flex flex-wrap gap-2">
                      <span className="font-medium uppercase tracking-wide text-neutral-600 mt-0.5">Sources:</span>
                      {action.basis_source_ids.map(id => {
                        const cite = out.source_citations.find(c => c.chunk_id === id);
                        return cite ? <span key={id} className="bg-neutral-950 px-2 py-1 rounded border border-neutral-800">{cite.title} {cite.section && `· ${cite.section}`}</span> : null;
                      })}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {out.legal_aid_resources && out.legal_aid_resources.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-sm font-semibold text-amber-500 uppercase tracking-wider">Official Legal Assistance</h3>
          <div className="space-y-4">
            {out.legal_aid_resources.map((resource, i) => (
              <div key={i} className="p-5 bg-gradient-to-br from-amber-950/30 to-amber-900/10 border border-amber-900/50 rounded-xl shadow-sm">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <h4 className="text-amber-500 font-semibold">{resource.name}</h4>
                    <div className="text-xs text-amber-200/70 mt-1 uppercase tracking-wide">{resource.level} Authority</div>
                  </div>
                </div>
                <p className="text-neutral-300 text-sm mt-3 leading-relaxed">{resource.description}</p>
                <div className="mt-4 flex flex-wrap gap-3">
                  <a href={resource.official_url} target="_blank" rel="noopener noreferrer" className="px-4 py-2 bg-amber-900/40 hover:bg-amber-900/60 border border-amber-800 rounded-lg text-xs font-medium text-amber-200 transition-colors">
                    Visit Official Site
                  </a>
                  <span className="px-4 py-2 bg-neutral-900/80 border border-neutral-800 rounded-lg text-xs font-medium text-neutral-300">
                    {resource.contact_info}
                  </span>
                </div>
                <div className="mt-4 pt-3 border-t border-amber-900/30 flex items-center justify-between">
                  <span className="text-[10px] text-amber-500/50 uppercase tracking-widest">Verified Official Source</span>
                  <a href={resource.source_url} target="_blank" rel="noopener noreferrer" className="text-[10px] text-amber-400 hover:underline flex items-center gap-1">
                    Data Source
                  </a>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="pt-8 border-t border-neutral-800 mt-12">
        <p className="text-sm text-neutral-500 text-center font-medium">
          {out.disclaimer || "Legal information, not legal advice."}
        </p>
      </div>
    </div>
  );
}
