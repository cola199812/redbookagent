"""文档加载器 - 支持 txt/md/pdf/JSON"""
import json
from pathlib import Path
from typing import List, Union
from langchain_community.document_loaders import (
    TextLoader,
    UnstructuredMarkdownLoader,
    PyPDFLoader,
)
from langchain_core.documents import Document as LCDocument
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class DocumentLoader:
    """统一的文档加载器"""

    SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf", ".json"}

    @classmethod
    def load_file(cls, file_path: Union[str, Path]) -> List[LCDocument]:
        """加载单个文件"""
        path = Path(file_path)
        suffix = path.suffix.lower()

        if suffix not in cls.SUPPORTED_EXTENSIONS:
            raise ValueError(f"不支持的文件类型: {suffix}")

        logger.info(f"加载文件: {path}")

        if suffix == ".txt":
            loader = TextLoader(str(path), encoding="utf-8")
        elif suffix == ".md":
            loader = UnstructuredMarkdownLoader(str(path))
        elif suffix == ".pdf":
            loader = PyPDFLoader(str(path))
        elif suffix == ".json":
            return cls._load_json(path)

        documents = loader.load()
        logger.info(f"成功加载 {len(documents)} 个文档块")
        return documents

    @classmethod
    def _load_json(cls, path: Path) -> List[LCDocument]:
        """加载JSON文件"""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            documents = []
            for i, item in enumerate(data):
                content = json.dumps(item, ensure_ascii=False)
                doc = LCDocument(
                    page_content=content,
                    metadata={"source": str(path), "index": i, "type": "json"}
                )
                documents.append(doc)
            return documents
        else:
            content = json.dumps(data, ensure_ascii=False)
            return [LCDocument(
                page_content=content,
                metadata={"source": str(path), "type": "json"}
            )]

    @classmethod
    def load_batch(cls, file_paths: List[Union[str, Path]]) -> List[LCDocument]:
        """批量加载文件"""
        all_documents = []
        for file_path in file_paths:
            try:
                docs = cls.load_file(file_path)
                all_documents.extend(docs)
            except Exception as e:
                logger.error(f"加载文件失败 {file_path}: {e}")
        return all_documents
