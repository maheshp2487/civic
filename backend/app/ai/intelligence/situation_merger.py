from typing import List
from app.schemas.contracts import Situation, DocumentClaim, Conflict

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
