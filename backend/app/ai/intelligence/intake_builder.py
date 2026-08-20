from typing import List, Optional
from app.schemas.contracts import Situation, IntakeForm, IntakeField

class IntakeBuilder:
    @staticmethod
    def build(situation: Situation) -> Optional[IntakeForm]:
        if not situation.missing_information:
            return None
            
        fields: List[IntakeField] = []
        missing_lower = [m.lower() for m in situation.missing_information]
        
        # General Fields
        if any("jurisdiction" in m or "state" in m or "city" in m or "location" in m for m in missing_lower):
            fields.append(IntakeField(
                id="jurisdiction",
                label="Where did this happen?",
                type="select",
                options=["Maharashtra", "Delhi", "Karnataka", "Tamil Nadu", "Other"],
                required=True
            ))
            
        if any("amount" in m or "cost" in m or "money" in m or "value" in m or "rent" in m for m in missing_lower):
            fields.append(IntakeField(
                id="amount",
                label="How much money is involved? (₹)",
                type="number",
                required=True,
                placeholder="e.g. 50000"
            ))
            
        if any("date" in m or "when" in m or "time" in m or "year" in m for m in missing_lower):
            fields.append(IntakeField(
                id="date",
                label="When did this happen?",
                type="date",
                required=False
            ))
            
        if any("party" in m or "who" in m or "person" in m or "name" in m for m in missing_lower):
            fields.append(IntakeField(
                id="other_party",
                label="Who is the other party involved?",
                type="text",
                required=False,
                placeholder="e.g. Landlord name, Employer name"
            ))
            
        # Domain Specific Fields
        category_lower = situation.category.lower()
        if "tenancy" in category_lower or "rent" in category_lower:
            if any("agreement" in m for m in missing_lower):
                fields.append(IntakeField(
                    id="evidence_agreement",
                    label="Do you have a written rental agreement?",
                    type="radio",
                    options=["Yes", "No"],
                    required=True
                ))
        elif "employment" in category_lower:
            if any("evidence" in m or "document" in m for m in missing_lower):
                fields.append(IntakeField(
                    id="evidence_employment",
                    label="What documents do you have?",
                    type="checkbox",
                    options=["Offer Letter", "Payslips", "Email/Messages", "None"],
                    required=False
                ))
        elif "consumer" in category_lower:
            if any("evidence" in m or "document" in m or "bill" in m or "receipt" in m for m in missing_lower):
                fields.append(IntakeField(
                    id="evidence_consumer",
                    label="Do you have proof of purchase?",
                    type="checkbox",
                    options=["Invoice/Bill", "Warranty Card", "Payment Receipt", "None"],
                    required=False
                ))
                
        # Always add a free-text fallback if they need to explain more
        fields.append(IntakeField(
            id="additional_facts",
            label="Any other important details?",
            type="text",
            required=False,
            placeholder="Type any additional facts here..."
        ))
        
        if len(fields) <= 1: # Only additional_facts was added
            # fallback for unmapped missing information
            fields.insert(0, IntakeField(
                id="missing_details",
                label=f"Please provide: {', '.join(situation.missing_information)}",
                type="text",
                required=True
            ))
            
        return IntakeForm(
            title="We need a few more details to help you correctly",
            fields=fields
        )
