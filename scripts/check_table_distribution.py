"""tables_json 배분 상세 확인"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.db_manager import DBManager
import json

with DBManager() as db:
    # 1. 전체 통계
    db.cursor.execute('''
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN tables_json IS NOT NULL THEN 1 ELSE 0 END) as with_tables,
            SUM(CASE WHEN tables_json IS NULL THEN 1 ELSE 0 END) as without_tables
        FROM "Source_Materials"
    ''')
    row = db.cursor.fetchone()
    print("=" * 70)
    print("tables_json 배분 결과")
    print("=" * 70)
    print(f"전체 청크: {row[0]}개")
    print(f"테이블 포함: {row[1]}개 ({row[1]/row[0]*100:.1f}%)")
    print(f"테이블 없음: {row[2]}개 ({row[2]/row[0]*100:.1f}%)")
    
    # 2. chapter별 테이블 배분
    print("\n" + "=" * 70)
    print("chapter별 테이블 배분")
    print("=" * 70)
    db.cursor.execute('''
        SELECT chapter, 
               COUNT(*) as total_chunks,
               SUM(CASE WHEN tables_json IS NOT NULL THEN 1 ELSE 0 END) as with_tables
        FROM "Source_Materials"
        GROUP BY chapter
    ''')
    rows = db.cursor.fetchall()
    for row in rows:
        pct = row[2]/row[1]*100 if row[1] > 0 else 0
        print(f"{row[0]}: {row[1]}개 청크 중 {row[2]}개에 테이블 ({pct:.1f}%)")
    
    # 3. 테이블 개수별 분포
    print("\n" + "=" * 70)
    print("청크당 테이블 개수 분포")
    print("=" * 70)
    db.cursor.execute('''
        SELECT 
            CASE WHEN tables_json IS NULL THEN 0 
                 ELSE jsonb_array_length(tables_json) 
            END as table_count,
            COUNT(*) as chunk_count
        FROM "Source_Materials"
        GROUP BY 1
        ORDER BY 1
    ''')
    rows = db.cursor.fetchall()
    for row in rows:
        print(f"테이블 {row[0]}개: {row[1]}개 청크")
    
    # 4. 샘플: 테이블이 여러 개 있는 청크
    print("\n" + "=" * 70)
    print("테이블 많은 청크 샘플 (상위 5개)")
    print("=" * 70)
    db.cursor.execute('''
        SELECT id, section_name, jsonb_array_length(tables_json) as cnt
        FROM "Source_Materials"
        WHERE tables_json IS NOT NULL
        ORDER BY jsonb_array_length(tables_json) DESC
        LIMIT 5
    ''')
    rows = db.cursor.fetchall()
    for row in rows:
        print(f"ID {row[0]}: {row[1][:40]} - {row[2]}개 테이블")
    
    # 5. 특정 청크의 테이블 내용 샘플
    print("\n" + "=" * 70)
    print("테이블 내용 샘플 (ID=5)")
    print("=" * 70)
    db.cursor.execute('''
        SELECT tables_json
        FROM "Source_Materials"
        WHERE id = 5
    ''')
    row = db.cursor.fetchone()
    if row and row[0]:
        tables = row[0]
        print(f"테이블 수: {len(tables)}개")
        for i, t in enumerate(tables[:2]):  # 처음 2개만
            print(f"\n테이블 {i+1}:")
            print(json.dumps(t, ensure_ascii=False, indent=2)[:300])

