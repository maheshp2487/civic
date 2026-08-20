export interface Conflict {
  field: string;
  user_value: string;
  document_value: string;
  document_source: string;
  resolution_status: string;
}

export interface Jurisdiction {
  country?: string;
  state?: string;
  district?: string;
}

export interface Situation {
  category: string;
  subcategory: string;
  jurisdiction?: Jurisdiction;
  facts: string[];
  parties: string[];
  dates: string[];
  amounts: string[];
  documents_mentioned: string[];
  missing_information: string[];
  conflicts: Conflict[];
}

export interface SourceCitation {
  title: string;
  chunk_id?: string;
  section?: string;
  url?: string;
}

export interface EvidenceItem {
  type: string;
  description: string;
  is_provided: boolean;
}

export interface ActionStep {
  step: number;
  description: string;
  basis_source_ids: string[];
  action_type: string;
  limitation?: string;
}

export interface LegalAidResource {
  name: string;
  level: string;
  description: string;
  official_url: string;
  contact_info: string;
  jurisdiction?: { [key: string]: string };
  source_url: string;
  last_verified_at: string;
}

export interface OutputResponse {
  situation_summary: string;
  clarification_questions: string[];
  verified_information: string[];
  source_citations: SourceCitation[];
  evidence_checklist: EvidenceItem[];
  action_plan: ActionStep[];
  legal_aid_resources: LegalAidResource[];
  legal_aid_status: string;
  disclaimer: string;
}

export interface CaseResponse {
  case_id: string;
  situation: Situation;
  output?: OutputResponse;
  workflow_state: string;
}

const API_BASE = "http://127.0.0.1:8001/api/v1";

export async function sendMessage(caseId: string, content: string): Promise<CaseResponse> {
  const res = await fetch(`${API_BASE}/cases/${caseId}/messages`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content }),
  });
  if (!res.ok) throw new Error("Failed to send message");
  return res.json();
}

export async function uploadDocument(caseId: string, file: File): Promise<CaseResponse> {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_BASE}/cases/${caseId}/documents`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Failed to upload document: ${errorText}`);
  }
  return res.json();
}
