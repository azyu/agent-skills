---
name: gemini-google-web-search
description: >-
  Google web search via Gemini CLI's `google_web_search` tool. Use when the
  user needs current web information, recent news, latest versions, live
  research, or broader web context beyond the local repository and model
  knowledge.
---

# Gemini Google Web Search

Use Gemini CLI's `google_web_search` tool when the task requires current information from the public web.

## Use This Skill When

- The user asks for latest or current information
- The user needs recent news, trends, releases, prices, or other time-sensitive facts
- The user asks for general web research or broader ecosystem context
- Local files, repository context, or GitHub data are not enough to answer the request

## Workflow

1. Extract the search query from `$ARGUMENTS`.
2. Run Gemini CLI with `google_web_search`.
3. If JSON output is empty or malformed, retry without JSON output.
4. Return the result with source URLs, and add a short summary or translation only if helpful.

## Command Patterns

```bash
gemini -m gemini-2.5-flash -p "Use google_web_search to find: $QUERY. Provide a comprehensive summary with source URLs." --output-format json 2>/dev/null | jq -r '.response'
```

```bash
gemini -m gemini-2.5-flash -p "Use google_web_search to find: $QUERY. Provide a comprehensive summary with source URLs." 2>/dev/null
```

## Notes

- Free tier: 60 req/min, 1,000 req/day
- Typical response time: 5-15 seconds with web search
- The result is Gemini's synthesized summary plus source URLs
- `gemini` must be available in `PATH` such as `/opt/homebrew/bin/gemini`
