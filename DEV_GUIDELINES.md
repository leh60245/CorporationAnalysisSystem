### 📂 1. DEV_GUIDELINES.md

**목적:** 코드 품질 유지, 일관된 스타일 적용, 아키텍처 원칙 준수


# 📘 개발 가이드라인 (DEV_GUIDELINES)

## 1. 프로젝트 개요 및 아키텍처 원칙
이 프로젝트는 기업 분석 정보를 수집, 가공하여 RAG(검색 증강 생성) 기반 시스템을 구축하는 것을 목표로 합니다.

### 핵심 아키텍처 원칙
1.  **모듈화 (Modularity):** 각 기능(수집, 가공, 저장, 임베딩)은 독립적인 모듈로 분리하며, 낮은 결합도(Low Coupling)를 유지합니다.
2.  **순차적 처리 (Sequential Processing):** 문서의 문맥 유지를 위해 `Sequential Block Processing` (텍스트 → 테이블 → 텍스트 흐름)을 준수합니다.
3.  **확장성 (Extensibility):** DART 외에 뉴스, 웹 등 다양한 소스를 수용할 수 있도록 인터페이스를 일반화합니다.
4.  **타입 안정성 (Type Safety):** Python 3.10+ 기반의 Type Hinting을 적극 사용하여 데이터 파이프라인의 오류를 방지합니다.

---

## 2. 코딩 컨벤션 (Coding Standards)

### 스타일 가이드
* **Formatter:** `Black`을 사용하여 코드 포맷을 통일합니다.
* **Linter:** `Flake8`을 사용하여 문법 오류와 스타일을 점검합니다.
* **Naming:**
    * 변수/함수: `snake_case`
    * 클래스: `PascalCase`
    * 상수: `UPPER_SNAKE_CASE`
    * 프라이빗 멤버: `_variable_name` (underscore prefix)

### Type Hinting & Docstrings
* 모든 함수의 인자와 반환값에 **Type Hint**를 필수적으로 명시합니다.
* 주요 클래스와 함수에는 **Google Style Docstring**을 작성합니다.

```python
def fetch_company_data(corp_code: str, year: int) -> dict[str, Any]:
    """
    특정 기업의 연도별 데이터를 수집합니다.

    Args:
        corp_code (str): 기업 고유 코드
        year (int): 대상 연도

    Returns:
        dict[str, Any]: 수집된 데이터 딕셔너리
    """
    pass

```

---

## 3. 데이터베이스 및 모델링

* **PostgreSQL (pgvector):** 벡터 데이터와 메타데이터를 함께 저장합니다.
* **Schema:** 소스(DART, News, Web)에 따라 유연하게 대응할 수 있도록 `JSONB` 컬럼 활용을 고려하되, 핵심 필드(날짜, 제목 등)는 정규화합니다.
* **Migration:** DB 스키마 변경 시 반드시 마이그레이션 스크립트나 히스토리를 남깁니다.

---

## 4. Git 워크플로우

* **Branch:** `main` (배포), `develop` (개발), `feature/기능명` (개별 작업)
* **Commit Message (Conventional Commits):**
* `feat`: 새로운 기능 추가
* `fix`: 버그 수정
* `refactor`: 코드 리팩토링 (기능 변경 없음)
* `docs`: 문서 수정
* `test`: 테스트 코드 추가
* `chor`: 빌드 업무 수정, 패키지 매니저 수정



---

## 5. 에러 처리 및 로깅

* `print()` 사용을 지양하고 프로젝트 표준 `logger`를 사용합니다.
* 예외 발생 시 `try-except` 블록에서 단순히 `pass` 하지 않고, 에러 로그를 남기거나 상위로 전파(raise)합니다.

