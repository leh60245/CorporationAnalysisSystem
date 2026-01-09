"""
설정 모듈 - 환경변수, API 키, DB 설정, 배치 설정 중앙 관리
"""
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()


# === DART API 설정 ===
DART_API_KEY = os.getenv("DART_API_KEY")

# === Database 설정 ===
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", "postgres"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD"),
    "port": os.getenv("DB_PORT", "5432")
}

# === 배치 처리 설정 ===
# DART API: 분당 1,000회 제한 -> 안전하게 분당 900회로 설정
BATCH_CONFIG = {
    "batch_size": 50,           # 배치당 처리할 기업 수
    "batch_delay_sec": 3,       # 배치 간 대기 시간 (초)
    "request_delay_sec": 0.1,   # 개별 요청 간 대기 시간 (초)
    "max_retries": 3,           # 실패 시 재시도 횟수
    "retry_delay_sec": 5        # 재시도 전 대기 시간 (초)
}

# === 사업보고서 섹션 설정 ===
# 핵심 섹션 (DART API에서 반환되는 실제 섹션명으로 업데이트 필요)
TARGET_SECTIONS = [
    "회사의 개요",
    "사업의 내용",
    "재무에 관한 사항"
]

# === 청킹 설정 ===
CHUNK_CONFIG = {
    "max_chunk_size": 2000,     # 청크 최대 문자 수
    "overlap": 200,             # 청크 간 오버랩 문자 수
    "min_chunk_size": 100       # 최소 청크 크기 (이보다 작으면 이전 청크에 병합)
}

# === 임베딩 설정 ===
EMBEDDING_CONFIG = {
    "hf_model": "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
    "dimension": 768,                    # 벡터 차원 수
    "batch_size": 32,                    # 임베딩 배치 크기
    "max_length": 512                    # 최대 토큰 길이
}

# === 보고서 검색 설정 ===
REPORT_SEARCH_CONFIG = {
    "bgn_de": "20240101",       # 검색 시작일 (YYYYMMDD)
    "pblntf_detail_ty": "a001", # 사업보고서 유형 코드
    "page_count": 100,          # 한 페이지당 최대 건수 (기본값 10, 최대 100)
    "page_delay_sec": 0.5,      # 페이지 간 API 호출 대기 (Rate Limiting)
    "max_search_days": 90       # corp_code 없을 때 최대 검색 기간 (일) - 3개월
}

