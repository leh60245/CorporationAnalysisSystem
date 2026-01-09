"""
효율 모드 테스트 스크립트
"""
import sys
from pathlib import Path

# src 폴더를 Python 경로에 추가
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.core.pipeline import DataPipeline

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 효율 모드 테스트 (최근 3개월, 최대 5개 기업)")
    print("=" * 60)

    pipeline = DataPipeline()

    # 효율 모드로 실행 (최근 3개월, 최대 5개 기업만)
    pipeline.run_efficient(
        bgn_de="20250101",
        end_de="20260109",
        reset_db=True,
        limit=5
    )

    print("\n✅ 테스트 완료!")

