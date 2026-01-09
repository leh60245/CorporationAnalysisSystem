# 기업 분석 보고서 시스템

DART API를 통해 기업 사업보고서를 수집하고, 계층적 구조로 파싱하여 PostgreSQL DB에 적재하는 파이프라인입니다.
테이블/텍스트 분리 저장을 통해 AI 기반 보고서 작성에 최적화된 데이터를 제공합니다.

## 🎯 주요 기능

- ✅ DART API를 통한 사업보고서 자동 수집
- ✅ 계층적 섹션 파싱 (Chapter → Section → Sub-Section)
- ✅ 테이블/텍스트 분리 저장 (JSON)
- ✅ 청킹 시 내용 흐름 유지 (sub-section 단위)
- ✅ HuggingFace 모델 기반 임베딩 생성
- ✅ pgvector를 활용한 벡터 검색 지원

## 📁 프로젝트 구조 (정리됨!)

```
CorporationAnalysis/
├── src/                         # 📦 소스 코드
│   ├── core/                    # 핵심 비즈니스 로직
│   │   ├── __init__.py
│   │   ├── db_manager.py        # 💾 DB 관리
│   │   ├── dart_agent.py        # 📡 DART API
│   │   ├── pipeline.py          # 🔄 파이프라인
│   │   └── embedding_pipeline.py # 🔗 임베딩 파이프라인
│   │
│   └── utils/                   # 유틸리티
│       ├── __init__.py
│       └── embedding_generator.py # 🤖 임베딩 생성
│
├── tests/                       # 🧪 테스트 코드
│   ├── __init__.py
│   ├── test_db.py              # DB 테스트
│   ├── test_dart_agent.py      # DART Agent 테스트
│   └── test_pipeline.py        # 파이프라인 테스트
│
├── scripts/                     # 📜 유틸리티 스크립트
│   ├── check_db.py             # ✅ DB 검증
│   └── explore_report_structure.py # 🔍 구조 탐색
│
├── docs/                        # 📖 문서
│   └── adr/                     # Architecture Decision Records
│
├── config.py                    # ⚙️ 설정
├── main.py                      # 🚀 메인 실행 파일
├── README.md                    # 📖 프로젝트 문서
├── REFACTORING_REPORT.md        # 📋 리팩토링 보고서
├── requirements.txt             # 📦 의존성
└── .env                         # 🔐 환경변수
```

## 🚀 시작하기

### 설치

```bash
pip install -r requirements.txt
```

### 환경 설정

`.env` 파일에 다음 정보를 설정하세요:

```env
# DART API
DART_API_KEY=your_dart_api_key

# PostgreSQL
DB_HOST=localhost
DB_NAME=your_database
DB_USER=postgres
DB_PASSWORD=your_password
DB_PORT=5432
```

## 💻 사용법

### 1. 파이프라인 실행

#### 테스트 모드 (삼성전자, SK하이닉스, NAVER)
```bash
python main.py --test
```

#### 특정 종목코드 처리
```bash
python main.py --codes 005930 000660 035420
```

#### 전체 상장 기업 처리
```bash
python main.py --all
python main.py --all --reset    # DB 초기화 후 처리
python main.py --all --limit 100  # 최대 100개 기업만 처리
```

#### 효율 모드 (권장) ⚡
사업보고서가 있는 기업만 일괄 검색하여 처리하는 효율적인 방식입니다.
기존 방식보다 API 호출 횟수를 대폭 줄여 빠르게 실행됩니다.

```bash
# 기본 실행 (최근 3개월 사업보고서)
python main.py --efficient

# 기간 지정 (YYYYMMDD 형식)
python main.py --efficient --bgn 20250101 --end 20250331

# DB 초기화 후 실행
python main.py --efficient --reset

# 최대 처리 개수 제한 (테스트용)
python main.py --efficient --limit 10

# 조합 사용
python main.py --efficient --bgn 20240101 --end 20241231 --reset --limit 50
```

**효율 모드 vs 기존 방식:**
- **기존 방식 (`--all`)**: ~2,600개 상장사 전체 순회 → 각각 API 호출하여 보고서 확인
- **효율 모드 (`--efficient`)**: 기간 내 사업보고서 일괄 검색 → 해당 기업만 처리
- **결과**: API 호출 횟수 90% 이상 감소, 실행 시간 대폭 단축

