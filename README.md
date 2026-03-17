# agent-skills

Personal skills collection for the `skills` CLI, organized in the same repository-style layout used by public skill catalogs.

## Install

List available skills from GitHub:

```bash
npx skills add azyu/agent-skills --list
```

Install a specific skill:

```bash
npx skills add azyu/agent-skills --skill kobus-bus-search
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
- `shell-script`: create, edit, and review shell scripts with shell-specific guidance
- `kobus-bus-search`: query Kobus bus schedules and remaining seats
<img width="460" height="608" alt="스크린샷 2026-03-17 오후 1 53 51" src="https://github.com/user-attachments/assets/061536de-cee0-45fd-854e-7fb3f7da80a6" />

## License

MIT
