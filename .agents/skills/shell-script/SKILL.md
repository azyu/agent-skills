---
name: shell-script
description: Use when creating, editing, or reviewing shell scripts. Detect the target shell first, preserve the existing shell unless migration is requested, and apply shell-specific rules for bash, sh, or zsh. Triggers on shell script creation, .sh file editing, shellcheck, and shell scripting best practices. Keywords - "shell script", "bash script", ".sh file", "shellcheck", "쉘 스크립트".
---

# shell-script

Required rules and patterns for writing or editing shell scripts.

## Scope

- MUST identify the target shell from the existing shebang, surrounding repo context, or explicit user request before editing.
- MUST preserve the current shell unless the user explicitly asks for migration.
- If the target shell is unclear, state the assumption before writing code.
- MUST use bash-only constructs such as `[[ ]]`, arrays, process substitution, `pipefail`, or `local` only when the target shell is bash-compatible.

## Required Header

For a new bash script, start with:

```bash
#!/usr/bin/env bash
set -euo pipefail
```

- `#!/usr/bin/env bash`: portable shebang without a hardcoded bash path
- `set -e`: exit immediately on error
- `set -u`: fail on undefined variable reference
- `set -o pipefail`: propagate failures through pipelines

- MUST keep an existing non-bash shebang unless the user asks to convert the script.
- For a new POSIX `sh` script, use a POSIX-compatible shebang and only add strict-mode options supported by that shell.
- If strict mode would break intentional control flow, keep the script readable and add only the flags the script can safely support.

## shellcheck Required

MUST run `shellcheck <file>` after writing or editing a shell script when `shellcheck` is available for the target shell.

- If `shellcheck` is unavailable, state that it was not installed and continue with a manual review of quoting, word splitting, traps, and error handling.
- If the script targets a non-default shell, pass the appropriate shell flag or document why the default invocation is sufficient.
- If multiple shell scripts changed, run `shellcheck` on each changed script or state which files were not checked.

Common findings:

| Code | Issue | Fix |
|------|-------|-----|
| SC2086 | Unquoted variable | Use `"$var"` |
| SC2034 | Unused variable | Remove it, or keep it only when external tooling intentionally reads it |
| SC2155 | `local` + assignment combined | Split: `local var; var=$(cmd)` |
| SC2046 | Unquoted command substitution | Use `"$(cmd)"` |
| SC2064 | Double-quoted trap string | Use `trap '...' EXIT` |
| SC2162 | Missing `-r` on `read` | Use `read -r` |

## Variables and Quoting

```bash
# Quote expansions unless the shell syntax requires splitting or globbing
echo "$variable"
cp "$src" "$dest"

# Expand the full array in bash
for item in "${array[@]}"; do
  printf '%s\n' "$item"
done

# Default value pattern that remains safe under set -u
val="${VAR:-default}"
```

- MUST quote variable and command substitutions unless intentional splitting or glob expansion is required.
- If intentional splitting is required, keep it local and make the reason obvious in the code.

## Function Pattern

```bash
my_func() {
  local arg1="$1"
  local result
  result=$(some_command "$arg1")
  printf '%s' "$result"
}
```

- In bash-compatible shells, separate `local` declaration from assignment to avoid masking command failures.
- Use `printf` when output must be exact or portable across shells.
- Return values via stdout; use exit codes for success or failure.
- If the target shell is POSIX `sh`, avoid `local` and use a POSIX-compatible function style.

## Error Handling

```bash
# Allow a known, intentional failure path
if ! cmd_that_may_fail; then
  printf '%s\n' "continuing after expected failure" >&2
fi

# Fallback value
if ! result=$(cmd 2>/dev/null); then
  result="fallback"
fi

# Cleanup trap
cleanup() { rm -f "$tmpfile"; }
trap cleanup EXIT
```

- MUST make expected failure paths explicit instead of silently swallowing errors.
- If a fallback value is used, keep the fallback close to the failing command.
- If cleanup is required, register a trap after the resource is created.

## General Rules

- MUST use `mktemp` for temporary files instead of hardcoded paths.
- MUST use `$(( ... ))` for arithmetic in shells that support it.
- Use `[[ ... ]]` only in bash-compatible shells; use POSIX `[ ... ]` when the script targets `sh`.
- Use process substitution `< <(cmd)` only in shells that support it.
- Use here-strings `<<< "$var"` only in shells that support them.
- If a pipeline becomes hard to read or debug, split it across lines or assign intermediate values to variables.
