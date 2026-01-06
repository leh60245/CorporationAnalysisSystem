"""수정 결과 검증 스크립트"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.db_manager import DBManager

with DBManager() as db:
    # 1. 전체 통계
    db.cursor.execute('''
        SELECT COUNT(*) as total,
               SUM(CASE WHEN tables_json IS NOT NULL THEN 1 ELSE 0 END) as with_tables
        FROM "Source_Materials"
    ''')
    row = db.cursor.fetchone()
    print("=" * 60)
    print("전체 통계")
    print("=" * 60)
    print(f"전체 청크: {row[0]}개")
    print(f"테이블 포함: {row[1]}개")

    # 2. 테이블 참조 마커 확인
    db.cursor.execute('''
        SELECT COUNT(*) 
        FROM "Source_Materials"
        WHERE raw_content LIKE '%%테이블 참조%%'
    ''')
    marker_count = db.cursor.fetchone()[0]
    print(f"[테이블 참조] 마커 포함: {marker_count}개")

    # 3. 샘플 raw_content 확인 (테이블 형식 데이터가 있는지)
    print("\n" + "=" * 60)
    print("샘플 raw_content (처음 500자)")
    print("=" * 60)

    db.cursor.execute('''
        SELECT id, section_name, raw_content
        FROM "Source_Materials"
        WHERE section_name LIKE '%%사업의 개요%%'
        LIMIT 1
    ''')
    row = db.cursor.fetchone()
    if row:
        print(f"ID: {row[0]}, Section: {row[1]}")
        print("-" * 60)
        print(row[2][:500])
        print("...")

    # 4. tables_json 확인
    print("\n" + "=" * 60)
    print("테이블 JSON 샘플")
    print("=" * 60)

    db.cursor.execute('''
        SELECT id, section_name, tables_json
        FROM "Source_Materials"
        WHERE tables_json IS NOT NULL
        LIMIT 1
    ''')
    row = db.cursor.fetchone()
    if row:
        print(f"ID: {row[0]}, Section: {row[1]}")
        print("-" * 60)
        import json
        tables = row[2]
        if tables:
            print(f"테이블 수: {len(tables)}개")
            if len(tables) > 0:
                print(json.dumps(tables[0], ensure_ascii=False, indent=2)[:400])

