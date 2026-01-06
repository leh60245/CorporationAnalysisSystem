"""
DART Agent 테스트 스크립트
DART API 연동, 보고서 검색, 섹션 추출 테스트

사용법:
    python tests/test_dart_agent.py              # 삼성전자 테스트
    python tests/test_dart_agent.py --stock 000660  # SK하이닉스 테스트
    python tests/test_dart_agent.py --functions  # 기능 테스트만
"""
import sys
import argparse
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from src.core.dart_agent import DartReportAgent


def test_initialization():
    """에이전트 초기화 테스트"""
    print("=" * 80)
    print("🧪 DART Agent 초기화 테스트")
    print("=" * 80)

    try:
        agent = DartReportAgent()
        print(f"✅ 에이전트 초기화 성공")
        print(f"   - 기업 리스트 수: {len(agent.corp_list):,}개")
        return agent
    except Exception as e:
        print(f"❌ 초기화 실패: {e}")
        return None


def test_corp_search(agent, stock_code="005930"):
    """기업 검색 테스트"""
    print("\n" + "=" * 80)
    print(f"🧪 기업 검색 테스트 (종목코드: {stock_code})")
    print("=" * 80)

    try:
        corp = agent.get_corp_by_stock_code(stock_code)

        if corp:
            print(f"✅ 기업 검색 성공")
            print(f"   - 기업명: {corp.corp_name}")
            print(f"   - 법인코드: {corp.corp_code}")
            print(f"   - 종목코드: {corp.stock_code}")
            return corp
        else:
            print(f"❌ 종목코드 {stock_code}에 해당하는 기업을 찾을 수 없습니다")
            return None

    except Exception as e:
        print(f"❌ 기업 검색 실패: {e}")
        return None


