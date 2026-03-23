---
name: codex
description: |
  OpenAI Codex CLI wrapper — five modes. Review: diff-based code review with
  uncommitted/commit/branch support. Challenge: adversarial mode that tries to break
  your code. Consult: ask codex anything with session continuity. Plan: review
  implementation plans. Research: topic research with structured reports.
  Use when asked to "codex review", "codex challenge", "ask codex", "codex plan",
  "codex research", "second opinion", or "consult codex".
allowed-tools:
  - Bash
  - Read
  - Write
  - Glob
  - Grep
  - AskUserQuestion
---

# /codex — Multi-AI Second Opinion

Unified skill wrapping the OpenAI Codex CLI. Get an independent second opinion from a separate AI system for cross-model verification.

---

## Step 0: Check codex binary

```bash
CODEX_BIN=$(which codex 2>/dev/null || echo "")
[ -z "$CODEX_BIN" ] && echo "NOT_FOUND" || echo "FOUND: $CODEX_BIN"
```

If `NOT_FOUND`, stop and tell the user:
"Codex CLI not found. Install: `npm install -g @openai/codex && codex auth`"

---

## Step 1: Detect mode

Parse user input to determine the mode:

1. `/codex review [args]` → **Review Mode** (Step 2A)
2. `/codex challenge [focus]` → **Challenge Mode** (Step 2B)
3. `/codex plan [file]` → **Plan Mode** (Step 2C)
4. `/codex research <topic>` → **Research Mode** (Step 2D)
5. `/codex` (no arguments) → **Auto-detect:**
   - If a diff exists → ask user to choose review or challenge
   - If a plan file exists → suggest plan review
   - Otherwise → "What would you like to ask Codex?"
6. `/codex <anything else>` → **Consult Mode** (Step 2E)

---

## Step 2A: Review Mode

Run `codex exec review` via the bundled shell script.

### Usage

| Argument | Behavior |
|----------|----------|
| (none) | Review uncommitted changes. Falls back to last commit if none |
| `last commit` | Review the last commit |
| `last N commits` | Review last N commits (numbers and words both work) |
| `against <branch>` | Review current branch against target branch |
| `--base <branch>` | Same as `against` |
| `-m <model>` | Use a specific model |

### Execution

```bash
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/.." 2>/dev/null && pwd)"
# Fall back to direct path if skill dir cannot be resolved
SCRIPT_PATH="${SKILL_DIR:-$HOME/.agents/skills/codex}/scripts/codex-review.sh"
bash "$SCRIPT_PATH" $ARGUMENTS
```

If the shell script is unavailable, construct the codex command directly:

1. Detect base branch:
```bash
BASE=$(gh pr view --json baseRefName -q .baseRefName 2>/dev/null || gh repo view --json defaultBranchRef -q .defaultBranchRef.name 2>/dev/null || echo "main")
```

2. Run review (5-minute timeout):
```bash
codex exec review --base "$BASE" -m gpt-5.2-codex -c 'model_reasoning_effort="high"' --dangerously-bypass-approvals-and-sandbox
```

### Output format

```
CODEX SAYS (code review):
════════════════════════════════════════════════════════════
<full codex output verbatim — do not truncate or summarize>
════════════════════════════════════════════════════════════
```

### Cross-model comparison

If Claude's `/review` was already run earlier in this conversation, compare the two:

```
CROSS-MODEL ANALYSIS:
  Both found: [overlapping findings]
  Only Codex found: [findings unique to Codex]
  Only Claude found: [findings unique to Claude]
  Agreement rate: X%
```

---

## Step 2B: Challenge (Adversarial) Mode

Codex tries to break your code — finding edge cases, race conditions, security holes, and failure modes.

1. Construct the adversarial prompt:

Default prompt (no focus):
"Review the changes on this branch. Run `git diff origin/<base>` to see the diff.
Your job is to find ways this code will fail in production. Think like an attacker
and a chaos engineer. Find edge cases, race conditions, security holes, resource leaks,
failure modes, and silent data corruption paths. Be adversarial. Be thorough."

With focus (e.g., `/codex challenge security`):
"Focus specifically on SECURITY. Find every way an attacker could exploit this code."

2. Run with JSONL output (5-minute timeout):
```bash
codex exec "<prompt>" -s read-only -c 'model_reasoning_effort="high"' --json 2>/dev/null | python3 -c "
import sys, json
for line in sys.stdin:
    line = line.strip()
    if not line: continue
    try:
        obj = json.loads(line)
        t = obj.get('type','')
        if t == 'item.completed' and 'item' in obj:
            item = obj['item']
            itype = item.get('type','')
            text = item.get('text','')
            if itype == 'reasoning' and text:
                print(f'[codex thinking] {text}')
                print()
            elif itype == 'agent_message' and text:
                print(text)
            elif itype == 'command_execution':
                cmd = item.get('command','')
                if cmd: print(f'[codex ran] {cmd}')
        elif t == 'turn.completed':
            usage = obj.get('usage',{})
            tokens = usage.get('input_tokens',0) + usage.get('output_tokens',0)
            if tokens: print(f'\ntokens used: {tokens}')
    except: pass
"
```

3. Present the output:
```
CODEX SAYS (adversarial challenge):
════════════════════════════════════════════════════════════
<full output verbatim>
════════════════════════════════════════════════════════════
Tokens: N
```

---

## Step 2C: Plan Mode

Review an implementation plan file with Codex.

