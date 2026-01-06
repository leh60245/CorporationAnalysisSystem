"""
순차적 블록 처리 방식 테스트 스크립트
"""
import sys
sys.path.insert(0, 'C:/Users/kkh60/PycharmProjects/CorporationAnalysis')

from src.core.dart_agent import DartReportAgent
from src.core.db_manager import DBManager
from src.core.pipeline import DataPipeline


def test_table_to_markdown():
    """테이블 -> Markdown 변환 테스트"""
    print("\n" + "=" * 50)
    print("🧪 테스트 1: 테이블 -> Markdown 변환")
    print("=" * 50)

    from bs4 import BeautifulSoup

    html = """
    <table>
        <tr><th>구분</th><th>2024년</th><th>2023년</th></tr>
        <tr><td>매출액</td><td>100억</td><td>80억</td></tr>
        <tr><td>영업이익</td><td>20억</td><td>15억</td></tr>
    </table>
    """

    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table')

    agent = DartReportAgent()
    markdown, metadata = agent.convert_table_to_markdown(table)

    print("\n📊 Markdown 테이블:")
    print(markdown)
    print("\n📋 메타데이터:")
    print(metadata)

    return bool(markdown)


def test_db_schema():
    """DB 스키마 테스트 (새로운 컬럼 확인)"""
    print("\n" + "=" * 50)
    print("🧪 테스트 2: DB 스키마 확인")
    print("=" * 50)

    with DBManager() as db:
        # 테이블 초기화 (새 스키마 적용)
        db.reset_db()
        print("✅ DB 스키마 초기화 완료")

        # 테스트 데이터 삽입
        company_id = db.insert_company(
            name="테스트기업",
            corp_code="00000000",
            stock_code="000000"
        )
        print(f"✅ 기업 등록: ID={company_id}")

        report_id = db.insert_report(company_id, {
            "title": "테스트 사업보고서",
            "rcept_no": "20240000000000",
            "rcept_dt": "20240101"
        })
        print(f"✅ 리포트 등록: ID={report_id}")

        # 순차적 블록 저장 테스트
        test_blocks = [
            {
                "chunk_type": "text",
                "section_path": "II. 사업의 내용 > 1. 사업의 개요",
                "content": "당사는 반도체 제조 전문기업입니다.",
                "sequence_order": 0
            },
            {
                "chunk_type": "table",
                "section_path": "II. 사업의 내용 > 1. 사업의 개요",
                "content": "| 구분 | 2024년 | 2023년 |\n| --- | --- | --- |\n| 매출액 | 100억 | 80억 |",
                "sequence_order": 1,
                "table_metadata": {"rows": 2, "cols": 3}
            },
            {
                "chunk_type": "text",
                "section_path": "II. 사업의 내용 > 2. 주요 제품",
                "content": "주요 제품은 메모리 반도체입니다.",
                "sequence_order": 2
            }
        ]

        saved = db.insert_materials_batch(report_id, test_blocks)
        print(f"✅ 블록 저장: {saved}개")

        # 저장된 데이터 확인
        materials = db.get_materials_by_report(report_id)
        print(f"\n📦 저장된 블록 목록:")
        for m in materials:
            print(f"  [{m['sequence_order']}] {m['chunk_type']:5} | {m['section_path']}")
            print(f"      내용: {m['raw_content'][:50]}...")

        return len(materials) == 3


def test_sequential_extraction():
    """순차적 블록 추출 테스트 (실제 DART 보고서)"""
    print("\n" + "=" * 50)
    print("🧪 테스트 3: 순차적 블록 추출 (삼성전자)")
    print("=" * 50)

    agent = DartReportAgent()

    # 삼성전자 사업보고서 조회
    corp = agent.get_corp_by_stock_code("005930")
    if not corp:
        print("❌ 삼성전자 정보 조회 실패")
        return False

    print(f"✅ 기업: {corp.corp_name} ({corp.stock_code})")

    report = agent.get_annual_report(corp.corp_code)
    if not report:
        print("❌ 사업보고서 조회 실패")
        return False

    print(f"✅ 보고서: {report.report_nm}")

    # "회사의 개요" 섹션만 테스트
    section_data = agent.extract_section_sequential(report, "회사의 개요")

    if not section_data:
        print("❌ 섹션 추출 실패")
        return False

    blocks = section_data.get('blocks', [])
    text_count = sum(1 for b in blocks if b['chunk_type'] == 'text')
    table_count = sum(1 for b in blocks if b['chunk_type'] == 'table')

    print(f"\n📊 추출 결과:")
    print(f"   - 총 블록: {len(blocks)}개")
    print(f"   - 텍스트 블록: {text_count}개")
    print(f"   - 테이블 블록: {table_count}개")

    # 처음 5개 블록 미리보기
    print(f"\n📋 처음 5개 블록:")
    for block in blocks[:5]:
        content_preview = block['content'][:80].replace('\n', ' ')
        print(f"  [{block['sequence_order']:2}] {block['chunk_type']:5} | {content_preview}...")

    return len(blocks) > 0


def test_full_pipeline():
    """전체 파이프라인 테스트"""
    print("\n" + "=" * 50)
    print("🧪 테스트 4: 전체 파이프라인 (삼성전자)")
    print("=" * 50)

    pipeline = DataPipeline()

    # 삼성전자만 테스트 (DB 초기화)
    stats = pipeline.run(stock_codes=["005930"], reset_db=True)

    print(f"\n📊 파이프라인 결과:")
    print(f"   - 성공: {stats['success']}")
    print(f"   - 스킵: {stats['skipped']}")
    print(f"   - 실패: {stats['failed']}")

    # DB 확인
    with DBManager() as db:
        db_stats = db.get_stats()
        print(f"\n📦 DB 현황:")
        print(f"   - 기업: {db_stats['companies']}")
        print(f"   - 리포트: {db_stats['reports']}")
        print(f"   - 원천 데이터: {db_stats['materials']}")

        # 몇 개의 블록 샘플 확인
        if db_stats['materials'] > 0:
            # 첫 번째 리포트의 블록 조회
            db.cursor.execute('SELECT id FROM "Analysis_Reports" LIMIT 1')
            result = db.cursor.fetchone()
            if result:
                report_id = result[0]
                materials = db.get_materials_by_report(report_id)

                print(f"\n📋 블록 샘플 (처음 10개):")
                for m in materials[:10]:
                    content = m['raw_content'][:50].replace('\n', ' ')
                    print(f"  [{m['sequence_order']:3}] {m['chunk_type']:5} | {m['section_path'][:40]}")

    return stats['success'] > 0


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 순차적 블록 처리 방식 테스트")
    print("=" * 60)

    results = {}

    # 테스트 1: Markdown 변환
    results['markdown'] = test_table_to_markdown()

    # 테스트 2: DB 스키마
    results['db_schema'] = test_db_schema()

    # 테스트 3: 순차적 추출
    results['extraction'] = test_sequential_extraction()

    # 테스트 4: 전체 파이프라인
    results['pipeline'] = test_full_pipeline()

    # 결과 요약
    print("\n" + "=" * 60)
    print("📊 테스트 결과 요약")
    print("=" * 60)
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {name}: {status}")

    all_passed = all(results.values())
    print(f"\n{'🎉 모든 테스트 통과!' if all_passed else '⚠️ 일부 테스트 실패'}")

