"""
DART 보고서 구조 탐색 스크립트
- 사업보고서의 실제 섹션 구조를 확인하여 청킹 전략 수립에 활용
"""
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import dart_fss as dart
from config import DART_API_KEY, REPORT_SEARCH_CONFIG
import json


def explore_report_structure(stock_code: str = "005930"):
    """
    특정 기업의 사업보고서 구조를 탐색합니다.

    Args:
        stock_code: 종목코드 (기본값: 삼성전자 005930)
    """
    # DART API 설정
    dart.set_api_key(api_key=DART_API_KEY)

    print("=" * 60)
    print("📊 DART 사업보고서 구조 탐색")
    print("=" * 60)

    # 1. 기업 리스트에서 대상 기업 찾기
    print("\n🔄 기업 리스트 로딩 중...")
    corp_list = dart.get_corp_list()

    target_corp = None
    for corp in corp_list:
        if corp.stock_code == stock_code:
            target_corp = corp
            break

    if not target_corp:
        print(f"❌ 종목코드 {stock_code}에 해당하는 기업을 찾을 수 없습니다.")
        return

    print(f"✅ 대상 기업: {target_corp.corp_name} ({target_corp.stock_code})")
    print(f"   법인코드: {target_corp.corp_code}")

    # 2. 사업보고서 검색
    print(f"\n🔍 사업보고서 검색 중 (시작일: {REPORT_SEARCH_CONFIG['bgn_de']})...")

    try:
        search_results = dart.search(
            corp_code=target_corp.corp_code,
            bgn_de=REPORT_SEARCH_CONFIG['bgn_de'],
            pblntf_detail_ty=REPORT_SEARCH_CONFIG['pblntf_detail_ty']
        )
    except Exception as e:
        print(f"❌ 검색 실패: {e}")
        return

    if not search_results:
        print("❌ 사업보고서를 찾을 수 없습니다.")
        return

    report = search_results[0]
    print(f"✅ 보고서 발견: {report.report_nm}")
    print(f"   접수번호: {report.rcept_no}")
    print(f"   접수일자: {report.rcept_dt}")

    # 3. 보고서 전체 구조 탐색
    print("\n" + "=" * 60)
    print("📑 보고서 섹션 구조")
    print("=" * 60)

    # find_all()로 전체 페이지 목록 가져오기
    try:
        all_pages = report.find_all()

        print(f"\n📋 전체 페이지 수: {len(all_pages.get('pages', []))}")

        # 각 페이지의 제목/타입 정보 출력
        sections_info = []
        for i, page in enumerate(all_pages.get('pages', [])):
            page_info = {
                "index": i,
                "title": getattr(page, 'title', 'N/A'),
                "type": type(page).__name__
            }

            # 추가 속성이 있다면 확인
            if hasattr(page, 'ele_id'):
                page_info['ele_id'] = page.ele_id
            if hasattr(page, 'dcm_no'):
                page_info['dcm_no'] = page.dcm_no

            sections_info.append(page_info)
            print(f"  [{i:3d}] {page_info['title']}")

    except Exception as e:
        print(f"⚠️ find_all() 실행 오류: {e}")
        all_pages = None

    # 4. 핵심 섹션 개별 탐색
    print("\n" + "=" * 60)
    print("🎯 핵심 섹션 탐색")
    print("=" * 60)

    target_keywords = [
        "회사의 개요",
        "사업의 개요",
        "사업의 내용",
        "재무에 관한 사항",
        "재무제표",
        "이사의 경영진단",
        "주주에 관한 사항"
    ]

    found_sections = {}

    for keyword in target_keywords:
        print(f"\n🔍 '{keyword}' 검색 중...")
        try:
            result = report.find_all(includes=keyword)
            pages = result.get('pages', [])

            if pages:
                print(f"   ✅ {len(pages)}개 페이지 발견")
                found_sections[keyword] = {
                    "page_count": len(pages),
                    "first_page_title": getattr(pages[0], 'title', 'N/A') if pages else None
                }

                # 첫 페이지 일부 내용 미리보기
                if pages:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(pages[0].html, 'html.parser')
                    text = soup.get_text()[:300].strip()
                    print(f"   📄 미리보기: {text[:100]}...")
            else:
                print(f"   ❌ 해당 섹션 없음")
                found_sections[keyword] = None

        except Exception as e:
            print(f"   ⚠️ 검색 오류: {e}")
            found_sections[keyword] = {"error": str(e)}

    # 5. 결과 저장
    output_path = Path("data/report_structure.json")
    output_path.parent.mkdir(exist_ok=True)

    result_data = {
        "company": {
            "name": target_corp.corp_name,
            "stock_code": target_corp.stock_code,
            "corp_code": target_corp.corp_code
        },
        "report": {
            "title": report.report_nm,
            "rcept_no": report.rcept_no,
            "rcept_dt": report.rcept_dt
        },
        "total_pages": len(all_pages.get('pages', [])) if all_pages else 0,
        "sections_found": found_sections
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print(f"💾 탐색 결과 저장: {output_path}")
    print("=" * 60)

    # 6. 요약
    print("\n📊 요약:")
    print(f"   - 전체 페이지 수: {result_data['total_pages']}")
    print(f"   - 발견된 핵심 섹션:")
    for keyword, info in found_sections.items():
        if info and not isinstance(info, dict):
            continue
        if info and 'page_count' in info:
            print(f"     ✅ {keyword}: {info['page_count']}페이지")
        else:
            print(f"     ❌ {keyword}: 없음")

    return result_data


if __name__ == "__main__":
    # 삼성전자로 테스트
    explore_report_structure("005930")
