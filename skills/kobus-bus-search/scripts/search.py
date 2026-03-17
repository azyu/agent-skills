import sys
import re
import argparse
import json
from datetime import datetime
from scrapling.fetchers import Fetcher

TERMINALS = {
    "진주": "722",
    "용인신갈": "111",
    "용인신갈(고가밑)": "111",
    "서울경부": "010",
    "서울": "010",
    "동서울": "032",
    "부산": "700",
    "대구": "801",
    "동대구": "801",
    "광주": "500",
    "대전": "300",
    "대전복합": "300",
    "전주": "602",
    "천안": "310",
    "청주": "400"
}

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

    depr_cd = TERMINALS.get(depr_nm)
    arvl_cd = TERMINALS.get(arvl_nm)

    if not depr_cd or not arvl_cd:
        exit_error(f"❌ 지원하지 않거나 알 수 없는 터미널입니다. 지원 목록: {', '.join(TERMINALS.keys())}")

    try:
        now = datetime.now()
        year = now.year
        
        nums = re.findall(r'\d+', date_str)
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
        weekdays = ['월', '화', '수', '목', '금', '토', '일']
        wd = weekdays[target_dt.weekday()]
        date_formatted = f"{target_dt.year}. {target_dt.month}. {target_dt.day}. {wd}"
        
    except Exception as e:
        exit_error(f"❌ 날짜 처리 오류: {e}")

    log(f"🔍 검색: {depr_nm}({depr_cd}) -> {arvl_nm}({arvl_cd}) [{target_dt.year}년 {target_dt.month}월 {target_dt.day}일 {wd}요일]")

    init_url = 'https://m.kobus.co.kr/mrs/rotinf.do'
    try:
        init_page = Fetcher.get(init_url, stealthy_headers=False)
        cookies = init_page.cookies
    except Exception as e:
        exit_error(f"❌ 사이트 초기 접속 오류 (쿠키 발급 실패): {e}")

    url = 'https://m.kobus.co.kr/mrs/alcnSrch.do'
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://m.kobus.co.kr',
        'Referer': init_url,
    }
    data = {
        'deprCd': depr_cd, 'deprNm': depr_nm,
        'arvlCd': arvl_cd, 'arvlNm': arvl_nm,
        'pathDvs': 'sngl', 'pathStep': '1', 'pathStepRtn': '1',
        'crchDeprArvlYn': 'Y',
        'deprDtm': target_date, 'deprDtmAll': date_formatted,
        'arvlDtm': target_date, 'arvlDtmAll': date_formatted,
        'busClsCd': '0', 'prmmDcYn': 'N', 'takeTime': '0'
    }

    try:
        response = Fetcher.post(url, headers=headers, cookies=cookies, data=data, stealthy_headers=False)
    except Exception as e:
        exit_error(f"❌ 네트워크 통신 오류: {e}")

    rows = response.css('p[role="row"]')
    
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
        time_txt = row.css('.start_time::text').get(default="").strip()
        grade_txt = row.css('.grade::text').get(default="-").replace('\n', ' ').strip()
        remain_txt = row.css('.remain::text').get(default="0").strip()
        status_txt = row.css('.status::text').get(default="").replace('\n', '').strip()

        if not time_txt:
            continue
        
        grade_simple = grade_txt.split('(')[0].strip()
        
        remain_num = int(re.sub(r'[^0-9]', '', remain_txt)) if re.sub(r'[^0-9]', '', remain_txt) else 0

        results.append({
            "time": time_txt,
            "grade": grade_simple,
            "remain_seats": remain_num,
            "status": status_txt
        })
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
