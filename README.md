# agent-skills

Personal skills collection for the `skills` CLI, organized in the same repository-style layout used by public skill catalogs.

## Install

List available skills from GitHub:

```bash
npx skills add azyu/agent-skills --list
```

Install a specific skill:

```bash
npx skills add azyu/agent-skills kobus-bus-search
```

## Repository Layout

Each skill lives under `skills/<skill-name>/SKILL.md`.

```text
skills/
  gemini-google-web-search/
    SKILL.md
  instruction-writer/
    SKILL.md
  kobus-bus-search/
    SKILL.md
  shell-script/
    SKILL.md
```

## Available Skills

- `gemini-google-web-search`: current web research through Gemini CLI's `google_web_search` tool
- `instruction-writer`: rewrite prompts and instruction files into concrete, model-friendly rules
- `kobus-bus-search`: query Kobus bus schedules and remaining seats
- `shell-script`: create, edit, and review shell scripts with shell-specific guidance

## Development

This repository now uses `skills/` as the canonical root for distributable skills. If you add a new skill, place it under `skills/<name>/`.

## License

MIT
