"""tables_json 상태 전체 확인"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.db_manager import DBManager

with DBManager() as db:
    # 1. tables_json NULL vs NOT NULL 통계
    db.cursor.execute('''
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN tables_json IS NOT NULL THEN 1 ELSE 0 END) as with_tables,
            SUM(CASE WHEN tables_json IS NULL THEN 1 ELSE 0 END) as without_tables
        FROM "Source_Materials"
    ''')
    row = db.cursor.fetchone()
    print("=" * 70)
    print("tables_json 통계")
    print("=" * 70)
    print(f"전체: {row[0]}개, 테이블 있음: {row[1]}개, 테이블 없음: {row[2]}개")

    # 2. chunk_index별 tables_json 유무
    print("\n" + "=" * 70)
    print("chunk_index별 tables_json 유무")
    print("=" * 70)
    db.cursor.execute('''
        SELECT chunk_index, 
               COUNT(*) as cnt,
               SUM(CASE WHEN tables_json IS NOT NULL THEN 1 ELSE 0 END) as with_table
        FROM "Source_Materials"
        GROUP BY chunk_index
        ORDER BY chunk_index
        LIMIT 15
    ''')
    rows = db.cursor.fetchall()
    print("Chunk_Index  Total  With_Tables")
    print("-" * 40)
    for row in rows:
        print(f"{row[0]:<12} {row[1]:<6} {row[2]}")

    # 3. chapter별 테이블 수
    print("\n" + "=" * 70)
    print("chapter별 전체 테이블 수 (처음 추출 시)")
    print("=" * 70)

    # 4. 각 청크별 상세 정보
    print("\n" + "=" * 70)
    print("상위 20개 청크 상세")
    print("=" * 70)
    db.cursor.execute('''
        SELECT id, chunk_index, chapter, section_name,
               tables_json IS NOT NULL as has_table
        FROM "Source_Materials"
        ORDER BY id
        LIMIT 20
    ''')
    rows = db.cursor.fetchall()
    print(f"{'ID':<5} {'Idx':<5} {'Chapter':<20} {'Section':<25} {'Table'}")
    print("-" * 80)
    for row in rows:
        chapter = (row[2] or '')[:18]
        section = (row[3] or '')[:23]
        print(f"{row[0]:<5} {row[1]:<5} {chapter:<20} {section:<25} {row[4]}")

