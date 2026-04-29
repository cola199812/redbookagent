"""向量检索器"""
from typing import List, Optional, Dict, Any
from langchain_core.documents import Document as LCDocument
from langchain_community.vectorstores import Chroma
from app.knowledge_base.embedder import Embedder
from app.config import CHROMA_PERSIST_DIR, DEFAULT_TOP_K
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class Retriever:
    """向量检索器"""

    def __init__(
        self,
        collection_name: str = "knowledge_base",
        top_k: int = DEFAULT_TOP_K
    ):
        self.collection_name = collection_name
        self.top_k = top_k
        self.embedder = Embedder()
        self._vectorstore: Optional[Chroma] = None

    def _get_vectorstore(self) -> Chroma:
        """获取或创建向量存储"""
        if self._vectorstore is None:
            if not self.embedder.is_available():
                raise RuntimeError("Embedding 服务不可用")

            self._vectorstore = Chroma(
                collection_name=self.collection_name,
                persist_directory=str(CHROMA_PERSIST_DIR),
                embedding_function=self.embedder._embedder
            )
        return self._vectorstore

    def add_documents(
        self,
        documents: List[LCDocument],
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """添加文档到向量库"""
        logger.info(f"添加 {len(documents)} 个文档到向量库")
        vectorstore = self._get_vectorstore()

        if ids:
            return vectorstore.add_documents(documents, ids=ids)
        else:
            return vectorstore.add_documents(documents)

    def search(
        self,
        query: str,
        k: Optional[int] = None,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[LCDocument]:
        """搜索最相关的文档"""
        k = k or self.top_k
        logger.info(f"搜索 query: {query}, k={k}")

        vectorstore = self._get_vectorstore()
        results = vectorstore.similarity_search(
            query,
            k=k,
            filter=filter_dict
        )

        logger.info(f"找到 {len(results)} 个相关文档")
        return results

    def delete(self, ids: List[str]) -> None:
        """删除文档"""
        logger.info(f"删除 {len(ids)} 个文档")
        vectorstore = self._get_vectorstore()
        vectorstore.delete(ids)

    def count(self) -> int:
        """统计文档数量"""
        vectorstore = self._get_vectorstore()
        return vectorstore._collection.count()
