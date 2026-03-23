#!/bin/bash
# codex-review.sh - Code review with OpenAI Codex
# Based on jinto/cc-plugins + azyu/cc-plugins improve/review-against-branch

set -e

# Default values
MODEL="gpt-5.2-codex"
REASONING="high"
REVIEW_TYPE="uncommitted"
COMMIT_COUNT=1
BASE_BRANCH=""
CUSTOM_PROMPT=""

# Convert word numbers to digits
word_to_number() {
    case "$1" in
        one) echo 1 ;; two) echo 2 ;; three) echo 3 ;;
        four) echo 4 ;; five) echo 5 ;; six) echo 6 ;;
        seven) echo 7 ;; eight) echo 8 ;; nine) echo 9 ;;
        ten) echo 10 ;; [1-9]|10) echo "$1" ;; *) echo "" ;;
    esac
}

# Parse "last [N] commit[s]" pattern
parse_last_commits() {
    local args_str="$*"
    if [[ "$args_str" =~ ^last[[:space:]]+([a-z0-9]+)[[:space:]]+(commit|commits)$ ]]; then
        word_to_number "${BASH_REMATCH[1]}"
    fi
}

# Parse "against <branch>" pattern
parse_against_branch() {
    local args_str="$*"
    if [[ "$args_str" =~ ^against[[:space:]]+([^[:space:]]+)$ ]]; then
        echo "${BASH_REMATCH[1]}"
    fi
}

# Check for "last N commit(s)" pattern
COMMIT_NUM=$(parse_last_commits "$@")
if [[ -n "$COMMIT_NUM" ]]; then
    REVIEW_TYPE="commits"
    COMMIT_COUNT="$COMMIT_NUM"
    set --
fi

# Check for "against <branch>" pattern
AGAINST_BRANCH=$(parse_against_branch "$@")
if [[ -n "$AGAINST_BRANCH" ]]; then
    REVIEW_TYPE="base"
    BASE_BRANCH="$AGAINST_BRANCH"
    set --
fi

# Parse remaining arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -m|--model)
            MODEL="$2"
            REASONING=""
            shift 2
            ;;
        --base)
            REVIEW_TYPE="base"
            BASE_BRANCH="$2"
            shift 2
            ;;
        against)
            REVIEW_TYPE="base"
            BASE_BRANCH="$2"
            shift 2
            ;;
        last-commit|--last-commit)
            REVIEW_TYPE="commits"
            COMMIT_COUNT=1
            shift
            ;;
        last)
            if [[ "$2" == "commit" ]]; then
                REVIEW_TYPE="commits"
                COMMIT_COUNT=1
                shift 2
            else
                CUSTOM_PROMPT="$CUSTOM_PROMPT $1"
                shift
            fi
            ;;
        uncommitted)
            REVIEW_TYPE="uncommitted"
            shift
            ;;
        -*)
            echo "Warning: Unknown option '$1' ignored" >&2
            shift
            ;;
        *)
            CUSTOM_PROMPT="$CUSTOM_PROMPT $1"
            shift
            ;;
    esac
done

CUSTOM_PROMPT="${CUSTOM_PROMPT## }"
CUSTOM_PROMPT="${CUSTOM_PROMPT%% }"

# Verify codex is installed
if ! command -v codex &> /dev/null; then
    echo "Error: OpenAI Codex CLI is not installed."
    echo "To install: npm install -g @openai/codex && codex auth"
    exit 1
fi

# Build model options
MODEL_OPTS="-m $MODEL"
[[ -n "$REASONING" ]] && MODEL_OPTS="$MODEL_OPTS -c model_reasoning_effort=\"$REASONING\""

# Auto-fallback to last commit if no uncommitted changes
if [[ "$REVIEW_TYPE" == "uncommitted" ]] && [[ -z "$(git status --short 2>/dev/null)" ]]; then
    echo "No uncommitted changes found. Reviewing last commit instead."
    REVIEW_TYPE="commits"
    COMMIT_COUNT=1
fi

# Execute review
CODEX_FLAGS="$MODEL_OPTS --dangerously-bypass-approvals-and-sandbox"

if [[ "$REVIEW_TYPE" == "base" ]]; then
    echo "Reviewing current branch against $BASE_BRANCH..."
    if [[ -n "$CUSTOM_PROMPT" ]]; then
        eval "codex exec review --base \"$BASE_BRANCH\" $CODEX_FLAGS \"$CUSTOM_PROMPT\""
    else
        eval "codex exec review --base \"$BASE_BRANCH\" $CODEX_FLAGS"
    fi
elif [[ "$REVIEW_TYPE" == "commits" ]]; then
    if [[ "$COMMIT_COUNT" -eq 1 ]]; then
        echo "Reviewing last commit..."
        COMMIT_REF="HEAD"
    else
        echo "Reviewing last $COMMIT_COUNT commits..."
        COMMIT_REF="HEAD~$((COMMIT_COUNT-1))..HEAD"
    fi
    if [[ -n "$CUSTOM_PROMPT" ]]; then
        eval "codex exec review --commit $COMMIT_REF $CODEX_FLAGS \"$CUSTOM_PROMPT\""
    else
        eval "codex exec review --commit $COMMIT_REF $CODEX_FLAGS"
    fi
else
    echo "Reviewing uncommitted changes..."
    eval "codex exec review --uncommitted $CODEX_FLAGS"
fi