### 2. 테스트 실행

#### DB 테스트
```bash
python tests/test_db.py                 # 전체 DB 테스트
python tests/test_db.py --connection    # 연결 테스트만
python tests/test_db.py --stats         # 통계 조회만
python tests/test_db.py --crud          # CRUD 기능 테스트 포함
```

#### DART Agent 테스트
```bash
python tests/test_dart_agent.py              # 삼성전자 전체 테스트
python tests/test_dart_agent.py --stock 000660  # SK하이닉스 테스트
python tests/test_dart_agent.py --functions  # 기능 테스트만
```

#### 파이프라인 통합 테스트
```bash
python tests/test_pipeline.py              # 삼성전자 전체 테스트
python tests/test_pipeline.py --top3       # 상위 3개 기업 테스트
python tests/test_pipeline.py --stock 005930  # 특정 종목 테스트
python tests/test_pipeline.py --quality    # 데이터 품질 검증만
python tests/test_pipeline.py --quick      # 빠른 테스트 (DB 초기화 없이)
```

### 3. 유틸리티 스크립트

#### DB 검증 및 통계
```bash
python scripts/check_db.py              # 전체 검증
python scripts/check_db.py --stats      # 통계만
python scripts/check_db.py --sample     # 샘플 데이터 조회
python scripts/check_db.py --tables     # 테이블 샘플 조회
```

#### Generated_Reports 테이블 검증
```bash
python scripts/test_generated_reports.py  # AI 리포트 테이블 검증
```

#### 보고서 구조 탐색
```bash
python scripts/explore_report_structure.py   # 대화형 모드
python main.py --explore                     # main을 통한 실행
```

### 4. 임베딩 생성

```bash
python src/core/embedding_pipeline.py                 # 전체 임베딩 생성
python src/core/embedding_pipeline.py --batch-size 16 # 배치 크기 조정
python src/core/embedding_pipeline.py --limit 100     # 최대 100개만 처리
python src/core/embedding_pipeline.py --report 1      # 특정 리포트만
```

## 🗄️ DB 스키마
DART_API_KEY=your_dart_api_key

# PostgreSQL
DB_HOST=localhost
DB_NAME=your_database
DB_USER=postgres
DB_PASSWORD=your_password
DB_PORT=5432

## 사용법

### 테스트 모드 (3개 기업)
```bash
python main.py --test
```
삼성전자, SK하이닉스, NAVER 3개 기업으로 테스트합니다.

### 특정 종목코드 처리
```bash
python main.py --codes 005930 000660 035420
```

### 전체 상장 기업 처리
```bash
python main.py --all
python main.py --all --reset    # DB 초기화 후 처리
python main.py --all --limit 100  # 최대 100개 기업만 처리
```

### DB 통계 조회
```bash
python main.py --stats
```

### 보고서 구조 탐색
```bash
python main.py --explore
```

### DB 추가
```bash
python -c "from src.core.db_manager import DBManager; db = DBManager(); db.__enter__(); db.init_db(); db.__exit__(None, None, None); print('DONE')"
```

## 핵심 섹션

현재 다음 3개 섹션을 추출합니다:
- **회사의 개요**: 기업 기본 정보
- **사업의 내용**: 사업 현황 및 전략
- **재무에 관한 사항**: 재무제표 및 재무 분석

## DB 스키마

### Companies (기업 정보)
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | SERIAL | PK |
| company_name | VARCHAR(255) | 기업명 (UNIQUE) |
| corp_code | VARCHAR(20) | DART 법인코드 |
| stock_code | VARCHAR(20) | 종목코드 |
| industry | VARCHAR(100) | 업종 |

### Analysis_Reports (분석 리포트)
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | SERIAL | PK |
| company_id | INTEGER | FK → Companies |
| title | VARCHAR(500) | 보고서 제목 |
| rcept_no | VARCHAR(20) | 접수번호 (UNIQUE) |
| rcept_dt | VARCHAR(10) | 접수일자 |
| basic_info | JSONB | 추가 메타데이터 |
| status | VARCHAR(50) | 처리 상태 |

