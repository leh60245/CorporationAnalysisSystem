"""마커와 테이블 동기화 확인"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.db_manager import DBManager

with DBManager() as db:
    print("=" * 80)
    print("테이블 마커와 tables_json 동기화 확인")
    print("=" * 80)

    # 1. 전체 통계
    db.cursor.execute('SELECT COUNT(*) FROM "Source_Materials"')
    total = db.cursor.fetchone()[0]

    db.cursor.execute('SELECT COUNT(*) FROM "Source_Materials" WHERE tables_json IS NOT NULL')
    with_table = db.cursor.fetchone()[0]

    print(f"전체 청크: {total}개")
    print(f"테이블 있는 청크: {with_table}개 ({with_table/total*100:.1f}%)")
    print(f"테이블 없는 청크: {total - with_table}개")

    # 2. [테이블 참조] 마커 있지만 tables_json 없는 케이스
    print("\n" + "=" * 80)
    print("불일치 케이스")
    print("=" * 80)

    db.cursor.execute('''
        SELECT COUNT(*) 
        FROM "Source_Materials"
        WHERE raw_content LIKE '%[테이블 참조]%' AND tables_json IS NULL
    ''')
    mismatch1 = db.cursor.fetchone()[0]
    print(f"[테이블 참조] 마커 있지만 tables_json 없음: {mismatch1}개")

    # 상세 출력
    if mismatch1 > 0:
        db.cursor.execute('''
            SELECT id, chapter, section_name
            FROM "Source_Materials"
            WHERE raw_content LIKE '%[테이블 참조]%' AND tables_json IS NULL
            LIMIT 5
        ''')
        rows = db.cursor.fetchall()
        for row in rows:
            print(f"  - ID {row[0]}: {row[1]} / {row[2]}")

    # 3. tables_json 있지만 마커 없는 케이스
    db.cursor.execute('''
        SELECT COUNT(*) 
        FROM "Source_Materials"
        WHERE raw_content NOT LIKE '%[테이블 참조]%' AND tables_json IS NOT NULL
    ''')
    mismatch2 = db.cursor.fetchone()[0]
    print(f"tables_json 있지만 [테이블 참조] 마커 없음: {mismatch2}개")

    # 4. 정상 케이스
    db.cursor.execute('''
        SELECT COUNT(*) 
        FROM "Source_Materials"
        WHERE (raw_content LIKE '%[테이블 참조]%' AND tables_json IS NOT NULL)
           OR (raw_content NOT LIKE '%[테이블 참조]%' AND tables_json IS NULL)
    ''')
    matched = db.cursor.fetchone()[0]
    print(f"\n정상 동기화: {matched}개 ({matched/total*100:.1f}%)")

    # 5. 샘플 데이터 확인
    print("\n" + "=" * 80)
    print("샘플: 테이블 있는 청크의 raw_content")
    print("=" * 80)
    db.cursor.execute('''
        SELECT id, section_name, raw_content
        FROM "Source_Materials"
        WHERE tables_json IS NOT NULL
        LIMIT 2
    ''')
    rows = db.cursor.fetchall()
    for row in rows:
        print(f"\nID: {row[0]}, Section: {row[1]}")
        content = row[2][:300] if row[2] else ''
        print(f"Content: {content}...")
        print("-" * 40)

