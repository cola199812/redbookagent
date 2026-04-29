"""文档切片器"""
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document as LCDocument
from app.config import CHUNK_SIZE, CHUNK_OVERLAP
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class DocumentChunker:
    """文档切片器"""

    def __init__(
        self,
        chunk_size: int = CHUNK_SIZE,
        chunk_overlap: int = CHUNK_OVERLAP
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", "。", "！", "？", " ", ""]
        )

    def split_documents(
        self,
        documents: List[LCDocument]
    ) -> List[LCDocument]:
        """将文档列表切分成小块"""
        logger.info(f"开始切片 {len(documents)} 个文档")

        splits = self.splitter.split_documents(documents)

        for i, split in enumerate(splits):
            split.metadata["chunk_index"] = i
            split.metadata["total_chunks"] = len(splits)

        logger.info(f"切片完成: {len(splits)} 个chunks")
        return splits

    def split_text(self, text: str) -> List[str]:
        """将单段文本切分成小块"""
        return self.splitter.split_text(text)
