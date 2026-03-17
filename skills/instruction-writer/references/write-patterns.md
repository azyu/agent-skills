# Instruction Patterns

Use these patterns when writing or rewriting instruction documents into model-friendly rules.

## Core heuristic

Prefer:

`must do Y when condition C`

over:

`never do X`

because the positive form gives the model a target behavior, not just a blocked action.
When rewriting a prohibition, prefer a target behavior plus fallback over a bare prohibition.

## Pattern Library

### 1. Abstract prohibition -> explicit fallback

- `Do not guess.`  
  -> `If information is missing, state what is missing and ask one clarifying question.`

- `Do not speculate.`  
  -> `If evidence is insufficient, label the uncertain part explicitly and provide only the supported portion of the answer.`

- `Do not hallucinate.`  
  -> `If the answer is uncertain, state the uncertainty explicitly and answer only with what the available context supports.`

### 2. Anti-fabrication -> source-bounded behavior

- `Never invent sources.`  
  -> `Must cite only sources actually used. If no source is available, say that no source was provided.`

- `Never make up references.`  
  -> `Must cite only references present in the provided materials; if none are available, say that no source was provided.`

- `Do not quote numbers without evidence.`  
  -> `Must quote exact numbers only from the provided or verified sources.`

### 3. Anti-assumption -> structured reasoning output

- `Do not assume.`  
  -> `Must separate observed facts, assumptions, and open questions in distinct bullets.`

- `Do not infer missing facts.`  
  -> `If required information is missing, explicitly say what is missing and ask one clarifying question.`

- `Do not pick silently.`  
  -> `If multiple interpretations exist, present the alternatives and recommend one explicitly.`

### 4. Conflict handling -> comparison behavior

- `Do not ignore conflicting evidence.`  
  -> `If evidence conflicts, present both possibilities and state which source is stronger.`

- `Do not hide uncertainty.`  
  -> `Must label uncertain claims as hypotheses and explain what would resolve them.`

### 5. Safety boundary -> prohibition plus fallback

- `Never claim to have run code you did not run.`  
  -> Keep as-is. Add: `If execution was not performed, say that you did not run it.`

- `Never fabricate citations.`  
  -> Keep as-is. Add: `If no valid citation is available, say that no source was provided.`

- If a prohibition must remain, attach the required follow-up behavior when possible.

## Strength Mapping

- Use `MUST` when the behavior is mandatory and violations would materially reduce reliability or safety.
- Use `SHOULD` when the behavior is the default but can yield to local context.
- Use `MAY` when the behavior is optional.

## Drafting and Editing Guardrails

- Preserve the original policy intent and scope.
- If no source document exists, derive the smallest complete document from the requested goals and boundaries.
- Preserve section structure unless the user explicitly asks for reorganization.
- Prefer observable output requirements over abstract virtues.
- Keep hard prohibitions only for actual safety boundaries.
