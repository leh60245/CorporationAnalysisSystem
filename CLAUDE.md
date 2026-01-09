
### 📂 2. CLAUDE.md
**목적:** AI 협업 히스토리 관리, 오류 추적, 해결 방안 아카이빙 (개발자 및 AI의 "기억 저장소")

# 🤖 CLAUDE.md (Developer Journal & Error Log)

이 파일은 프로젝트 진행 중 발생하는 이슈, 해결책, 주요 의사결정 사항을 기록하여 컨텍스트를 유지하는 데 사용됩니다.

## 📌 현재 진행 상황 (Current Context)
* **단계:** 시스템 고도화 및 소스 확장 (Phase 2)
* **현재 작업:** `NewsAgent` 구현 및 DB 스키마 일반화
* **최근 이슈:** DART 중심의 DB 구조를 뉴스/웹 수집 구조로 변경 필요

---

## 🛠️ 주요 명령어 (Commands)
```bash
# 가상환경 활성화
conda activate CorporationAnalysis

# 테스트 실행
pytest tests/

# 특정 테스트 파일 실행
pytest tests/test_news_agent.py

# 메인 파이프라인 실행
python main.py

```

---

## 🐛 오류 및 해결 로그 (Issue & Solution Log)

### [Template]

* **날짜:** YYYY-MM-DD
* **이슈:** (발생한 에러 메시지 또는 버그 현상 요약)
* **원인:** (분석된 원인)
* **해결:** (적용한 코드 수정 또는 해결 방법)
* **관련 파일:** `src/core/xxx.py`

### 202X-XX-XX (예시)

* **이슈:** `psycopg2.errors.UndefinedTable: relation "analysis_reports" does not exist`
* **원인:** DB 초기화 스크립트가 실행되지 않아 테이블이 생성되지 않음.
* **해결:** `db_manager.py`의 `create_tables()` 메서드를 `main.py` 시작 시 호출하도록 수정함.
* **관련 파일:** `src/core/db_manager.py`

---

## 💡 아키텍처 결정 사항 (ADR Summary)

* **[ADR-001] 데이터 소스 확장 전략:** `rcept_no`에 의존하던 PK 전략을 수정하여, 뉴스 및 웹 데이터는 URL 해시 등을 ID로 사용하고 `source_type` 컬럼으로 구분하기로 결정함.
* **[ADR-002] 임베딩 전략:** 테이블 데이터의 문맥 손실을 막기 위해 테이블 바로 앞의 텍스트 블록을 합쳐서 임베딩하는 'Context Look-back' 방식 유지.
