"""
임베딩 생성 모듈 - HuggingFace 모델을 사용한 텍스트 임베딩 생성
모델: sentence-transformers/paraphrase-multilingual-mpnet-base-v2 (768차원)
"""
import torch
from transformers import AutoTokenizer, AutoModel
from typing import List, Optional
from config import EMBEDDING_CONFIG


class EmbeddingGenerator:
    """
    HuggingFace 모델을 사용한 텍스트 임베딩 생성기
    """

    def __init__(self, model_name: str = None, device: str = None):
        """
        임베딩 생성기 초기화

        Args:
            model_name: HuggingFace 모델명 (기본: config.py 설정값)
            device: 연산 장치 ('cuda', 'cpu', 또는 None=자동 감지)
        """
        self.model_name = model_name or EMBEDDING_CONFIG.get(
            'hf_model',
            'sentence-transformers/paraphrase-multilingual-mpnet-base-v2'
        )

        # 디바이스 설정
        if device is None:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        else:
            self.device = device

        print(f"🔄 임베딩 모델 로딩 중: {self.model_name}")
        print(f"   디바이스: {self.device}")

        # 모델 및 토크나이저 로드
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModel.from_pretrained(self.model_name)
        self.model.to(self.device)
        self.model.eval()  # 추론 모드

        print(f"✅ 임베딩 모델 로드 완료 (차원: {self.get_dimension()})")

    def get_dimension(self) -> int:
        """임베딩 차원 수 반환"""
        return self.model.config.hidden_size

    def _mean_pooling(self, model_output, attention_mask) -> torch.Tensor:
        """
        Mean Pooling - attention mask를 고려한 평균 계산
        """
        token_embeddings = model_output[0]  # 모든 토큰 임베딩
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(
            input_mask_expanded.sum(1), min=1e-9
        )

    def embed_text(self, text: str) -> List[float]:
        """
        단일 텍스트 임베딩 생성

        Args:
            text: 임베딩할 텍스트

        Returns:
            List[float]: 임베딩 벡터
        """
        return self.embed_texts([text])[0]

    def embed_texts(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        여러 텍스트 배치 임베딩 생성

        Args:
            texts: 임베딩할 텍스트 리스트
            batch_size: 배치 크기

        Returns:
            List[List[float]]: 임베딩 벡터 리스트
        """
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]

            # 토큰화
            encoded_input = self.tokenizer(
                batch_texts,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors='pt'
            )
            encoded_input = {k: v.to(self.device) for k, v in encoded_input.items()}

            # 임베딩 생성
            with torch.no_grad():
                model_output = self.model(**encoded_input)

            # Mean pooling
            embeddings = self._mean_pooling(model_output, encoded_input['attention_mask'])

            # 정규화 (선택적이지만 유사도 검색에 유용)
            embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)

            # CPU로 이동 후 리스트 변환
            embeddings = embeddings.cpu().tolist()
            all_embeddings.extend(embeddings)

        return all_embeddings

