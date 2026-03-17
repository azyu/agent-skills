import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from difflib import SequenceMatcher

from scrapling.fetchers import Fetcher

FALLBACK_TERMINALS = {
    "광주(유·스퀘어)": "500",
    "대전복합": "300",
    "동대구": "801",
    "동서울": "032",
    "부산": "700",
    "서울경부": "010",
    "센트럴시티(서울)": "021",
    "서부산(사상)": "703",
    "용인신갈(고가밑)": "111",
    "전주고속터미널": "602",
    "진주": "722",
    "천안": "310",
    "청주고속터미널": "400",
}

TERMINAL_ALIASES = {
    "광주": "광주(유·스퀘어)",
    "대구": "동대구",
    "대전": "대전복합",
    "부산사상": "서부산(사상)",
    "서울": "서울경부",
    "센트럴시티": "센트럴시티(서울)",
    "용인신갈": "용인신갈(고가밑)",
    "전주": "전주고속터미널",
    "전주고속": "전주고속터미널",
    "청주": "청주고속터미널",
}

TERMINAL_LIST_URL = "https://m.kobus.co.kr/mrs/rotinf.do"
TERMINAL_PATTERN = re.compile(r"fn(?:Depr|Arvl)Chc\('(?P<code>\d+)','(?P<name>[^']+)'")


def normalize_terminal_name(name):
    return re.sub(r"[\s\-\(\)·\.,_/]", "", name).lower()


def parse_terminal_candidates(html):
    candidates = {}
    for match in TERMINAL_PATTERN.finditer(html):
        candidates[match.group("name")] = match.group("code")
    return candidates


def fetch_terminal_candidates():
    # Kobus mobile pages currently negotiate more reliably through curl than Python stdlib HTTPS.
    cmd = ["curl", "-k", "-L", "-A", "Mozilla/5.0", "-s", TERMINAL_LIST_URL]
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        return {}
    return parse_terminal_candidates(result.stdout)


def merge_terminal_candidates():
    candidates = dict(FALLBACK_TERMINALS)
    candidates.update(fetch_terminal_candidates())
    return candidates


def pick_preferred_terminal(entries):
    return sorted(entries, key=lambda entry: (len(entry[0]), entry[0]))[0]


def resolve_terminal(name, candidates):
    query = name.strip()
    if not query:
        raise ValueError("터미널 이름이 비어 있습니다.")

    alias_target = TERMINAL_ALIASES.get(query)
    if alias_target and alias_target in candidates:
        return alias_target, candidates[alias_target]

    if query in candidates:
        return query, candidates[query]

    normalized_query = normalize_terminal_name(query)
    if not normalized_query:
        raise ValueError("터미널 이름이 비어 있습니다.")

    normalized_aliases = {
        normalize_terminal_name(alias): target
        for alias, target in TERMINAL_ALIASES.items()
        if target in candidates
    }
    alias_target = normalized_aliases.get(normalized_query)
    if alias_target:
        return alias_target, candidates[alias_target]

    normalized_candidates = {}
    for terminal_name, terminal_code in candidates.items():
        normalized_name = normalize_terminal_name(terminal_name)
        normalized_candidates.setdefault(normalized_name, []).append((terminal_name, terminal_code))

    exact_entries = normalized_candidates.get(normalized_query)
    if exact_entries:
        return pick_preferred_terminal(exact_entries)

    scored = []
    for normalized_name, entries in normalized_candidates.items():
        score = SequenceMatcher(None, normalized_query, normalized_name).ratio()
        if normalized_query in normalized_name or normalized_name in normalized_query:
            score += 0.12
        scored.append((score, pick_preferred_terminal(entries)))

    scored.sort(key=lambda item: (-item[0], len(item[1][0]), item[1][0]))
    best_score, best_match = scored[0]
    second_score = scored[1][0] if len(scored) > 1 else 0

    if best_score >= 0.78 and best_score - second_score >= 0.08:
        return best_match

    suggestions = [terminal_name for score, (terminal_name, _) in scored if score >= 0.45][:3]
    if suggestions:
        raise ValueError("지원하지 않거나 모호한 터미널입니다. 추천: " + ", ".join(suggestions))
    raise ValueError("지원하지 않거나 알 수 없는 터미널입니다.")


