"""
DB Manager 테스트 스크립트
데이터베이스 연결, 스키마 생성, 통계 조회 테스트

사용법:
    python tests/test_db.py              # 전체 테스트
    python tests/test_db.py --connection # 연결 테스트만
    python tests/test_db.py --stats      # 통계만 조회
    python tests/test_db.py --reset      # DB 초기화 포함
"""
import sys
import argparse
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from src.core.db_manager import DBManager


def test_connection():
    """DB 연결 테스트"""
    print("=" * 80)
    print("🧪 DB 연결 테스트")
    print("=" * 80)

    try:
        with DBManager() as db:
            print("✅ DB 연결 성공")
            return True
    except Exception as e:
        print(f"❌ DB 연결 실패: {e}")
        return False


def test_schema():
    """DB 스키마 생성 테스트"""
    print("\n" + "=" * 80)
    print("🧪 DB 스키마 생성 테스트")
    print("=" * 80)

    try:
        with DBManager() as db:
            db.init_db()

            # 테이블 존재 확인
            db.cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('Companies', 'Analysis_Reports', 'Source_Materials')
            """)
            tables = [row[0] for row in db.cursor.fetchall()]

            print(f"✅ 발견된 테이블: {', '.join(tables)}")

            if len(tables) == 3:
                return True
            else:
                print(f"⚠️ 일부 테이블이 누락되었습니다")
                return False

    except Exception as e:
        print(f"❌ 스키마 생성 실패: {e}")
        return False


def test_stats():
    """DB 통계 조회 테스트"""
    print("\n" + "=" * 80)
    print("🧪 DB 통계 조회 테스트")
    print("=" * 80)

    try:
        with DBManager() as db:
            stats = db.get_stats()
            print(f"\n📊 현재 DB 상태:")
            print(f"   - 기업 수: {stats['companies']:,}개")
            print(f"   - 리포트 수: {stats['reports']:,}개")
            print(f"   - 원천 데이터 수: {stats['materials']:,}개")
            print(f"   - 임베딩 완료 수: {stats['embedded_materials']:,}개")
            return True
    except Exception as e:
        print(f"❌ 통계 조회 실패: {e}")
        return False


def test_crud():
    """기본 CRUD 테스트"""
    print("\n" + "=" * 80)
    print("🧪 CRUD 기능 테스트")
    print("=" * 80)

    try:
        with DBManager() as db:
            # 1. 기업 등록
            print("\n1. 기업 등록 테스트...")
            company_id = db.insert_company(
                name="테스트기업",
                corp_code="99999999",
                stock_code="999999",
                industry="테스트업종"
            )
            print(f"   ✅ 기업 등록 성공 (ID: {company_id})")

            # 2. 기업 조회
            print("\n2. 기업 조회 테스트...")
            company = db.get_company_by_corp_code("99999999")
            assert company is not None, "기업 조회 실패"
            print(f"   ✅ 기업 조회 성공: {company['company_name']}")

            # 3. 리포트 등록
            print("\n3. 리포트 등록 테스트...")
            report_id = db.insert_report(company_id, {
                "title": "테스트 보고서",
                "rcept_no": "999999999999",
                "rcept_dt": "20260106",
                "report_type": "annual"
            })
            print(f"   ✅ 리포트 등록 성공 (ID: {report_id})")

            # 4. 원천 데이터 등록
            print("\n4. 원천 데이터 등록 테스트...")
            success = db.insert_source_material(
                report_id=report_id,
                section_name="테스트 섹션",
                chunk_index=0,
                content="테스트 내용입니다.",
                chapter="테스트 챕터",
                sub_section="테스트 서브섹션",
                tables_json=[{"table_index": 0, "data": [{"col1": "val1"}]}]
            )
            assert success, "원천 데이터 등록 실패"
            print(f"   ✅ 원천 데이터 등록 성공")

            print("\n✅ 모든 CRUD 테스트 통과")
            return True

    except AssertionError as e:
        print(f"\n❌ CRUD 테스트 실패: {e}")
        return False
    except Exception as e:
        print(f"\n❌ CRUD 테스트 중 오류: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_reset():
    """DB 초기화 테스트 (주의: 모든 데이터 삭제)"""
    print("\n" + "=" * 80)
    print("🧪 DB 초기화 테스트")
    print("=" * 80)

    confirm = input("⚠️ 모든 데이터가 삭제됩니다. 계속하시겠습니까? (y/N): ")
    if confirm.lower() != 'y':
        print("❌ 테스트 취소됨")
        return False

    try:
        with DBManager() as db:
            db.reset_db()
            print("✅ DB 초기화 성공")
            return True
    except Exception as e:
        print(f"❌ DB 초기화 실패: {e}")
        return False


def run_all_tests(include_reset=False, include_crud=False):
    """모든 테스트 실행"""
    print("\n" + "=" * 80)
    print("🧪 DB Manager 전체 테스트 시작")
    print("=" * 80 + "\n")

    results = []

    # 1. 연결 테스트
    results.append(("DB 연결", test_connection()))

    # 2. 스키마 테스트
    results.append(("스키마 생성", test_schema()))

    # 3. 통계 테스트
    results.append(("통계 조회", test_stats()))

    # 4. CRUD 테스트 (옵션)
    if include_crud:
        results.append(("CRUD 기능", test_crud()))

    # 5. 초기화 테스트 (옵션)
    if include_reset:
        results.append(("DB 초기화", test_reset()))

    # 결과 요약
    print("\n" + "=" * 80)
    print("📊 테스트 결과 요약")
    print("=" * 80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    print(f"\n총 {passed}/{total} 테스트 통과")

    return passed == total


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DB Manager 테스트")
    parser.add_argument("--reset", action="store_true", help="DB 초기화 테스트 포함")
    parser.add_argument("--crud", action="store_true", help="CRUD 테스트 포함")
    parser.add_argument("--connection", action="store_true", help="연결 테스트만 실행")
    parser.add_argument("--stats", action="store_true", help="통계 조회만 실행")

    args = parser.parse_args()

    if args.connection:
        success = test_connection()
    elif args.stats:
        success = test_stats()
    else:
        success = run_all_tests(include_reset=args.reset, include_crud=args.crud)

    sys.exit(0 if success else 1)
