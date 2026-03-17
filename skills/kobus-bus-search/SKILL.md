---
name: kobus-bus-search
description: Query real-time Kobus express bus schedules and remaining seats from kobus.co.kr. Use when a user asks for high-speed bus departure times, seat availability, or route lookups between supported Korean terminals.
---

# Kobus Bus Search

Use this skill when the user wants to check Kobus express bus departures or remaining seats between supported terminals.

## Workflow

1. Confirm the departure terminal, arrival terminal, and travel date.
2. Run `scripts/search.py`.
3. Use `--json` when another tool or agent needs structured output.

## Commands

```bash
# Human-readable table output
python3 scripts/search.py "용인신갈" "진주" "20260214"
python3 scripts/search.py "동서울" "대구" "3월 20일"

# Structured output for downstream parsing
python3 scripts/search.py "서울경부" "부산" "2월 14일" --json
```

## Response Samples

Human-readable table output:

```text
🔍 검색: 서울경부(010) -> 부산(700) [2026년 2월 14일 토요일]

출발   | 등급         | 잔여석   | 상태
---------------------------------------------
09 : 20 | 우등         | 26 석    | 선택
10 : 00 | 프리미엄      | 8 석     | 선택
11 : 10 | 일반         | 0 석     | 매진
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
{"error": "❌ 지원하지 않거나 알 수 없는 터미널입니다. 지원 목록: 진주, 용인신갈, 용인신갈(고가밑), 서울경부, 서울, 동서울, 부산, 대구, 동대구, 광주, 대전, 대전복합, 전주, 천안, 청주"}
```

No results example in JSON mode:

```json
[]
```

## Supported Terminals

- 진주
- 용인신갈
- 서울경부
- 동서울
- 부산
- 대구
- 동대구
- 광주
- 대전
- 전주
- 천안
- 청주

Add more terminals in `scripts/search.py` by extending the `TERMINALS` dictionary.

## Notes

- The script targets `https://m.kobus.co.kr`.
- `kobus` covers express bus routes. Some intercity routes may not be available.
- Date input accepts `YYYYMMDD` or `M월 D일`. If `M월 D일` is already in the past for the current year, the script rolls it to the next year.
