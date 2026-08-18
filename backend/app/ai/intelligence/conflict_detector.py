from app.schemas.contracts import Situation, Conflict

class ConflictDetector:
    @staticmethod
    def merge_and_detect(old_sit: Situation, new_sit: Situation) -> Situation:
        conflicts = list(old_sit.conflicts)
        
        if old_sit.jurisdiction and new_sit.jurisdiction:
            if old_sit.jurisdiction.state and new_sit.jurisdiction.state:
                if old_sit.jurisdiction.state != new_sit.jurisdiction.state:
                    conflicts.append(Conflict(
                        field="Jurisdiction",
                        user_value=old_sit.jurisdiction.state,
                        document_value=new_sit.jurisdiction.state,
                        document_source="User Update",
                        resolution_status="Unresolved"
                    ))
                    
        if old_sit.amounts and new_sit.amounts:
            for new_amt in new_sit.amounts:
                if new_amt not in old_sit.amounts:
                    conflicts.append(Conflict(
                        field="Amount",
                        user_value=", ".join(old_sit.amounts),
                        document_value=new_amt,
                        document_source="User Update",
                        resolution_status="Unresolved"
                    ))
                    
        if old_sit.dates and new_sit.dates:
            for new_date in new_sit.dates:
                if new_date not in old_sit.dates:
                    conflicts.append(Conflict(
                        field="Date",
                        user_value=", ".join(old_sit.dates),
                        document_value=new_date,
                        document_source="User Update",
                        resolution_status="Unresolved"
                    ))

        merged_jurisdiction = new_sit.jurisdiction if new_sit.jurisdiction and new_sit.jurisdiction.state else old_sit.jurisdiction
        merged_facts = list(set(old_sit.facts + new_sit.facts))
        merged_parties = list(set(old_sit.parties + new_sit.parties))
        merged_dates = list(set(old_sit.dates + new_sit.dates))
        merged_amounts = list(set(old_sit.amounts + new_sit.amounts))
        merged_docs = list(set(old_sit.documents_mentioned + new_sit.documents_mentioned))
        
        missing = list(set(old_sit.missing_information + new_sit.missing_information))
        if not merged_jurisdiction or not merged_jurisdiction.state:
            if "State/Jurisdiction" not in missing:
                missing.append("State/Jurisdiction")
        elif "State/Jurisdiction" in missing:
            missing.remove("State/Jurisdiction")
            
        return Situation(
            category=new_sit.category or old_sit.category,
            subcategory=new_sit.subcategory or old_sit.subcategory,
            jurisdiction=merged_jurisdiction,
            facts=merged_facts,
            parties=merged_parties,
            dates=merged_dates,
            amounts=merged_amounts,
            documents_mentioned=merged_docs,
            missing_information=missing,
            conflicts=conflicts,
            uncertainty=list(set(old_sit.uncertainty + new_sit.uncertainty)),
            urgency=new_sit.urgency if new_sit.urgency.level != "Low" else old_sit.urgency
        )
