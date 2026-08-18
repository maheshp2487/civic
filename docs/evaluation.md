# Offline Evaluation Framework

We designed a completely deterministic, offline evaluation harness to measure the safety of the pipeline without relying on "LLM-as-a-judge" mechanisms, which are often subject to the same hallucinations they try to measure.

## Metrics Assessed
- **Jurisdiction Accuracy**: Does the system identify the correct state based on the city?
- **Clarification Logic**: Does the system correctly halt generation to ask for missing required facts?
- **Legal-Aid Routing Accuracy**: Does the router output the exact verified official resource names?
- **Unsupported Legal Claim Rate**: Do any action steps lack verifiable citations?
- **Citation Integrity Rate**: Do all cited sources trace back to the retrieved context?

## Results on Golden Dataset (Phase 12 Demo Freeze)
- **Scenario count:** 3
- **Jurisdiction accuracy:** 100.0%
- **Clarification logic accuracy:** 100.0%
- **Legal-aid routing accuracy:** 100.0%
- **Unsupported legal claim rate:** 0.0%
- **Citation integrity rate:** 100.0%
