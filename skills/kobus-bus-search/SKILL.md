---
name: kobus-bus-search
description: Query real-time Kobus express bus schedules and remaining seats from kobus.co.kr. Use when a user asks for high-speed bus departure times, seat availability, or route lookups between supported Korean terminals.
---

# Kobus Bus Search

Use this skill when the user wants to check Kobus express bus departures or remaining seats between supported terminals.

## Workflow

1. Confirm the departure terminal, arrival terminal, and travel date.
2. Prefer the official Kobus terminal name when the user already knows it, but short aliases like `서울`, `광주`, `대전`, `전주`, `청주`, and `용인신갈` are also accepted.
3. Run `scripts/search.py`.
4. Use `--json` when another tool or agent needs structured output.

## Commands

```bash
# Human-readable table output
python3 scripts/search.py "용인신갈" "진주" "20260214"
python3 scripts/search.py "동서울" "대구" "3월 20일"
python3 scripts/search.py "서울" "부산" "20260214"
python3 scripts/search.py "광주" "센트럴시티" "4월 2일"

# Structured output for downstream parsing
python3 scripts/search.py "서울경부" "부산" "2월 14일" --json
```

## Response Samples

Human-readable Markdown bullet output:

```text
- 출발지 자동 보정: 서울 -> 서울경부
- 서울경부(010) -> 부산(700) | 2026년 2월 14일 토요일
- 09:20 | 우등 | 26석 | 선택
- 10:00 | 프리미엄 | 8석 | 선택
- 11:10 | 일반 | 0석 | 매진
```

Structured JSON output:

```json
[
  {
    "time": "09 : 20",
    "grade": "우등",
    "remain_seats": 26,
    "status": "선택"
  }
]
```

When `--json` is set, the script prints only JSON to stdout.

Unsupported terminal example:

```json
{"error": "❌ 지원하지 않거나 모호한 터미널입니다. 추천: 용인유림, 용인"}
```

No results example in JSON mode:

```json
[]
```

## Matching Strategy

The script resolves terminals in this order:

1. Exact match against official Kobus terminal names
2. Alias match for common short names
3. Normalized match that ignores spaces and punctuation such as parentheses or `·`
4. Fuzzy match against the live Kobus terminal list

Examples:

- `서울` -> `서울경부`
- `광주` -> `광주(유·스퀘어)`
- `대전` -> `대전복합`
- `전주` -> `전주고속터미널`
- `청주` -> `청주고속터미널`
- `부산사상` -> `서부산(사상)`
- `센트럴시티서울` -> `센트럴시티(서울)`

If the best match is not clearly better than the next candidates, the script does not guess. It returns an error with suggested official terminal names instead.

## Terminal Matching

- The script reads Kobus terminal candidates from `https://m.kobus.co.kr/mrs/rotinf.do` at runtime, then falls back to a small built-in map for common terminals.
- Common aliases such as `서울`, `광주`, `대전`, `전주`, `청주`, and `용인신갈` are resolved to the corresponding official Kobus names automatically.
- If the input is close but not exact, the script attempts fuzzy matching. If the result is still ambiguous, it returns suggested terminals instead of guessing.

## JSON Usage

- `--json` prints only JSON on success.
- On terminal resolution or date parsing failures, `--json` returns an object with an `error` field.
- This mode is appropriate when another tool needs to parse the output without human-readable log lines.

## Text Output

- The default non-JSON mode is optimized for Slack and Telegram paste-in use.
- The script prints a flat Markdown bullet list instead of a fixed-width table.
- Auto-corrections appear first, followed by one summary bullet and one bullet per departure.
- This avoids alignment issues in chat clients that do not preserve monospaced spacing consistently.

## Operational Notes

- The script currently uses `curl` to fetch the Kobus terminal list because the mobile site TLS handshake is more reliable that way in this environment.
- The actual schedule lookup still uses `scrapling` for cookie handling and HTML parsing.
- Kobus terminal labels can differ from colloquial names. Prefer the site label when possible if fuzzy matching produces ambiguous recommendations.

## Notes

- The script targets `https://m.kobus.co.kr`.
- `kobus` covers express bus routes. Some intercity routes may not be available.
- Date input accepts `YYYYMMDD` or `M월 D일`. If `M월 D일` is already in the past for the current year, the script rolls it to the next year.
