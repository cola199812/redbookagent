"""Embedding 模型封装"""
from typing import List, Optional
from langchain_community.embeddings import DashScopeEmbeddings
from app.config import DASHSCOPE_API_KEY, EMBEDDING_MODEL
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class Embedder:
    """Embedding 模型封装"""

    def __init__(
        self,
        model: str = EMBEDDING_MODEL,
        api_key: str = DASHSCOPE_API_KEY
    ):
        self.model = model
        self.api_key = api_key

        if not api_key:
            logger.warning("未设置 DASHSCOPE_API_KEY，Embedding 功能将不可用")

        self._embedder = DashScopeEmbeddings(
            model=model,
            dashscope_api_key=api_key
        ) if api_key else None

    def embed_query(self, text: str) -> List[float]:
        """单个文本嵌入"""
        if not self._embedder:
            raise RuntimeError("Embedding 未初始化，请检查 API_KEY")
        return self._embedder.embed_query(text)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """批量文本嵌入"""
        if not self._embedder:
            raise RuntimeError("Embedding 未初始化，请检查 API_KEY")
        return self._embedder.embed_documents(texts)

    def is_available(self) -> bool:
        """检查是否可用"""
        return self._embedder is not None
