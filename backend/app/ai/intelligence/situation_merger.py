from typing import List, Tuple, Dict
from app.schemas.contracts import Situation, DocumentClaim, Conflict, Jurisdiction, IntakeResponse

class SituationMerger:
    @staticmethod
    def merge(situation: Situation, claims: List[DocumentClaim]) -> Situation:
        for claim in claims:
            if claim.claim_type == "Amount":
                if situation.amounts:
                    conflict_found = False
                    for amt in situation.amounts:
                        if claim.value not in amt and amt not in claim.value:
                            situation.conflicts.append(Conflict(
                                field="Amount",
                                user_value=amt,
                                document_value=claim.value,
                                document_source=f"Uploaded Document (Page {claim.page_number or 1})",
                                resolution_status="Unresolved"
                            ))
                            conflict_found = True
                    if not conflict_found:
                        situation.amounts.append(claim.value)
                else:
                    situation.amounts.append(claim.value)
                    
            elif claim.claim_type == "Date":
                if situation.dates:
                    conflict_found = False
                    for date in situation.dates:
                        if claim.value not in date and date not in claim.value:
                            situation.conflicts.append(Conflict(
                                field="Date",
                                user_value=date,
                                document_value=claim.value,
                                document_source=f"Uploaded Document (Page {claim.page_number or 1})",
                                resolution_status="Unresolved"
                            ))
                            conflict_found = True
                    if not conflict_found:
                        situation.dates.append(claim.value)
                else:
                    situation.dates.append(claim.value)
                    
            elif claim.claim_type == "Party":
                situation.parties.append(claim.value)
                
            elif claim.claim_type == "Fact":
                situation.facts.append(claim.value)
                
        situation.amounts = list(set(situation.amounts))
        situation.dates = list(set(situation.dates))
        situation.parties = list(set(situation.parties))
        situation.facts = list(set(situation.facts))
        
        return situation
        
    @staticmethod
    def merge_intake(situation: Situation, intake: IntakeResponse) -> Tuple[Situation, bool]:
        """
        Merges an IntakeResponse directly into the Situation.
        Returns a tuple: (Updated Situation, Requires Evidence Invalidation)
        """
        invalidate_evidence = False
        vals = intake.values
        
        if "jurisdiction" in vals and vals["jurisdiction"]:
            new_jurisdiction = vals["jurisdiction"].strip()
            # If changed, invalidate
            if not situation.jurisdiction or situation.jurisdiction.state != new_jurisdiction:
                if not situation.jurisdiction:
                    situation.jurisdiction = Jurisdiction(country="India", state=new_jurisdiction)
                else:
                    situation.jurisdiction.state = new_jurisdiction
                    situation.jurisdiction.district = None
                invalidate_evidence = True
                
        if "amount" in vals and vals["amount"]:
            amt = str(vals["amount"]).strip()
            if amt not in situation.amounts:
                situation.amounts.append(amt)
                invalidate_evidence = True
                
        if "date" in vals and vals["date"]:
            date_val = str(vals["date"]).strip()
            if date_val not in situation.dates:
                situation.dates.append(date_val)
                # Dates may or may not be material depending on domain, but usually are
                invalidate_evidence = True
                
        if "other_party" in vals and vals["other_party"]:
            party = str(vals["other_party"]).strip()
            if party not in situation.parties:
                situation.parties.append(party)
                # Adding a party usually doesn't invalidate generic laws, but might change local routing
                invalidate_evidence = True
                
        # Merge evidence boolean fields as documents
        evidence_keys = [k for k in vals.keys() if k.startswith("evidence_")]
        for ek in evidence_keys:
            ev_val = str(vals[ek]).strip()
            if ev_val and ev_val.lower() != "no" and ev_val.lower() != "none":
                # Only add if it's new
                if ev_val not in situation.documents_mentioned:
                    situation.documents_mentioned.append(ev_val)
                
        if "additional_facts" in vals and vals["additional_facts"]:
            fact = str(vals["additional_facts"]).strip()
            if fact not in situation.facts:
                situation.facts.append(fact)
                invalidate_evidence = True
                
        # Handle dynamically generated questions
        dynamic_keys = [k for k in vals.keys() if k.startswith("dynamic_q_")]
        for dk in dynamic_keys:
            ans = str(vals[dk]).strip()
            if ans:
                # Extract the question text from the ID (e.g. dynamic_q_0__What happened?)
                parts = dk.split("__", 1)
                question_text = parts[1] if len(parts) > 1 else "Additional Context"
                fact = f"Answer to '{question_text}': {ans}"
                if fact not in situation.facts:
                    situation.facts.append(fact)
                    invalidate_evidence = True
                
        # Clear out the missing information because the user just submitted the form
        # The AI will figure out if something is still missing next time
        situation.missing_information = []
        
        return situation, invalidate_evidence
