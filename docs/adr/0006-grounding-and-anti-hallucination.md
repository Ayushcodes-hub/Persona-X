# ADR 0006: Grounding, Anti-Hallucination & Cite-or-Drop Verification

## Status
Accepted

## Context
The core product promise of PERSONA-X is evidence-backed public intelligence without fabricated facts, hallucinated quotes, or unsourced claims. Standard LLM extraction pipelines frequently introduce subtle confabulations, paraphrases presented as direct quotes, or misplaced dates.

## Decision
1. **Cite-or-Drop Pipeline Stage**:
   - Establish a dedicated verification stage in `engine/evidence/` prior to timeline, statement, or claim persistence.
   - Every extracted direct quote or specific assertion MUST include:
     - `source_id`: Valid ID of captured source.
     - `text_span`: Exact verbatim string excerpt from the source.
2. **Deterministic Span Verification**:
   - The verifier performs normalized string search of `text_span` against the clean textual body in `source_captures.extracted_text`.
   - If the quoted span cannot be verified within the source text, the item is either demoted to `unverified_claim` or dropped entirely from the public dossier.
3. **Corroboration & Confidence Scoring**:
   - Confidence is computed algorithmically:
     - Number of independent sources corroborating the claim.
     - Source Tier (Tier 1: primary/official records = 1.0 weight; Tier 2: reputable media = 0.8 weight; Tier 3: secondary = 0.5 weight).
     - Recency and attribution clarity.
4. **Statement Taxonomy**:
   - Explicitly classify all statements into:
     - `direct_quote`: Verbatim quote in primary or interview source.
     - `reported_claim`: Claim reported by secondary source.
     - `paraphrase`: Summarized position.
     - `allegation`: Unresolved claim or legal assertion.

## Consequences
- **Positive**: Eliminates hallucinated facts; verifiable citations for every dossier claim; defensible intelligence output.
- **Negative**: Increases computation time slightly during the verification stage.
