"""
파이프라인 테스트 스크립트
DART 데이터 수집 파이프라인 통합 테스트

사용법:
    python tests/test_pipeline.py                    # 삼성전자 1개 테스트
    python tests/test_pipeline.py --top3             # 삼성/SK하이닉스/NAVER
    python tests/test_pipeline.py --stock 005930     # 특정 종목코드
    python tests/test_pipeline.py --quick            # 빠른 테스트 (DB 초기화 없이)
"""
import sys
import argparse
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from src.core.pipeline import DataPipeline
from src.core.db_manager import DBManager


def test_pipeline_initialization():
    """파이프라인 초기화 테스트"""
    print("=" * 80)
    print("🧪 파이프라인 초기화 테스트")
    print("=" * 80)

    try:
        pipeline = DataPipeline()
        print(f"✅ 파이프라인 초기화 성공")
        print(f"   - DART Agent: {'OK' if pipeline.agent else 'FAIL'}")
        return pipeline
    except Exception as e:
        print(f"❌ 초기화 실패: {e}")
        return None


def test_single_company(stock_code="005930", reset_db=True):
    """단일 기업 테스트"""
    print("\n" + "=" * 80)
    print(f"🧪 단일 기업 테스트 (종목코드: {stock_code})")
    print("=" * 80)

    try:
        pipeline = DataPipeline()
        result = pipeline.run(stock_codes=[stock_code], reset_db=reset_db)

        # 결과 분석
        success_rate = (result['success'] / result['total']) * 100 if result['total'] > 0 else 0

        print(f"\n{'='*80}")
        print(f"테스트 결과:")
        print(f"  - 전체: {result['total']}개")
        print(f"  - 성공: {result['success']}개")
        print(f"  - 스킵: {result['skipped']}개")
        print(f"  - 실패: {result['failed']}개")
        print(f"  - 성공률: {success_rate:.1f}%")

        # DB 확인
        with DBManager() as db:
            stats = db.get_stats()
            print(f"\nDB 상태:")
            print(f"  - 기업: {stats['companies']}개")
            print(f"  - 리포트: {stats['reports']}개")
            print(f"  - 원천 데이터: {stats['materials']}개")

        print(f"{'='*80}")

        if result['success'] > 0:
            print(f"\n✅ 테스트 성공")
            return True
        else:
            print(f"\n❌ 테스트 실패")
            return False

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_top3_companies(reset_db=True):
    """상위 3개 기업 테스트"""
    print("\n" + "=" * 80)
    print("🧪 상위 3개 기업 테스트 (삼성전자, SK하이닉스, NAVER)")
    print("=" * 80)

    stock_codes = ["005930", "000660", "035420"]

    try:
        pipeline = DataPipeline()
        result = pipeline.run(stock_codes=stock_codes, reset_db=reset_db)

        success_rate = (result['success'] / result['total']) * 100 if result['total'] > 0 else 0

        print(f"\n{'='*80}")
        print(f"테스트 결과:")
        print(f"  - 전체: {result['total']}개")
        print(f"  - 성공: {result['success']}개")
        print(f"  - 스킵: {result['skipped']}개")
        print(f"  - 실패: {result['failed']}개")
        print(f"  - 성공률: {success_rate:.1f}%")

        # DB 확인
        with DBManager() as db:
            stats = db.get_stats()
            print(f"\nDB 상태:")
            print(f"  - 기업: {stats['companies']}개")
            print(f"  - 리포트: {stats['reports']}개")
            print(f"  - 원천 데이터: {stats['materials']}개")

        # 실패한 기업 출력
        if result['failed'] > 0 and pipeline.failed_corps:
            print(f"\n⚠️ 실패한 기업:")
            for corp in pipeline.failed_corps:
                print(f"  - {corp['corp_name']} ({corp['stock_code']})")

        print(f"{'='*80}")

        # 적어도 1개 이상 성공하면 통과
        if result['success'] > 0:
            print(f"\n✅ 테스트 성공 ({result['success']}/{result['total']} 성공)")
            return True
        else:
            print(f"\n❌ 테스트 실패 (모든 기업 실패)")
            return False

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_data_quality():
    """저장된 데이터 품질 검증"""
    print("\n" + "=" * 80)
    print("🧪 데이터 품질 검증")
    print("=" * 80)

    try:
        with DBManager() as db:
            # 1. 계층 구조 확인
            print("\n1. 계층 구조 검증...")
            db.cursor.execute('''
                SELECT COUNT(*) as cnt
                FROM "Source_Materials"
                WHERE chapter IS NOT NULL 
                AND section_name IS NOT NULL
            ''')
            hierarchical_count = db.cursor.fetchone()[0]
            print(f"   ✅ 계층 구조 데이터: {hierarchical_count:,}개")

            # 2. 테이블 분리 확인
            print("\n2. 테이블 분리 저장 검증...")
            db.cursor.execute('''
                SELECT COUNT(*) as cnt
                FROM "Source_Materials"
                WHERE tables_json IS NOT NULL
            ''')
            table_count = db.cursor.fetchone()[0]
            print(f"   ✅ 테이블 포함 청크: {table_count:,}개")

            # 3. 내용 길이 확인
            print("\n3. 청크 내용 길이 검증...")
            db.cursor.execute('''
                SELECT AVG(LENGTH(raw_content)) as avg_len,
                       MIN(LENGTH(raw_content)) as min_len,
                       MAX(LENGTH(raw_content)) as max_len
                FROM "Source_Materials"
            ''')
            row = db.cursor.fetchone()
            print(f"   ✅ 평균 길이: {row[0]:.0f} 자")
            print(f"   ✅ 최소 길이: {row[1]} 자")
            print(f"   ✅ 최대 길이: {row[2]:,} 자")

            # 4. 섹션별 분포
            print("\n4. 섹션별 데이터 분포...")
            db.cursor.execute('''
                SELECT chapter, COUNT(*) as cnt
                FROM "Source_Materials"
                GROUP BY chapter
                ORDER BY cnt DESC
                LIMIT 5
            ''')
            rows = db.cursor.fetchall()
            for chapter, cnt in rows:
                print(f"   - {chapter[:40]}: {cnt:,}개")

            print("\n✅ 데이터 품질 검증 완료")
            return True

    except Exception as e:
        print(f"❌ 데이터 품질 검증 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests(reset_db=True):
    """모든 테스트 실행"""
    print("\n" + "=" * 80)
    print("🧪 파이프라인 전체 테스트 시작")
    print("=" * 80 + "\n")

    results = []

    # 1. 초기화 테스트
    print("\n[1/3] 초기화 테스트")
    pipeline = test_pipeline_initialization()
    results.append(("초기화", pipeline is not None))

    if not pipeline:
        print("\n❌ 초기화 실패로 테스트 중단")
        return False

    # 2. 단일 기업 테스트
    print("\n[2/3] 단일 기업 테스트")
    single_success = test_single_company("005930", reset_db=reset_db)
    results.append(("삼성전자 처리", single_success))

    # 3. 데이터 품질 검증
    if single_success:
        print("\n[3/3] 데이터 품질 검증")
        quality_success = test_data_quality()
        results.append(("데이터 품질", quality_success))

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
    parser = argparse.ArgumentParser(description="파이프라인 통합 테스트")
    parser.add_argument("--top3", action="store_true", help="상위 3개 기업 테스트")
    parser.add_argument("--stock", type=str, help="특정 종목코드 테스트")
    parser.add_argument("--quick", action="store_true", help="빠른 테스트 (DB 초기화 없이)")
    parser.add_argument("--quality", action="store_true", help="데이터 품질 검증만")

    args = parser.parse_args()

    reset_db = not args.quick

    if args.quality:
        success = test_data_quality()
    elif args.top3:
        success = test_top3_companies(reset_db=reset_db)
    elif args.stock:
        success = test_single_company(args.stock, reset_db=reset_db)
    else:
        # 기본: 전체 테스트
        success = run_all_tests(reset_db=reset_db)

    sys.exit(0 if success else 1)
