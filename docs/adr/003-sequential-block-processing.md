# 순차적 블록 처리(Sequential Block Processing) 리팩토링 완료

## 📋 개요

전문가 조언에 따라 DART 데이터 저장 방식을 **"순차적 블록 처리(Sequential Block Processing)"** 방식으로 리팩토링했습니다.

### 기존 방식의 문제점
- 글/표를 따로 추출 후 `[테이블 참조]` 마커로 연결
- 인덱스 오류로 텍스트-테이블 싱크 불일치 발생
- 복잡한 계층 구조(chapter/section_name/sub_section) 관리 어려움

### 새로운 방식의 장점
- HTML을 위에서 아래로 읽으며 만나는 순서대로 저장
- **싱크 100% 일치**: 순서대로 저장하므로 어긋날 일 없음
- **마커 불필요**: 다음 행이 바로 해당 테이블
- **단순한 구조**: `section_path` 하나로 경로 관리

---

## 🔧 변경 사항

### 1. DB 스키마 (`db_manager.py`)

**Before:**
```sql
CREATE TABLE "Source_Materials" (
    chapter VARCHAR(200),
    section_name VARCHAR(200),
    sub_section VARCHAR(200),
    chunk_index INTEGER,
    raw_content TEXT,
    tables_json JSONB,
    ...
);
```

**After:**
```sql
CREATE TABLE "Source_Materials" (
    chunk_type VARCHAR(20) NOT NULL DEFAULT 'text',  -- 'text' | 'table'
    section_path TEXT,                                -- "II. 사업의 내용 > 1. 사업의 개요"
    sequence_order INTEGER,                           -- 문서 내 순서 (0부터)
    raw_content TEXT,                                 -- 텍스트 또는 Markdown 테이블
    table_metadata JSONB,                             -- 테이블 메타데이터
    ...
);
```

### 2. 테이블 → Markdown 변환 (`dart_agent.py`)

새로운 `convert_table_to_markdown()` 함수:
```python
def convert_table_to_markdown(self, table_element) -> Tuple[str, Dict]:
    # HTML 테이블을 Markdown 형식으로 변환
    # 예: | 구분 | 2024년 | 2023년 |
    #     |---|---|---|
    #     | 매출액 | 100억 | 80억 |
```

### 3. 순차적 블록 파싱 (`dart_agent.py`)

새로운 함수들:
- `extract_section_sequential()`: 섹션을 순차적으로 추출
- `_parse_sequential_blocks()`: HTML 요소를 순서대로 파싱
- `_update_section_path()`: 헤더 만날 때 경로 업데이트
- `extract_target_sections_sequential()`: 핵심 섹션들 추출

### 4. 파이프라인 연동 (`pipeline.py`)

`_process_single_corp()` 메서드가 새로운 순차적 블록 처리 방식 사용

---

## 📊 테스트 결과

### 삼성전자 사업보고서 테스트
```
✅ '회사의 개요' 추출 완료 (3페이지, 60블록: 텍스트 16, 테이블 44)
✅ '사업의 내용' 추출 완료 (3페이지, 136블록: 텍스트 37, 테이블 99)
✅ '재무에 관한 사항' 추출 완료 (25페이지, 1891블록: 텍스트 90, 테이블 1801)

📥 2087개 블록 저장 완료 (텍스트: 143, 테이블: 1944)
```

### DB 통계
```
기업: 1
리포트: 1
원천 데이터: 2087개

블록 타입:
  - text: 143개
  - table: 1944개
```

### 샘플 데이터
```
[0] TEXT | I. 회사의 개요
I. 회사의 개요
1. 회사의 개요
가. 회사의 법적ㆍ상업적 명칭...

[1] TABLE | I. 회사의 개요
| 부문 | 주 요 제 품 |
|---|---|
| DX 부문 | TV, 모니터, 냉장고... |
| DS 부문 | DRAM, NAND Flash... |
...
```

---

## 📁 변경된 파일

| 파일 | 변경 내용 |
|------|----------|
| `src/core/db_manager.py` | 스키마 변경, insert/get 함수 수정 |
| `src/core/dart_agent.py` | 순차적 블록 처리 함수 추가 |
| `src/core/pipeline.py` | 새 방식으로 파이프라인 수정 |

---

## 🚀 사용 방법

```python
from src.core.pipeline import DataPipeline

# 테스트 실행 (삼성전자)
pipeline = DataPipeline()
pipeline.run(stock_codes=["005930"], reset_db=True)

# 전체 기업 처리
pipeline.run_all(reset_db=True)
```

---

## ⚠️ 주의사항

1. **DB 초기화 필요**: 스키마가 변경되었으므로 `reset_db=True` 필요
2. **기존 데이터 마이그레이션**: 기존 데이터가 중요하다면 별도 마이그레이션 필요
3. **테이블 과다 추출**: 재무제표 섹션에서 테이블이 많이 추출됨 (1800+개)
   - 필요시 필터링 로직 추가 검토

---

## 📅 완료일

2026-01-06

