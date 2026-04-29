"""知识库管理器 - 整合文档加载、切分、存储和检索"""
from pathlib import Path
from typing import List, Union, Optional, Dict, Any
from langchain_core.documents import Document as LCDocument
from app.knowledge_base.loader import DocumentLoader
from app.knowledge_base.chunker import DocumentChunker
from app.knowledge_base.retriever import Retriever
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class KnowledgeBaseManager:
    """知识库管理器"""

    def __init__(self, collection_name: str = "knowledge_base"):
        self.loader = DocumentLoader()
        self.chunker = DocumentChunker()
        self.retriever = Retriever(collection_name=collection_name)

    def add_documents(
        self,
        file_paths: List[Union[str, Path]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        添加文档到知识库

        返回: {
            "total_files": int,
            "total_chunks": int,
            "ids": List[str]
        }
        """
        logger.info(f"开始添加 {len(file_paths)} 个文件")

        raw_documents = self.loader.load_batch(file_paths)

        for doc in raw_documents:
            if metadata:
                doc.metadata.update(metadata)
            doc.metadata["source_file"] = str(file_paths)

        chunks = self.chunker.split_documents(raw_documents)
        ids = self.retriever.add_documents(chunks)

        logger.info(f"文档添加完成: {len(file_paths)} 个文件, {len(chunks)} 个chunks")

        return {
            "total_files": len(file_paths),
            "total_chunks": len(chunks),
            "ids": ids
        }

    def add_text(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """添加单段文本到知识库"""
        chunks = self.chunker.split_text(text)
        documents = [
            LCDocument(page_content=chunk, metadata=metadata or {})
            for chunk in chunks
        ]

        self.retriever.add_documents(documents)
        return documents[0].id if documents else None

    def search(
        self,
        query: str,
        k: int = 5,
        source_filter: Optional[str] = None,
        date_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """搜索知识库"""
        filter_dict = {}
        if source_filter:
            filter_dict["source"] = source_filter

        results = self.retriever.search(query, k=k, filter_dict=filter_dict if filter_dict else None)

        return [
            {
                "content": doc.page_content,
                "metadata": doc.metadata
            }
            for doc in results
        ]

    def delete(self, ids: List[str]) -> None:
        """删除文档"""
        self.retriever.delete(ids)

    def list_documents(self) -> List[Dict[str, Any]]:
        """列出所有文档摘要"""
        count = self.retriever.count()
        return [{"total_chunks": count}]