def search_bus(depr_nm, arvl_nm, date_str, output_json=False):
    def log(msg):
        if not output_json:
            print(msg)

    def exit_error(msg):
        if output_json:
            print(json.dumps({"error": msg}, ensure_ascii=False))
        else:
            print(msg)
        sys.exit(1)

    terminal_candidates = merge_terminal_candidates()

    try:
        resolved_depr_nm, depr_cd = resolve_terminal(depr_nm, terminal_candidates)
        resolved_arvl_nm, arvl_cd = resolve_terminal(arvl_nm, terminal_candidates)
    except ValueError as exc:
        exit_error(f"❌ {exc}")

    try:
        now = datetime.now()
        year = now.year

        nums = re.findall(r"\d+", date_str)
        if len(nums) == 1 and len(nums[0]) == 8:
            year = int(nums[0][:4])
            month = int(nums[0][4:6])
            day = int(nums[0][6:8])
            target_dt = datetime(year, month, day)
        elif len(nums) >= 2:
            month = int(nums[0])
            day = int(nums[1])
            if month < now.month or (month == now.month and day < now.day):
                year += 1
            target_dt = datetime(year, month, day)
        else:
            exit_error("❌ 날짜 형식을 알 수 없습니다. (예: 20260214 또는 2월 14일)")

        target_date = target_dt.strftime("%Y%m%d")
        weekdays = ["월", "화", "수", "목", "금", "토", "일"]
        wd = weekdays[target_dt.weekday()]
        date_formatted = f"{target_dt.year}. {target_dt.month}. {target_dt.day}. {wd}"

    except Exception as e:
        exit_error(f"❌ 날짜 처리 오류: {e}")

    if resolved_depr_nm != depr_nm:
        log(f"↪ 출발지 자동 보정: {depr_nm} -> {resolved_depr_nm}")
    if resolved_arvl_nm != arvl_nm:
        log(f"↪ 도착지 자동 보정: {arvl_nm} -> {resolved_arvl_nm}")

    log(
        f"🔍 검색: {resolved_depr_nm}({depr_cd}) -> {resolved_arvl_nm}({arvl_cd}) "
        f"[{target_dt.year}년 {target_dt.month}월 {target_dt.day}일 {wd}요일]"
    )

    init_url = "https://m.kobus.co.kr/mrs/rotinf.do"
    try:
        init_page = Fetcher.get(init_url, stealthy_headers=False)
        cookies = init_page.cookies
    except Exception as e:
        exit_error(f"❌ 사이트 초기 접속 오류 (쿠키 발급 실패): {e}")

    url = "https://m.kobus.co.kr/mrs/alcnSrch.do"
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://m.kobus.co.kr",
        "Referer": init_url,
    }
    data = {
        "deprCd": depr_cd,
        "deprNm": resolved_depr_nm,
        "arvlCd": arvl_cd,
        "arvlNm": resolved_arvl_nm,
        "pathDvs": "sngl",
        "pathStep": "1",
        "pathStepRtn": "1",
        "crchDeprArvlYn": "Y",
        "deprDtm": target_date,
        "deprDtmAll": date_formatted,
        "arvlDtm": target_date,
        "arvlDtmAll": date_formatted,
        "busClsCd": "0",
        "prmmDcYn": "N",
        "takeTime": "0",
    }

    try:
        response = Fetcher.post(url, headers=headers, cookies=cookies, data=data, stealthy_headers=False)
    except Exception as e:
        exit_error(f"❌ 네트워크 통신 오류: {e}")

    rows = response.css("p[role=\"row\"]")

    if not rows:
        if output_json:
            print(json.dumps([]))
        else:
            print("❌ 배차 정보가 없거나 파싱에 실패했습니다. (매진이거나 해당 일자 운행이 없을 수 있습니다)")
        return

    results = []
    log(f"\n{'출발':<6} | {'등급':<10} | {'잔여석':<6} | {'상태'}")
    log("-" * 45)

    for row in rows:
        time_txt = row.css(".start_time::text").get(default="").strip()
        grade_txt = row.css(".grade::text").get(default="-").replace("\n", " ").strip()
        remain_txt = row.css(".remain::text").get(default="0").strip()
        status_txt = row.css(".status::text").get(default="").replace("\n", "").strip()

        if not time_txt:
            continue

        grade_simple = grade_txt.split("(")[0].strip()
        remain_digits = re.sub(r"[^0-9]", "", remain_txt)
        remain_num = int(remain_digits) if remain_digits else 0

        results.append(
            {
                "time": time_txt,
                "grade": grade_simple,
                "remain_seats": remain_num,
                "status": status_txt,
            }
        )
        log(f"{time_txt:<6} | {grade_simple:<10} | {remain_txt:<6} | {status_txt}")

    if not results:
        log("\n(조회된 배차가 없습니다.)")

    if output_json:
        print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kobus Bus Search")
    parser.add_argument("depr", help="출발지 (예: 용인신갈, 진주)")
    parser.add_argument("arvl", help="도착지 (예: 진주, 용인신갈)")
    parser.add_argument("date", help="날짜 (예: 20260214, '2월 14일')")
    parser.add_argument("--json", action="store_true", help="JSON 형식으로 결과 출력 (AI 처리용)")

    args = parser.parse_args()
    search_bus(args.depr, args.arvl, args.date, args.json)
