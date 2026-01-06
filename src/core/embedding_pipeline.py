"""
임베딩 파이프라인 모듈 - DB에 저장된 원천 데이터에 임베딩 생성 및 업데이트
"""
import time
from typing import List, Dict, Optional
from datetime import datetime
from tqdm import tqdm

from config import EMBEDDING_CONFIG, BATCH_CONFIG
from .db_manager import DBManager
from ..utils.embedding_generator import EmbeddingGenerator


class EmbeddingPipeline:
    """
    Source_Materials 테이블의 텍스트에 임베딩을 생성하고 업데이트하는 파이프라인
    """

    def __init__(self):
        self.generator = None  # Lazy loading
        self.stats = {
            "total": 0,
            "processed": 0,
            "failed": 0,
            "start_time": None,
            "end_time": None
        }

    def _init_generator(self):
        """임베딩 생성기 초기화 (lazy loading)"""
        if self.generator is None:
            self.generator = EmbeddingGenerator()

    # ==================== 메인 파이프라인 ====================

    def run(
        self,
        batch_size: int = None,
        limit: Optional[int] = None,
        report_id: Optional[int] = None
    ):
        """
        임베딩 파이프라인 실행

        Args:
            batch_size: 한 번에 처리할 청크 수
            limit: 최대 처리 개수 (테스트용)
            report_id: 특정 리포트만 처리 (None이면 전체)
        """
        self.stats["start_time"] = datetime.now()
        batch_size = batch_size or EMBEDDING_CONFIG.get('batch_size', 32)

        print("\n" + "=" * 60)
        print("🧠 임베딩 파이프라인 시작")
        print("=" * 60)
        print(f"   시작 시간: {self.stats['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   배치 크기: {batch_size}")

        # 1. 임베딩 생성기 초기화
        self._init_generator()

        # 2. 임베딩이 없는 데이터 조회
        with DBManager() as db:
            pending_materials = self._get_pending_materials(db, limit, report_id)

        self.stats["total"] = len(pending_materials)
        print(f"\n📋 처리 대상: {self.stats['total']}개 청크")

        if self.stats["total"] == 0:
            print("✅ 모든 데이터에 임베딩이 이미 존재합니다.")
            return self.stats

        # 3. 배치 처리
        batches = self._create_batches(pending_materials, batch_size)
        print(f"📦 배치 수: {len(batches)}")

        for batch_idx, batch in enumerate(tqdm(batches, desc="임베딩 생성")):
            self._process_batch(batch)

            # 메모리 관리를 위한 짧은 딜레이
            if batch_idx % 10 == 0 and batch_idx > 0:
                time.sleep(0.1)

        # 4. 결과 요약
        self.stats["end_time"] = datetime.now()
        self._print_summary()

        return self.stats

    def run_for_report(self, report_id: int):
        """특정 리포트의 임베딩만 생성"""
        print(f"\n🎯 리포트 ID {report_id}의 임베딩 생성")
        return self.run(report_id=report_id)

    def run_all(self, batch_size: int = None):
        """전체 미처리 데이터 임베딩 생성"""
        return self.run(batch_size=batch_size)

    # ==================== 데이터 조회 ====================

    def _get_pending_materials(
        self,
        db: DBManager,
        limit: Optional[int] = None,
        report_id: Optional[int] = None
    ) -> List[Dict]:
        """임베딩이 없는 Source_Materials 조회"""

        sql = """
            SELECT id, report_id, section_name, chunk_index, raw_content
            FROM "Source_Materials"
            WHERE embedding IS NULL
        """
        params = []

        if report_id is not None:
            sql += " AND report_id = %s"
            params.append(report_id)

        sql += " ORDER BY report_id, section_name, chunk_index"

        if limit is not None:
            sql += f" LIMIT {limit}"

        db.cursor.execute(sql, params)
        rows = db.cursor.fetchall()

        return [
            {
                "id": row[0],
                "report_id": row[1],
                "section_name": row[2],
                "chunk_index": row[3],
                "raw_content": row[4]
            }
            for row in rows
        ]

    # ==================== 배치 처리 ====================

    def _create_batches(self, items: List, batch_size: int) -> List[List]:
        """리스트를 배치 단위로 분할"""
        return [items[i:i + batch_size] for i in range(0, len(items), batch_size)]

    def _process_batch(self, batch: List[Dict]):
        """단일 배치 처리"""
        try:
            # 텍스트 추출
            texts = [item["raw_content"] for item in batch]
            ids = [item["id"] for item in batch]

            # 임베딩 생성
            embeddings = self.generator.embed_texts(texts)

            # DB 업데이트
            with DBManager() as db:
                for item_id, embedding in zip(ids, embeddings):
                    self._update_embedding(db, item_id, embedding)

            self.stats["processed"] += len(batch)

        except Exception as e:
            print(f"\n⚠️ 배치 처리 실패: {e}")
            self.stats["failed"] += len(batch)

    def _update_embedding(self, db: DBManager, material_id: int, embedding: List[float]):
        """Source_Materials 테이블에 임베딩 업데이트"""
        sql = """
            UPDATE "Source_Materials"
            SET embedding = %s,
                metadata = jsonb_set(
                    COALESCE(metadata, '{}'), 
                    '{has_embedding}', 
                    'true'
                )
            WHERE id = %s
        """
        db.cursor.execute(sql, (embedding, material_id))
        db.conn.commit()

    # ==================== 결과 출력 ====================

    def _print_summary(self):
        """실행 결과 요약 출력"""
        duration = self.stats["end_time"] - self.stats["start_time"]

        print("\n" + "=" * 60)
        print("📊 임베딩 파이프라인 결과")
        print("=" * 60)
        print(f"   시작 시간: {self.stats['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   종료 시간: {self.stats['end_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   소요 시간: {duration}")
        print(f"\n   📈 처리 통계:")
        print(f"      - 전체: {self.stats['total']}")
        print(f"      - 성공: {self.stats['processed']}")
        print(f"      - 실패: {self.stats['failed']}")

        if self.stats['total'] > 0:
            success_rate = (self.stats['processed'] / self.stats['total']) * 100
            print(f"      - 성공률: {success_rate:.1f}%")

            # 처리 속도
            seconds = duration.total_seconds()
            if seconds > 0:
                rate = self.stats['processed'] / seconds
                print(f"      - 처리 속도: {rate:.1f} 청크/초")

        # DB 현황
        with DBManager() as db:
            stats = db.get_stats()
            print(f"\n   📦 DB 현황:")
            print(f"      - 전체 원천 데이터: {stats['materials']}")
            print(f"      - 임베딩 완료: {stats['embedded_materials']}")

            if stats['materials'] > 0:
                embed_rate = (stats['embedded_materials'] / stats['materials']) * 100
                print(f"      - 임베딩 비율: {embed_rate:.1f}%")

        print("=" * 60)


# === CLI 지원 ===
def main():
    import argparse

    parser = argparse.ArgumentParser(description="임베딩 파이프라인")
    parser.add_argument('--all', action='store_true', help='전체 미처리 데이터 임베딩')
    parser.add_argument('--report', type=int, help='특정 리포트 ID만 처리')
    parser.add_argument('--batch-size', type=int, default=32, help='배치 크기')
    parser.add_argument('--limit', type=int, help='최대 처리 개수 (테스트용)')

    args = parser.parse_args()

    pipeline = EmbeddingPipeline()

    if args.report:
        pipeline.run_for_report(args.report)
    else:
        pipeline.run(batch_size=args.batch_size, limit=args.limit)


if __name__ == "__main__":
    main()

