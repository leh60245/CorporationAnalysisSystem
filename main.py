"""
기업 분석 보고서 시스템 - 메인 진입점
DART 사업보고서 데이터 수집 및 DB 적재 파이프라인 실행

사용법:
    python main.py --test          # 테스트 모드 (3개 기업)
    python main.py --all           # 전체 상장 기업
    python main.py --explore       # 보고서 구조 탐색
    python main.py --stats         # DB 통계 조회
"""
import argparse
import sys

# src 폴더를 Python 경로에 추가
from pathlib import Path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))


def run_test_mode():
    """테스트 모드: 삼성전자, SK하이닉스, NAVER 3개 기업"""
    from src.core.pipeline import DataPipeline

    pipeline = DataPipeline()
    pipeline.run_test()


def run_all_mode(reset_db: bool = False):
    """전체 모드: 모든 상장 기업 처리"""
    from src.core.pipeline import DataPipeline

    if not reset_db:
        confirm = input("⚠️ 전체 상장 기업을 처리합니다. 계속하시겠습니까? (y/N): ")
        if confirm.lower() != 'y':
            print("취소되었습니다.")
            return

    pipeline = DataPipeline()
    pipeline.run_all(reset_db=reset_db)


def run_efficient_mode(reset_db: bool = False, limit: int = None, bgn_de: str = None, end_de: str = None):
    """
    효율 모드: 사업보고서가 있는 기업만 처리 (dart.filings.search 사용)

    기존 방식보다 훨씬 빠름 - 전체 상장사 순회 대신 사업보고서 일괄 검색
    """
    from src.core.pipeline import DataPipeline

    pipeline = DataPipeline()
    pipeline.run_efficient(bgn_de=bgn_de, end_de=end_de, reset_db=reset_db, limit=limit)


def run_explore_mode():
    """보고서 구조 탐색 모드"""
    from scripts.explore_report_structure import explore_report_structure

    stock_code = input("종목코드 입력 (기본: 005930 삼성전자): ").strip()
    if not stock_code:
        stock_code = "005930"

    explore_report_structure(stock_code)


def run_stats_mode():
    """DB 통계 조회"""
    from src.core.db_manager import DBManager

    print("\n📊 DB 통계")
    print("=" * 40)

    with DBManager() as db:
        stats = db.get_stats()
        print(f"   기업 수: {stats['companies']}")
        print(f"   리포트 수: {stats['reports']}")
        print(f"   원천 데이터 수: {stats['materials']}")
        print(f"   임베딩 완료: {stats['embedded_materials']}")

        if stats['materials'] > 0:
            embed_rate = (stats['embedded_materials'] / stats['materials']) * 100
            print(f"   임베딩 비율: {embed_rate:.1f}%")

    print("=" * 40)


def run_embed_mode(report_id: int = None, batch_size: int = 32, limit: int = None):
    """임베딩 생성 모드"""
    from embedding_pipeline import EmbeddingPipeline

    pipeline = EmbeddingPipeline()

    if report_id:
        pipeline.run_for_report(report_id)
    else:
        pipeline.run(batch_size=batch_size, limit=limit)


def run_custom_mode(stock_codes: list, reset_db: bool = False):
    """커스텀 모드: 특정 종목코드 리스트 처리"""
    from src.core.pipeline import DataPipeline

    pipeline = DataPipeline()
    pipeline.run(stock_codes=stock_codes, reset_db=reset_db)


def main():
    parser = argparse.ArgumentParser(
        description="기업 분석 보고서 시스템 - DART 데이터 파이프라인",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
    python main.py --test                    # 테스트 모드 (3개 기업)
    python main.py --all                     # 전체 상장 기업
    python main.py --all --reset             # DB 초기화 후 전체 처리
    python main.py --efficient               # 효율 모드 (사업보고서 있는 기업만)
    python main.py --efficient --bgn 20250101 --end 20250331  # 기간 지정
    python main.py --codes 005930 000660     # 특정 종목코드만 처리
    python main.py --embed                   # 전체 임베딩 생성
    python main.py --embed --report-id 1     # 특정 리포트 임베딩
    python main.py --explore                 # 보고서 구조 탐색
    python main.py --stats                   # DB 통계 조회
        """
    )

    # 실행 모드
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument('--test', action='store_true',
                            help='테스트 모드 (삼성전자, SK하이닉스, NAVER)')
    mode_group.add_argument('--all', action='store_true',
                            help='전체 상장 기업 처리')
    mode_group.add_argument('--efficient', action='store_true',
                            help='효율 모드 (사업보고서가 있는 기업만 일괄 검색)')
    mode_group.add_argument('--codes', nargs='+', metavar='CODE',
                            help='특정 종목코드 처리 (공백으로 구분)')
    mode_group.add_argument('--embed', action='store_true',
                            help='임베딩 생성')
    mode_group.add_argument('--explore', action='store_true',
                            help='보고서 구조 탐색')
    mode_group.add_argument('--stats', action='store_true',
                            help='DB 통계 조회')

    # 옵션
    parser.add_argument('--reset', action='store_true',
                        help='DB 초기화 후 실행')
    parser.add_argument('--limit', type=int,
                        help='최대 처리 개수')
    parser.add_argument('--report-id', type=int,
                        help='특정 리포트 ID (--embed와 함께 사용)')
    parser.add_argument('--batch-size', type=int, default=32,
                        help='임베딩 배치 크기 (기본: 32)')
    parser.add_argument('--bgn', type=str, metavar='YYYYMMDD',
                        help='검색 시작일 (--efficient와 함께 사용)')
    parser.add_argument('--end', type=str, metavar='YYYYMMDD',
                        help='검색 종료일 (--efficient와 함께 사용)')

    args = parser.parse_args()

    try:
        if args.test:
            run_test_mode()
        elif args.all:
            if args.limit:
                from src.core.pipeline import DataPipeline
                pipeline = DataPipeline()
                pipeline.run(stock_codes=None, limit=args.limit, reset_db=args.reset)
            else:
                run_all_mode(reset_db=args.reset)
        elif args.efficient:
            run_efficient_mode(
                reset_db=args.reset,
                limit=args.limit,
                bgn_de=args.bgn,
                end_de=args.end
            )
        elif args.codes:
            run_custom_mode(args.codes, reset_db=args.reset)
        elif args.embed:
            run_embed_mode(
                report_id=args.report_id,
                batch_size=args.batch_size,
                limit=args.limit
            )
        elif args.explore:
            run_explore_mode()
        elif args.stats:
            run_stats_mode()

    except KeyboardInterrupt:
        print("\n\n⚠️ 사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

