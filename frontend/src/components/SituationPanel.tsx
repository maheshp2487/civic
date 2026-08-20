import { CaseResponse } from "@/lib/api";
import { Info, MapPin, Tag, Users, Wallet, AlertCircle } from "lucide-react";

export default function SituationPanel({ data }: { data: CaseResponse | null }) {
  if (!data || !data.situation) return null;
  const sit = data.situation;

  return (
    <div className="bg-surface border border-border-subtle rounded-2xl p-6 shadow-sm">
      <div className="border-b border-border-subtle pb-4 mb-6 flex items-center gap-3">
        <Info className="w-5 h-5 text-accent-primary" />
        <h2 className="text-lg font-semibold tracking-tight text-text-primary">Situation Analysis</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="flex items-start gap-3">
          <div className="p-2 bg-surface-hover rounded-lg text-text-muted mt-1"><Tag className="w-4 h-4" /></div>
          <div>
            <div className="text-xs font-semibold uppercase tracking-wider text-text-muted mb-1">Issue Type</div>
            <div className="text-text-primary font-medium">{sit.category} • {sit.subcategory}</div>
          </div>
        </div>

        <div className="flex items-start gap-3">
          <div className="p-2 bg-surface-hover rounded-lg text-text-muted mt-1"><MapPin className="w-4 h-4" /></div>
          <div>
            <div className="text-xs font-semibold uppercase tracking-wider text-text-muted mb-1">Jurisdiction</div>
            <div className="text-text-primary font-medium">
              {sit.jurisdiction?.state ? `${sit.jurisdiction.district || ""}, ${sit.jurisdiction.state}` : <span className="text-error-text text-sm flex items-center gap-1 font-medium">Unspecified</span>}
            </div>
          </div>
        </div>

        {sit.amounts.length > 0 && (
          <div className="flex items-start gap-3">
            <div className="p-2 bg-surface-hover rounded-lg text-text-muted mt-1"><Wallet className="w-4 h-4" /></div>
            <div>
              <div className="text-xs font-semibold uppercase tracking-wider text-text-muted mb-1">Amount in Dispute</div>
              <div className="text-text-primary font-medium">{sit.amounts.join(", ")}</div>
            </div>
          </div>
        )}

        {sit.parties.length > 0 && (
          <div className="col-span-1 md:col-span-2 flex items-start gap-3">
            <div className="p-2 bg-surface-hover rounded-lg text-text-muted mt-1"><Users className="w-4 h-4" /></div>
            <div>
              <div className="text-xs font-semibold uppercase tracking-wider text-text-muted mb-1">Involved Parties</div>
              <div className="text-text-primary font-medium">{sit.parties.join(", ")}</div>
            </div>
          </div>
        )}
      </div>

      {sit.missing_information.length > 0 && (
        <div className="p-4 bg-error-bg/50 border border-error-border rounded-xl mt-6 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-error-text shrink-0 mt-0.5" />
          <div>
            <div className="text-error-text text-sm font-semibold mb-2">Missing Context</div>
            <ul className="list-disc pl-4 text-sm text-error-text/90 space-y-1 font-medium">
              {sit.missing_information.map((m, i) => <li key={i}>{m}</li>)}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}
