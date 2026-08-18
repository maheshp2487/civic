export interface Jurisdiction {
  country: string;
  state?: string;
  district?: string;
}

export interface Situation {
  category: string;
  subcategory: string;
  jurisdiction?: Jurisdiction;
  facts: string[];
  parties: string[];
  missing_information: string[];
  urgency_indicator: string;
}

export interface SourceCitation {
  title: string;
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
}

export interface OutputResponse {
  situation_summary: string;
  clarification_questions: string[];
  verified_information: string[];
  source_citations: SourceCitation[];
  evidence_checklist: EvidenceItem[];
  action_plan: ActionStep[];
  disclaimer: string;
}