### Source_Materials (원천 데이터) ⭐ 개선됨
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | SERIAL | PK |
| report_id | INTEGER | FK → Analysis_Reports |
| **chunk_type** | VARCHAR(20) | **블록 타입** (text/table) |
| section_path | TEXT | 섹션 경로 (예: "사업의 내용 > 1. 사업의 개요") |
| sequence_order | INTEGER | 순서 번호 |
| raw_content | TEXT | 텍스트 또는 테이블 내용 |
| table_metadata | JSONB | 테이블 메타데이터 (구조, 컬럼 등) |
| embedding | VECTOR | 임베딩 벡터 (768차원) |
| metadata | JSONB | 추가 메타데이터 |

### Generated_Reports (AI 생성 리포트) 🆕
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | SERIAL | PK |
| company_name | VARCHAR(100) | 기업명 |
| topic | TEXT | 리포트 주제 |
| report_content | TEXT | 리포트 본문 (Markdown) |
| toc_text | TEXT | 목차 |
| references_data | JSONB | 참고 자료 데이터 |
| conversation_log | JSONB | 대화 로그 |
| meta_info | JSONB | 메타 정보 (토큰, 처리시간 등) |
| model_name | VARCHAR(50) | 사용된 AI 모델 (기본: gpt-4o) |
| created_at | TIMESTAMP | 생성 일시 |

## 🎯 핵심 섹션

현재 다음 3개 섹션을 추출합니다:
- **회사의 개요**: 기업 기본 정보, 조직 구조
- **사업의 내용**: 사업 현황, 주요 제품, 시장 분석
- **재무에 관한 사항**: 재무제표, 재무 분석

각 섹션은 계층적으로 파싱됩니다:
```
Chapter (챕터)
└── Section (중단원: 1., 2., 3...)
    └── Sub-Section (소단원: 가., 나., 다...)
```

## ⚙️ 배치 처리 설정

`config.py`에서 Rate Limiting 설정을 조정할 수 있습니다:

```python
BATCH_CONFIG = {
    "batch_size": 50,           # 배치당 처리 기업 수
    "batch_delay_sec": 3,       # 배치 간 대기 시간
    "request_delay_sec": 0.1,   # 개별 요청 간 대기 시간
    "max_retries": 3,           # 실패 시 재시도 횟수
    "retry_delay_sec": 5        # 재시도 전 대기 시간
}
```

DART API는 분당 1,000회 제한이 있으므로, 기본 설정은 안전하게 분당 약 900회로 제한됩니다.

## 📊 데이터 흐름

```
1. DART API
   ↓
2. DartReportAgent (보고서 수집 및 파싱)
   ↓
3. 계층적 파싱 (chapter/section/sub_section)
   ↓
4. 테이블/텍스트 분리
   ↓
5. 청킹 (내용 흐름 유지)
   ↓
6. DB 저장 (Source_Materials)
   ↓
7. EmbeddingPipeline (임베딩 생성)
   ↓
8. 벡터 검색 준비 완료
```

## 🧪 테스트 전략

### 단위 테스트
- `test_db.py`: DB 연결, 스키마, CRUD 기능
- `test_dart_agent.py`: DART API, 섹션 추출, 청킹

### 통합 테스트  
- `test_pipeline.py`: 전체 파이프라인, 데이터 품질 검증

### 검증 스크립트
- `check_db.py`: DB 상태 확인, 통계 조회

## 🔜 다음 단계

1. ✅ **데이터 수집 파이프라인** (완료)
2. ✅ **계층적 파싱 및 테이블 분리** (완료)
3. ⏳ **임베딩 생성 완료** (진행 중)
4. 🔲 **RAG 구현**: pgvector를 활용한 유사도 검색
5. 🔲 **LLM 통합**: GPT-4/Claude를 활용한 보고서 생성
6. 🔲 **웹 인터페이스**: Streamlit 기반 대시보드

## 📝 참고사항

### 데이터 특징
- **삼성전자 사업보고서** 기준:
  - 회사의 개요: 29개 섹션, 44개 테이블
  - 사업의 내용: 30개 섹션, 95개 테이블
  - 재무에 관한 사항: 457개 섹션, 1155개 테이블
  - **총 566개 청크** 저장

### 테이블 저장 예시
```json
{
  "table_index": 0,
  "data": [
    {"부문": "DX 부문", "주요 제품": "TV, 모니터, ..."},
    {"부문": "DS 부문", "주요 제품": "DRAM, NAND Flash, ..."}
  ]
}
```

## 📄 라이선스

MIT License

## 👥 기여

이슈와 PR은 언제나 환영합니다!
