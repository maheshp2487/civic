# Safety & Security Architecture

## The Core Principle
"Rules determine. Evidence grounds. Gemini explains."

InnoAi is explicitly designed not to trust the generative LLM with critical legal determinations. The pipeline is wrapped in deterministic gates to ensure citizen safety.

## Deterministic Controls
1. **Evidence Sufficiency**: The RAG layer evaluates semantic distance. If distance exceeds a threshold, sufficiency drops to INSUFFICIENT.
2. **Citation Validity**: A final validation pass guarantees that every source referenced in an `ActionStep` exists in the originally retrieved chunk list.
3. **Action Policy**: If sufficiency is `INSUFFICIENT`, the Action Policy engine forcefully turns off action generation capability for the LLM.
4. **Legal-Aid Routing**: Routing maps `jurisdiction` directly to a hardcoded, official list. The LLM is never permitted to synthesize contact information.
5. **Conflict Detection**: Python extracts numerical/date facts from OCR output and cross-checks them against the User's Situation. Conflicts trigger a hard pause in the workflow.

## Adversarial Protection
- **Prompt Injection**: Uploaded documents are parsed and converted into flat `Conflict` claims. Malicious instructions are treated as benign textual data.
- **Data Boundaries**: The RAG context window strictly isolates retrieved legal chunks from user instructions.
