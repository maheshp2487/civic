from app.schemas.contracts import OutputResponse

class DeterministicEvaluator:
    @staticmethod
    def evaluate(scenario, situation, response: OutputResponse):
        results = {}
        
        # Check clarification trigger accuracy
        if scenario.get("should_clarify"):
            results["clarification_triggered"] = len(response.clarification_questions) > 0
        else:
            # If we don't expect clarification, it's correct if there are 0 questions
            results["clarification_triggered"] = len(response.clarification_questions) == 0

        # Check unsupported claims
        unsupported = 0
        total_claims = len(response.action_plan)
        for action in response.action_plan:
             if not action.basis_source_ids:
                 unsupported += 1
        
        results["unsupported_claim_rate"] = unsupported / total_claims if total_claims > 0 else 0.0
        
        # Check Legal aid routing accuracy
        routed_names = [res.name for res in response.legal_aid_resources]
        expected_routing = scenario.get("expected_legal_aid_routing", [])
        
        if len(expected_routing) == 0:
            results["legal_aid_routing_accuracy"] = 1.0 if len(routed_names) == 0 else 0.0
        else:
            matched = sum(1 for e in expected_routing if any(e in name for name in routed_names))
            results["legal_aid_routing_accuracy"] = 1.0 if matched > 0 else 0.0
        
        # Check Jurisdiction accuracy
        expected_state = scenario.get("expected_jurisdiction_state")
        if expected_state:
            if situation.jurisdiction and situation.jurisdiction.state:
                 results["jurisdiction_accuracy"] = 1.0 if expected_state.lower() in situation.jurisdiction.state.lower() else 0.0
            else:
                 results["jurisdiction_accuracy"] = 0.0
        else:
            # Expected no jurisdiction
            results["jurisdiction_accuracy"] = 1.0 if not situation.jurisdiction or not situation.jurisdiction.state else 0.0
            
        # Citation Integrity
        # If there are sources cited in action plan, do they exist in source_citations?
        total_cited = 0
        valid_cited = 0
        valid_ids = [c.chunk_id for c in response.source_citations]
        for action in response.action_plan:
            for sid in action.basis_source_ids:
                total_cited += 1
                if sid in valid_ids:
                    valid_cited += 1
                    
        results["citation_integrity"] = valid_cited / total_cited if total_cited > 0 else 1.0
            
        return results