1. Detect the plan file:
```bash
# Use file from arguments if provided, otherwise auto-detect the latest
if stat --version &>/dev/null 2>&1; then
  PLAN_FILE=$(find ~/.claude/plans -maxdepth 1 -name "*.md" -type f -exec stat -c '%Y %n' {} \; 2>/dev/null | sort -rn | head -1 | cut -d' ' -f2-)
else
  PLAN_FILE=$(find ~/.claude/plans -maxdepth 1 -name "*.md" -type f -exec stat -f '%m %N' {} \; 2>/dev/null | sort -rn | head -1 | cut -d' ' -f2-)
fi
```

2. Run Codex review:
```bash
PROMPT="Please provide a comprehensive review of the following implementation plan:

1. **Feasibility**: Is this technically feasible? What are the potential issues or risks?
2. **Missing Items**: Are there any missing steps or considerations?
3. **Alternatives**: Are there better approaches or improvements to suggest?

Plan file: $PLAN_FILE

---
$(cat "$PLAN_FILE")
---"

codex exec -m gpt-5.2-codex -c 'model_reasoning_effort="high"' "$PROMPT"
```

3. Present the results from three perspectives:
   - **Feasibility** — Technical viability and risks
   - **Missing Items** — Gaps or missing steps
   - **Alternatives** — Better approaches

---

## Step 2D: Research Mode

Generate a structured research report on any topic.

1. Parse arguments:
   - `-d` / `--deep`: Enable deep research mode (more thorough, slower)
   - `-m <model>`: Specify a model
   - Everything else: The research topic

2. Run Codex research:
```bash
DEPTH="Provide a focused, practical overview covering the most important aspects."
# For deep mode:
# DEPTH="Perform an exhaustive deep-dive analysis. Cover history, current state, future trends, key players, trade-offs, and lesser-known insights."

PROMPT="You are a research analyst. Investigate the following topic and produce a structured research report in markdown format.

## Research Topic
$TOPIC

## Instructions
$DEPTH

## Required Report Structure

### Summary
A concise 2-3 sentence executive summary.

### Key Findings
Numbered list of the most important discoveries and insights.

### Analysis
Detailed analysis organized by relevant subtopics.

### Recommendations
Actionable recommendations based on the findings.

### Sources & References
List credible sources, documentation links, or references used."

codex exec -m gpt-5.2-codex -c 'model_reasoning_effort="high"' "$PROMPT"
```

3. After presenting the report, offer follow-up options:
   - Deep dive into a specific section
   - Compare with alternative topics
   - Save the report to a file

---

## Step 2E: Consult Mode

Ask Codex anything about the codebase. Supports session continuity for follow-ups.

1. Check for an existing session:
```bash
cat .context/codex-session-id 2>/dev/null || echo "NO_SESSION"
```

If a session exists, ask whether to continue or start fresh.

2. Run with JSONL output (5-minute timeout):

For a **new session:**
```bash
codex exec "<prompt>" -s read-only -c 'model_reasoning_effort="high"' --json 2>/dev/null | python3 -c "
import sys, json
for line in sys.stdin:
    line = line.strip()
    if not line: continue
    try:
        obj = json.loads(line)
        t = obj.get('type','')
        if t == 'thread.started':
            tid = obj.get('thread_id','')
            if tid: print(f'SESSION_ID:{tid}')
        elif t == 'item.completed' and 'item' in obj:
            item = obj['item']
            itype = item.get('type','')
            text = item.get('text','')
            if itype == 'reasoning' and text:
                print(f'[codex thinking] {text}')
                print()
            elif itype == 'agent_message' and text:
                print(text)
            elif itype == 'command_execution':
                cmd = item.get('command','')
                if cmd: print(f'[codex ran] {cmd}')
        elif t == 'turn.completed':
            usage = obj.get('usage',{})
            tokens = usage.get('input_tokens',0) + usage.get('output_tokens',0)
            if tokens: print(f'\ntokens used: {tokens}')
    except: pass
"
```

For a **resumed session:**
```bash
codex exec resume <session-id> "<prompt>" -s read-only -c 'model_reasoning_effort="high"' --json 2>/dev/null | python3 -c "<same parser>"
```

3. Save the session ID:
```bash
mkdir -p .context
echo "<session-id>" > .context/codex-session-id
```

4. Present the output:
```
CODEX SAYS (consult):
════════════════════════════════════════════════════════════
<full output verbatim>
════════════════════════════════════════════════════════════
Tokens: N
Session saved — run /codex again to continue this conversation.
```

5. If Codex's analysis differs from Claude's understanding, flag it:
   "Note: Claude Code disagrees on X because Y."

---

## Error Handling

- **Binary not found:** Detected in Step 0. Stop with install instructions.
- **Auth error:** "Codex authentication failed. Run `codex login` to authenticate."
- **Timeout:** If the Bash call times out (5 min), inform the user. Use `timeout: 300000`.
- **Empty response:** Tell the user to check stderr for errors.
- **Session resume failure:** Delete the session file and start fresh.

---

## Important Rules

- **Never modify files.** This skill is read-only. Codex runs in read-only sandbox mode.
- **Present output verbatim.** Do not truncate, summarize, or editorialize Codex's output before showing it.
- **Add synthesis after, not instead of.** Any Claude commentary comes after the full output.
- **5-minute timeout** on all Bash calls to codex (`timeout: 300000`).
- **No double-reviewing.** If `/review` was already run, Codex provides an independent second opinion. Do not re-run Claude's own review.
