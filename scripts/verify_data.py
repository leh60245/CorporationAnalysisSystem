"""DB에 저장된 데이터 확인 - 파일로 출력"""
import sys
sys.path.insert(0, 'C:/Users/kkh60/PycharmProjects/CorporationAnalysis')

from src.core.db_manager import DBManager

with DBManager() as db:
    # 통계
    stats = db.get_stats()
    print("=== DB 통계 ===")
    print(f"기업: {stats['companies']}")
    print(f"리포트: {stats['reports']}")
    print(f"원천 데이터: {stats['materials']}")
    
    # 텍스트/테이블 블록 수
    db.cursor.execute("""
        SELECT chunk_type, COUNT(*) 
        FROM "Source_Materials" 
        GROUP BY chunk_type
    """)
    print("\n=== 블록 타입별 수 ===")
    for row in db.cursor.fetchall():
        print(f"  {row[0]}: {row[1]}개")
    
    # 섹션 경로 분포
    db.cursor.execute("""
        SELECT section_path, COUNT(*) 
        FROM "Source_Materials" 
        GROUP BY section_path 
        ORDER BY COUNT(*) DESC 
        LIMIT 10
    """)
    print("\n=== 상위 10개 섹션 경로 ===")
    for row in db.cursor.fetchall():
        path = row[0][:50] if row[0] else 'None'
        print(f"  {path}: {row[1]}개")
    
    # 샘플 데이터 파일로 저장
    db.cursor.execute("""
        SELECT chunk_type, section_path, raw_content, sequence_order
        FROM "Source_Materials" 
        ORDER BY sequence_order 
        LIMIT 20
    """)
    
    with open('scripts/sample_data.txt', 'w', encoding='utf-8') as f:
        f.write("=== 샘플 데이터 (처음 20개 블록) ===\n\n")
        for row in db.cursor.fetchall():
            f.write(f"[{row[3]}] {row[0].upper()} | {row[1]}\n")
            f.write("-" * 60 + "\n")
            content = row[2][:500] if row[2] else 'None'
            f.write(content + "\n\n")
    
    print("\n샘플 데이터 저장됨: scripts/sample_data.txt")

