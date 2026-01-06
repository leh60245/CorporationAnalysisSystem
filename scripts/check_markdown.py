"""DB에 저장된 테이블 블록의 Markdown 형식 확인"""
import sys
sys.path.insert(0, 'C:/Users/kkh60/PycharmProjects/CorporationAnalysis')

from src.core.db_manager import DBManager

with DBManager() as db:
    # 테이블 블록 조회
    db.cursor.execute("""
        SELECT id, chunk_type, section_path, raw_content 
        FROM "Source_Materials" 
        WHERE chunk_type = 'table' 
        LIMIT 3
    """)
    rows = db.cursor.fetchall()

    for row in rows:
        print('='*60)
        print(f'ID: {row[0]}')
        print(f'Type: {row[1]}')
        print(f'Path: {row[2]}')
        print('Content (repr):')
        content = row[3][:300] if row[3] else 'None'
        print(repr(content))
        print()

