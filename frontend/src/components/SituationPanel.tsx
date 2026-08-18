import { CaseResponse } from "@/lib/api";

export default function SituationPanel({ data }: { data: CaseResponse | null }) {
  if (!data || !data.situation) return null;
  const sit = data.situation;

  return (
    <div className="space-y-6">
      <div className="border-b border-neutral-800 pb-4">
        <h2 className="text-xl font-semibold tracking-tight">Here's what we understood</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <div className="text-sm text-neutral-500 mb-1 font-medium">Issue</div>
          <div className="text-neutral-200">{sit.category} • {sit.subcategory}</div>
        </div>

        <div>
          <div className="text-sm text-neutral-500 mb-1 font-medium">Location</div>
          <div className="text-neutral-200">
            {sit.jurisdiction?.state ? `${sit.jurisdiction.district || ""}, ${sit.jurisdiction.state}` : <span className="text-amber-500 text-sm flex items-center gap-1">Missing</span>}
          </div>
        </div>

        {sit.amounts.length > 0 && (
          <div>
            <div className="text-sm text-neutral-500 mb-1 font-medium">Amount</div>
            <div className="text-neutral-200">{sit.amounts.join(", ")}</div>
          </div>
        )}

        {sit.parties.length > 0 && (
          <div className="col-span-1 md:col-span-2">
            <div className="text-sm text-neutral-500 mb-1 font-medium">Parties</div>
            <div className="text-neutral-200">{sit.parties.join(", ")}</div>
          </div>
        )}
      </div>

      {sit.missing_information.length > 0 && (
        <div className="p-4 bg-amber-950/20 border border-amber-900/50 rounded-xl mt-4">
          <div className="text-amber-500 text-sm font-medium mb-2">We need one more detail</div>
          <ul className="list-disc pl-5 text-sm text-amber-200 space-y-1">
            {sit.missing_information.map((m, i) => <li key={i}>{m}</li>)}
          </ul>
        </div>
      )}
    </div>
  );
}
