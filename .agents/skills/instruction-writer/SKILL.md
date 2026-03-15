---
name: instruction-writer
description: Write or rewrite prompts, AGENTS.md, CLAUDE.md, policy docs, and instruction files into model-friendly rules. Use when the user asks to draft new instruction documents, convert negative wording into positive directives, replace abstract prohibitions with observable actions, tighten agent instructions, or rewrite guidance like "don't", "do not", "never", "no", or "nothing" into concrete MUST/SHOULD behavior.
---

# Instruction Writer

Write or rewrite instruction documents so the model gets clear, executable rules instead of vague prohibitions.

Use this skill for:
- `AGENTS.md`, `CLAUDE.md`, Copilot instructions, system prompts, policy docs, and internal rule files
- Requests like "부정문을 긍정문으로 바꿔줘", "make this prompt less hallucination-prone", "rewrite these instructions", "turn don't/do not into must/should", "make this guidance more actionable", or "draft a new AGENTS.md from scratch"

## Goals

1. Preserve the original intent and rule strength
2. Replace abstract prohibitions with observable behavior
3. Add fallback behavior when uncertainty or ambiguity exists
4. Draft from explicit goals and boundaries when no source document exists
5. Keep edits surgical unless the user asks for a broader rewrite

## Workflow

### 1. Inspect the target document first

- If a target document exists, read the actual file before proposing rewrites
- If no target document exists, extract the intended goals, operating boundaries, and fallback behavior before drafting
- Identify repeated patterns such as `don't`, `do not`, `never`, `no`, `nothing`, or vague warnings like "avoid hallucination"
- Separate three cases:
  - style-only rewrites
  - behavior rewrites
  - new drafting from requirements
  - true safety boundaries that may still need a hard prohibition

### 2. Write rules into executable behavior

Prefer this shape whenever possible:

`must do Y when condition C`

Good instruction rules specify:
- the trigger or condition
- the required behavior
- the fallback when the requirement cannot be satisfied
- When rewriting a prohibition, prefer a target behavior plus fallback over a bare prohibition

Examples:
- `Do not guess.` → `If information is missing, state what is missing and ask one clarifying question.`
- `Do not hallucinate.` → `If the answer is uncertain, explicitly state uncertainty and provide only what is supported by the available context.`
- `Never make up references.` → `Must cite only references actually used; if no source is available, say that no source was provided.`
- `Do not assume.` → `Must separate observed facts, assumptions, and open questions in distinct bullets.`

### 3. Keep rule strength explicit

Use modal strength consistently:
- `MUST` for hard requirements
- `SHOULD` for strong defaults or preferred behavior
- `MAY` for optional behavior

MUST preserve the original rule strength instead of flattening all rules to the same modality.

### 4. Keep hard prohibitions only where they are genuinely needed

Hard prohibitions are still appropriate for clear safety boundaries, especially when the claim would be materially misleading.

Examples:
- `Never claim to have run code you did not run.`
- `Never fabricate citations.`

Even then, add the fallback behavior when possible:
- `Never fabricate citations. If no valid source is available, say that no source was provided.`
- If a prohibition remains, attach the required follow-up behavior when possible

### 5. Prefer observable checks over abstract ideals

Each rewritten rule should be easy to verify from the output.

Prefer:
- `Must label uncertain claims as hypotheses.`
- `Must quote exact numbers only from provided sources.`
- `If evidence conflicts, present both possibilities and say which source is stronger.`

Replace weak examples like:
- `Be accurate.`
- `Avoid hallucination.`
- `Be clear.`

### 6. Edit or draft surgically

- Preserve frontmatter, section order, headings, and examples unless the user asked to restructure them
- When rewriting, change only the lines required to achieve the requested rewrite
- When drafting, include only the sections needed for the requested instruction scope
- If adjacent text is already aligned with the new style, leave it alone

## Validation Checklist

Before finishing:
- List any residual `don't`, `do not`, `never`, `no`, or `nothing` phrases and justify each remaining hard prohibition
- For each remaining hard prohibition, confirm it is a real safety boundary
- Confirm each written or rewritten rule describes an observable action
- Confirm uncertainty, ambiguity, and missing-information cases have an explicit fallback
- Confirm `MUST` vs `SHOULD` still matches the original policy strength
- Confirm the document scope is limited to what the user requested

## Reference

For instruction patterns and before/after examples, read [references/write-patterns.md](references/write-patterns.md).