def test_report_search(agent, corp):
    """보고서 검색 테스트"""
    print("\n" + "=" * 80)
    print(f"🧪 사업보고서 검색 테스트")
    print("=" * 80)

    try:
        report = agent.get_annual_report(corp.corp_code)

        if report:
            print(f"✅ 보고서 검색 성공")
            print(f"   - 보고서명: {report.report_nm}")
            print(f"   - 접수번호: {report.rcept_no}")
            print(f"   - 접수일자: {report.rcept_dt}")
            return report
        else:
            print(f"❌ 사업보고서를 찾을 수 없습니다")
            return None

    except Exception as e:
        print(f"❌ 보고서 검색 실패: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_section_extraction(agent, report):
    """섹션 추출 테스트 (기본 방식)"""
    print("\n" + "=" * 80)
    print(f"🧪 섹션 추출 테스트 (기본)")
    print("=" * 80)

    try:
        sections = agent.extract_target_sections(report)

        if sections:
            print(f"✅ 섹션 추출 성공: {len(sections)}개 섹션")

            for section in sections:
                print(f"\n   📑 {section['section_name']}")
                print(f"      - 텍스트 길이: {len(section['text']):,} 자")
                print(f"      - 테이블 수: {len(section['tables'])}개")

            return sections
        else:
            print(f"❌ 추출 가능한 섹션이 없습니다")
            return None

    except Exception as e:
        print(f"❌ 섹션 추출 실패: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_advanced_extraction(agent, report):
    """고급 섹션 추출 테스트 (테이블/텍스트 분리)"""
    print("\n" + "=" * 80)
    print(f"🧪 고급 섹션 추출 테스트 (테이블/텍스트 분리)")
    print("=" * 80)

    try:
        sections = agent.extract_target_sections_advanced(report)

        if sections:
            print(f"✅ 고급 추출 성공: {len(sections)}개 섹션")

            for section in sections:
                chapter = section['chapter']
                parsed_count = len(section['sections'])
                table_count = len(section['tables'])

                print(f"\n   📑 {chapter}")
                print(f"      - 파싱된 섹션: {parsed_count}개")
                print(f"      - 테이블: {table_count}개")
                print(f"      - 페이지: {section['page_count']}개")

            return sections
        else:
            print(f"❌ 추출 가능한 섹션이 없습니다")
            return None

    except Exception as e:
        print(f"❌ 고급 섹션 추출 실패: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_chunking(agent, sections):
    """청킹 테스트"""
    print("\n" + "=" * 80)
    print(f"🧪 청킹 테스트")
    print("=" * 80)

    try:
        if not sections:
            print("⚠️ 테스트할 섹션이 없습니다")
            return False

        # 첫 번째 섹션만 테스트
        section = sections[0]

        # 고급 청킹
        if 'sections' in section:  # 고급 추출 방식
            chunks = agent.chunk_section_advanced(section)
            print(f"✅ 고급 청킹 성공")
        else:  # 기본 추출 방식
            chunks = agent.chunk_section(section)
            print(f"✅ 기본 청킹 성공")

        print(f"   - 전체 청크 수: {len(chunks)}개")

        # 샘플 출력
        if chunks:
            sample = chunks[0]
            print(f"\n   샘플 청크 정보:")
            print(f"   - Chapter: {sample.get('chapter', 'N/A')}")
            print(f"   - Section: {sample.get('section_name', 'N/A')}")
            print(f"   - Sub-Section: {sample.get('sub_section', 'N/A')}")
            print(f"   - 내용 길이: {len(sample['content'])} 자")
            print(f"   - 테이블 포함: {len(sample.get('tables', [])) > 0}")

        return True

    except Exception as e:
        print(f"❌ 청킹 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_function_tests():
    """기능 테스트만 실행"""
    print("\n" + "=" * 80)
    print("🧪 DART Agent 기능 테스트")
    print("=" * 80 + "\n")

    results = []

    # 1. 초기화
    agent = test_initialization()
    results.append(("초기화", agent is not None))

    if not agent:
        print("\n❌ 초기화 실패로 테스트 중단")
        return False

    # 2. 기업 검색
    corp = test_corp_search(agent, "005930")
    results.append(("기업 검색", corp is not None))

    if not corp:
        print("\n❌ 기업 검색 실패로 테스트 중단")
        return False

    # 3. 보고서 검색
    report = test_report_search(agent, corp)
    results.append(("보고서 검색", report is not None))

    # 결과 요약
    print("\n" + "=" * 80)
    print("📊 기능 테스트 결과")
    print("=" * 80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    print(f"\n총 {passed}/{total} 테스트 통과")

    return passed == total


def run_full_test(stock_code="005930", use_advanced=True):
    """전체 테스트 실행"""
    print("\n" + "=" * 80)
    print(f"🧪 DART Agent 전체 테스트 (종목코드: {stock_code})")
    print("=" * 80 + "\n")

    results = []

    # 1. 초기화
    agent = test_initialization()
    results.append(("초기화", agent is not None))

    if not agent:
        return False

    # 2. 기업 검색
    corp = test_corp_search(agent, stock_code)
    results.append(("기업 검색", corp is not None))

    if not corp:
        return False

    # 3. 보고서 검색
    report = test_report_search(agent, corp)
    results.append(("보고서 검색", report is not None))

    if not report:
        return False

    # 4. 섹션 추출
    if use_advanced:
        sections = test_advanced_extraction(agent, report)
        results.append(("고급 섹션 추출", sections is not None))
    else:
        sections = test_section_extraction(agent, report)
        results.append(("섹션 추출", sections is not None))

    if not sections:
        return False

    # 5. 청킹
    chunking_success = test_chunking(agent, sections)
    results.append(("청킹", chunking_success))

    # 결과 요약
    print("\n" + "=" * 80)
    print("📊 전체 테스트 결과")
    print("=" * 80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    print(f"\n총 {passed}/{total} 테스트 통과")

    return passed == total


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DART Agent 테스트")
    parser.add_argument("--stock", type=str, default="005930", help="종목코드 (기본: 005930 삼성전자)")
    parser.add_argument("--functions", action="store_true", help="기능 테스트만 실행")
    parser.add_argument("--basic", action="store_true", help="기본 추출 방식 사용")

    args = parser.parse_args()

    if args.functions:
        success = run_function_tests()
    else:
        success = run_full_test(stock_code=args.stock, use_advanced=not args.basic)

    sys.exit(0 if success else 1)
