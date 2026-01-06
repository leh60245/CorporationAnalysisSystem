"""
파이프라인 모듈 - DART 데이터 수집 및 DB 적재 오케스트레이션
배치 처리, Rate Limiting, 에러 핸들링 담당
"""
import time
from typing import List, Optional, Dict
from datetime import datetime
from config import BATCH_CONFIG
from .db_manager import DBManager
from .dart_agent import DartReportAgent


class DataPipeline:
    """
    DART 사업보고서 데이터 수집 및 DB 적재 파이프라인
    """

    def __init__(self):
        self.agent = DartReportAgent()
        self.stats = {
            "total": 0,
            "success": 0,
            "skipped": 0,
            "failed": 0,
            "start_time": None,
            "end_time": None
        }
        self.failed_corps = []

    # ==================== 메인 파이프라인 ====================

    def run(
        self,
        stock_codes: Optional[List[str]] = None,
        limit: Optional[int] = None,
        reset_db: bool = False
    ):
        """
        파이프라인 실행

        Args:
            stock_codes: 처리할 종목코드 리스트 (None이면 전체 상장사)
            limit: 최대 처리 기업 수 (테스트용)
            reset_db: DB 초기화 여부
        """
        self.stats["start_time"] = datetime.now()

        print("\n" + "=" * 60)
        print("🚀 DART 데이터 파이프라인 시작")
        print("=" * 60)
        print(f"   시작 시간: {self.stats['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")

        # 1. DB 초기화
        with DBManager() as db:
            if reset_db:
                print("\n⚠️ DB 초기화 중...")
                db.reset_db()
            else:
                db.init_db()

        # 2. 대상 기업 선정
        if stock_codes:
            target_corps = []
            for code in stock_codes:
                corp = self.agent.get_corp_by_stock_code(code)
                if corp:
                    target_corps.append(corp)
                else:
                    print(f"⚠️ 종목코드 {code} 기업 없음")
        else:
            target_corps = self.agent.get_listed_corps()

        if limit:
            target_corps = target_corps[:limit]

        self.stats["total"] = len(target_corps)
        print(f"\n📋 대상 기업 수: {self.stats['total']}")

        # 3. 배치 처리
        batches = self._create_batches(target_corps)
        print(f"📦 배치 수: {len(batches)} (배치당 {BATCH_CONFIG['batch_size']}개)")

        for batch_idx, batch in enumerate(batches):
            print(f"\n{'─' * 50}")
            print(f"📦 배치 {batch_idx + 1}/{len(batches)} 처리 중...")

            self._process_batch(batch, batch_idx, len(batches))

            # 배치 간 딜레이 (마지막 배치 제외)
            if batch_idx < len(batches) - 1:
                delay = BATCH_CONFIG['batch_delay_sec']
                print(f"   ⏳ 다음 배치까지 {delay}초 대기...")
                time.sleep(delay)

        # 4. 결과 요약
        self.stats["end_time"] = datetime.now()
        self._print_summary()

        return self.stats

    def run_test(self, stock_codes: List[str] = None):
        """
        테스트 모드 실행 (기본: 삼성전자, SK하이닉스, NAVER)
        """
        if stock_codes is None:
            stock_codes = ["005930", "000660", "035420"]

        print("\n🧪 테스트 모드로 실행")
        return self.run(stock_codes=stock_codes, reset_db=True)

    def run_all(self, reset_db: bool = False):
        """
        전체 상장 기업 처리
        """
        print("\n🌐 전체 기업 처리 모드")
        return self.run(stock_codes=None, reset_db=reset_db)

    # ==================== 배치 처리 ====================

    def _create_batches(self, items: List) -> List[List]:
        """리스트를 배치 단위로 분할"""
        batch_size = BATCH_CONFIG['batch_size']
        return [items[i:i + batch_size] for i in range(0, len(items), batch_size)]

    def _process_batch(self, batch: List, batch_idx: int, total_batches: int):
        """단일 배치 처리"""
        for idx, corp in enumerate(batch):
            global_idx = batch_idx * BATCH_CONFIG['batch_size'] + idx + 1

            print(f"\n[{global_idx}/{self.stats['total']}] {corp.corp_name} ({corp.stock_code})")

            success = self._process_single_corp(corp)

            if success:
                self.stats["success"] += 1
            elif success is None:
                self.stats["skipped"] += 1
            else:
                self.stats["failed"] += 1
                self.failed_corps.append({
                    "corp_name": corp.corp_name,
                    "stock_code": corp.stock_code,
                    "corp_code": corp.corp_code
                })

            # 요청 간 딜레이
            time.sleep(BATCH_CONFIG['request_delay_sec'])

    def _process_single_corp(self, corp) -> Optional[bool]:
        """
        단일 기업 처리 (순차적 블록 처리 방식)

        Returns:
            True: 성공
            False: 실패
            None: 스킵 (보고서 없음 등)
        """
        corp_name = corp.corp_name
        corp_code = corp.corp_code
        stock_code = corp.stock_code

        try:
            # 1. 사업보고서 검색
            report = self.agent.get_annual_report(corp_code)

            if not report:
                print(f"   ⚠️ 사업보고서 없음 - 스킵")
                return None

            print(f"   📄 보고서: {report.report_nm}")

            # 2. 핵심 섹션 순차적 블록 추출
            sections = self.agent.extract_target_sections_sequential(report)

            if not sections:
                print(f"   ⚠️ 추출 가능한 섹션 없음 - 스킵")
                return None

            # 3. DB 저장
            with DBManager() as db:
                # 기업 등록
                company_id = db.insert_company(corp_name, corp_code, stock_code)
                print(f"   🏢 기업 등록 완료 (ID: {company_id})")

                # 리포트 등록
                report_info = self.agent.get_report_info(report)
                report_id = db.insert_report(company_id, report_info)
                print(f"   📋 리포트 등록 완료 (ID: {report_id})")

                # 섹션별 블록 저장 (순차적 블록 처리)
                total_blocks = 0
                text_count = 0
                table_count = 0

                for section in sections:
                    blocks = section.get('blocks', [])
                    saved = db.insert_materials_batch(report_id, blocks)
                    total_blocks += saved
                    text_count += sum(1 for b in blocks if b['chunk_type'] == 'text')
                    table_count += sum(1 for b in blocks if b['chunk_type'] == 'table')

                print(f"   📥 {total_blocks}개 블록 저장 완료 (텍스트: {text_count}, 테이블: {table_count})")

            return True

        except Exception as e:
            print(f"   ❌ 처리 실패: {e}")
            import traceback
            traceback.print_exc()
            return False

    # ==================== 재시도 로직 ====================

    def retry_failed(self):
        """실패한 기업들 재처리"""
        if not self.failed_corps:
            print("✅ 재처리할 실패 기업이 없습니다.")
            return

        print(f"\n🔄 {len(self.failed_corps)}개 실패 기업 재처리")

        retry_corps = []
        for failed in self.failed_corps:
            corp = self.agent.get_corp_by_stock_code(failed['stock_code'])
            if corp:
                retry_corps.append(corp)

        # 실패 목록 초기화
        self.failed_corps = []

        # 재시도 딜레이 후 처리
        time.sleep(BATCH_CONFIG['retry_delay_sec'])

        for corp in retry_corps:
            print(f"\n🔄 재시도: {corp.corp_name}")
            success = self._process_single_corp(corp)

            if not success and success is not None:
                self.failed_corps.append({
                    "corp_name": corp.corp_name,
                    "stock_code": corp.stock_code,
                    "corp_code": corp.corp_code
                })

            time.sleep(BATCH_CONFIG['request_delay_sec'])

    # ==================== 결과 출력 ====================

    def _print_summary(self):
        """실행 결과 요약 출력"""
        duration = self.stats["end_time"] - self.stats["start_time"]

        print("\n" + "=" * 60)
        print("📊 파이프라인 실행 결과")
        print("=" * 60)
        print(f"   시작 시간: {self.stats['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   종료 시간: {self.stats['end_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   소요 시간: {duration}")
        print(f"\n   📈 처리 통계:")
        print(f"      - 전체: {self.stats['total']}")
        print(f"      - 성공: {self.stats['success']}")
        print(f"      - 스킵: {self.stats['skipped']} (보고서 없음)")
        print(f"      - 실패: {self.stats['failed']}")

        if self.stats['total'] > 0:
            success_rate = (self.stats['success'] / self.stats['total']) * 100
            print(f"      - 성공률: {success_rate:.1f}%")

        if self.failed_corps:
            print(f"\n   ⚠️ 실패 기업 목록:")
            for fc in self.failed_corps[:10]:  # 최대 10개만 출력
                print(f"      - {fc['corp_name']} ({fc['stock_code']})")
            if len(self.failed_corps) > 10:
                print(f"      ... 외 {len(self.failed_corps) - 10}개")

        # DB 현황
        with DBManager() as db:
            stats = db.get_stats()
            print(f"\n   📦 DB 현황:")
            print(f"      - 기업: {stats['companies']}")
            print(f"      - 리포트: {stats['reports']}")
            print(f"      - 원천 데이터: {stats['materials']}")

        print("=" * 60)

