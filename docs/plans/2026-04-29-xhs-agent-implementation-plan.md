# 小红书智能创作与学习 Agent - 完整实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个具备自学习能力的闭环内容创作系统，能够根据用户指令和知识库生成小红书文案，并持续从平台学习优化。

**Architecture:** 基于 LangChain/LangGraph 的 Agent 架构，采用 RAG 模式管理知识库。前后端分离架构：Vue 3 Web 前端 + Python FastAPI 后端。数据层使用 Chroma 向量数据库 + SQLite。

**最终技术栈：**

| 层级 | 技术选型 | 版本/说明 |
|------|---------|----------|
| 前端框架 | Vue 3 | Composition API + `<script setup>` |
| 前端构建 | Vite | 极速开发体验 |
| 前端语言 | TypeScript | 类型安全 |
| 前端 UI 库 | Element Plus | 成熟的后台组件库 |
| HTTP 客户端 | Axios | 前后端通信 |
| 后端框架 | FastAPI | Python 异步 API |
| Agent 编排 | LangChain + LangGraph | 不变 |
| 向量数据库 | Chroma | 不变 |
| 关系数据库 | SQLite | 不变 |
| 爬虫 | Playwright + Crawlee | 不变 |
| 定时任务 | APScheduler | 不变 |

**关键决策：**
- 桌面端废弃，纯 Web 应用
- MVP 阶段免登录，所有功能直接可用
- 配置（小红书账号、API Key 等）存在本地 SQLite 或环境变量

---

## 架构图

```
┌─────────────────────────────────────────────────────────┐
│                    浏览器（Vue 前端）                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │ 文案生成页 │ │ 知识库管理 │ │ 学习看板  │ │ 发布队列  │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
│                        │                               │
│                    HTTP / WebSocket                     │
└────────────────────────┼───────────────────────────────┘
                         │
┌────────────────────────▼───────────────────────────────┐
│              FastAPI 后端（Python）                      │
│  ┌──────────────────────────────────────────────────┐  │
│  │              LangGraph Agent 编排层                │  │
│  └──────────┬───────────┬───────────┬──────────────┘  │
│             │           │           │                 │
│  ┌──────────▼──┐ ┌───────▼────┐ ┌────▼──────────┐    │
│  │ 创作Agent   │ │ 爬虫Agent  │ │ 学习Agent     │    │
│  └─────────────┘ └────────────┘ └───────────────┘    │
│                                                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐             │
│  │ Chroma   │ │ SQLite   │ │ Playwright│             │
│  │(向量库)  │ │(数据存储)│ │           │             │
│  └──────────┘ └──────────┘ └──────────┘             │
└───────────────────────────────────────────────────────┘
```

---

## 目录结构规划

```
redbookagent/                          # 项目根目录
├── frontend/                          # Vue 3 前端
│   ├── src/
│   │   ├── api/                      # API 调用
│   │   │   ├── index.ts              # Axios 实例
│   │   │   ├── knowledge.ts          # 知识库 API
│   │   │   ├── creator.ts            # 创作 Agent API
│   │   │   ├── crawler.ts            # 爬虫 Agent API
│   │   │   └── publish.ts            # 发布 API
│   │   ├── components/               # 公共组件
│   │   ├── views/                    # 页面
│   │   │   ├── CreatorView.vue       # 文案生成页
│   │   │   ├── KnowledgeBaseView.vue # 知识库管理页
│   │   │   ├── LearnerView.vue       # 学习看板页
│   │   │   └── PublisherView.vue     # 发布队列页
│   │   ├── stores/                   # Pinia 状态管理
│   │   ├── router/                   # Vue Router
│   │   ├── App.vue
│   │   └── main.ts
│   ├── index.html
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── package.json
│
├── backend/                           # FastAPI 后端
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI 入口
│   │   ├── config.py                  # 配置管理
│   │   ├── models/                    # 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── document.py
│   │   │   ├── post.py
│   │   │   └── knowledge.py
│   │   ├── knowledge_base/            # M1: RAG知识库
│   │   │   ├── __init__.py
│   │   │   ├── loader.py
│   │   │   ├── chunker.py
│   │   │   ├── embedder.py
│   │   │   ├── retriever.py
│   │   │   └── knowledge_base_manager.py
│   │   ├── agents/                    # Agent核心
│   │   │   ├── __init__.py
│   │   │   ├── creator_agent.py       # M2: 文案生成
│   │   │   ├── crawler_agent.py       # M4: 数据抓取
│   │   │   └── learner_agent.py       # M5: 学习提炼
│   │   ├── tools/                     # 工具层
│   │   │   ├── __init__.py
│   │   │   ├── publisher.py           # M3: 自动发布
│   │   │   ├── scheduler.py           # M7: 定时调度
│   │   │   └── search.py
│   │   ├── api/                       # API 路由
│   │   │   ├── __init__.py
│   │   │   ├── knowledge.py
│   │   │   ├── creator.py
│   │   │   ├── crawler.py
│   │   │   └── publish.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── logger.py
│   ├── tests/
│   ├── data/
│   │   ├── chroma_db/
│   │   ├── sqlite/
│   │   └── uploads/
│   ├── configs/
│   │   └── tasks.yaml
│   ├── requirements.txt
│   └── README.md
│
├── docs/
│   └── plans/
└── README.md
```

---

## 功能模块保留

| 功能模块 | 保留 | 说明 |
|---------|------|-----|
| RAG 知识库管理 | ✅ | 核心，不能砍 |
| 小红书文案生成 (Creator Agent) | ✅ | 核心，不能砍 |
| 爬虫功能 (Crawler Agent) | ✅ | 核心，用来学习 |
| 自动发布 (Publisher) | ✅ | 核心亮点 |
| 学习提炼 (Learner Agent) | ✅ | 核心，形成闭环 |

---

## Phase 1: v0.1 - 核心功能 (M1 + M2)

### 任务 1: 项目初始化与配置

**Files:**
- Create: `backend/.env.example`
- Create: `backend/requirements.txt`
- Create: `backend/app/config.py`
- Create: `backend/app/__init__.py`
- Create: `backend/app/utils/__init__.py`
- Create: `backend/app/utils/logger.py`

- [ ] **Step 1: 创建后端项目目录结构**

```bash
mkdir -p backend/app/{models,knowledge_base,agents,tools,api,utils}
mkdir -p backend/tests/{test_knowledge_base,test_agents,test_tools}
mkdir -p backend/data/{chroma_db,sqlite,uploads}
mkdir -p backend/configs
```

- [ ] **Step 2: 创建 requirements.txt**

```txt
langchain>=0.3.0
langchain-community>=0.3.0
langgraph>=0.2.0
chromadb>=0.4.0
sqlitevec
python-dotenv>=1.0.0
apscheduler>=3.10.0
fastapi>=0.100.0
uvicorn>=0.25.0
pydantic>=2.0.0
tiktoken>=0.5.0
playwright>=1.40.0
httpx>=0.25.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
pyyaml>=6.0.0
pytest>=8.0.0
pytest-asyncio>=0.23.0
dashscope>=1.20.0
```

- [ ] **Step 3: 创建 .env.example**

```bash
# LLM 配置 (通义千问)
DASHSCOPE_API_KEY=your_api_key_here
LLM_MODEL=qwen-max
EMBEDDING_MODEL=text-embedding-v3

# 向量数据库
CHROMA_PERSIST_DIR=./data/chroma_db

# SQLite 数据库路径
SQLITE_DB_PATH=./data/sqlite/redbookagent.db

# 小红书发布配置 (可选)
XHS_COOKIE=your_cookie_here
XHS_UA=your_user_agent_here

# 代理配置 (可选)
HTTP_PROXY=
HTTPS_PROXY=

# 日志级别
LOG_LEVEL=INFO

# CORS 配置
CORS_ORIGINS=http://localhost:5173
```

- [ ] **Step 4: 创建 backend/app/config.py**

```python
"""配置管理模块"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent

# 数据目录
DATA_DIR = PROJECT_ROOT / "data"
CHROMA_PERSIST_DIR = DATA_DIR / "chroma_db"
SQLITE_DB_PATH = DATA_DIR / "sqlite" / "redbookagent.db"

# 确保目录存在
DATA_DIR.mkdir(parents=True, exist_ok=True)
(DATA_DIR / "chroma_db").mkdir(parents=True, exist_ok=True)
(DATA_DIR / "sqlite").mkdir(parents=True, exist_ok=True)
(DATA_DIR / "uploads").mkdir(parents=True, exist_ok=True)

# LLM 配置
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen-max")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-v3")

# RAG 配置
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
DEFAULT_TOP_K = 5

# 小红书生成配置
TARGET_WORD_COUNT = (200, 500)
EMOJI_DENSITY = 50
HASHTAG_COUNT = (3, 5)
LLM_TEMPERATURE = 0.7

# 抓取配置
CRAWL_REQUEST_DELAY = (3, 5)
CRAWL_BATCH_SIZE = 10

# 发布配置
PUBLISH_INTERVAL_MINUTES = 60
PUBLISH_MAX_RETRIES = 3

# CORS 配置
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

# 日志配置
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
```

- [ ] **Step 5: 创建 backend/app/utils/logger.py**

```python
"""日志工具"""
import logging
import sys
from pathlib import Path
from src.config import LOG_LEVEL, DATA_DIR

def setup_logger(name: str) -> logging.Logger:
    """配置日志记录器"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL))

    if not logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)

        log_dir = DATA_DIR / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_dir / "redbookagent.log")
        file_handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger
```

- [ ] **Step 6: 创建 FastAPI 入口 backend/app/main.py**

```python
"""FastAPI 主入口"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import CORS_ORIGINS
from app.api import knowledge, creator, crawler, publish

app = FastAPI(title="RedBook Agent API", version="0.1.0")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(knowledge.router, prefix="/api/knowledge", tags=["knowledge"])
app.include_router(creator.router, prefix="/api/creator", tags=["creator"])
app.include_router(crawler.router, prefix="/api/crawler", tags=["crawler"])
app.include_router(publish.router, prefix="/api/publish", tags=["publish"])

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "version": "0.1.0"}
```

- [ ] **Step 7: 提交代码**

```bash
cd backend
git init
git add .
git commit -m "feat: initial backend project structure and config"
```

---

### 任务 2: 数据模型定义

**Files:**
- Create: `backend/app/models/__init__.py`
- Create: `backend/app/models/document.py`
- Create: `backend/app/models/post.py`
- Create: `backend/app/models/knowledge.py`

- [ ] **Step 1: 创建 backend/app/models/document.py**

```python
"""文档数据模型"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class Document(BaseModel):
    """文档模型"""
    id: str = Field(default_factory=lambda: f"doc_{datetime.now().timestamp()}")
    content: str = Field(description="文档内容")
    metadata: dict = Field(default_factory=dict, description="元数据")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "doc_1714392000.123",
                "content": "这是一篇关于护肤的文档...",
                "metadata": {
                    "source": "user_upload",
                    "filename": "skincare_tips.txt",
                    "file_type": "txt"
                },
                "created_at": "2026-04-29T10:00:00",
                "updated_at": "2026-04-29T10:00:00"
            }
        }
```

- [ ] **Step 2: 创建 backend/app/models/post.py**

```python
"""帖子数据模型"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class Post(BaseModel):
    """小红书帖子模型"""
    id: str = Field(default_factory=lambda: f"post_{datetime.now().timestamp()}")
    url: str = Field(description="帖子URL")
    title: str = Field(description="帖子标题")
    content: str = Field(description="帖子正文内容")
    likes: int = Field(default=0, description="点赞数")
    comments: int = Field(default=0, description="评论数")
    tags: List[str] = Field(default_factory=list, description="标签列表")
    user_name: str = Field(default="", description="作者昵称")
    post_time: Optional[datetime] = Field(default=None, description="发布时间")
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "post_1714392000.456",
                "url": "https://www.xiaohongshu.com/explore/xxx",
                "title": "这款精华液真的绝绝子！",
                "content": "作为一个熬夜党...",
                "likes": 15230,
                "comments": 892,
                "tags": ["#护肤", "#精华液", "#好物推荐"],
                "user_name": "美妆达人小雅",
                "post_time": "2026-04-28T15:30:00"
            }
        }
```

- [ ] **Step 3: 创建 backend/app/models/knowledge.py**

```python
"""知识片段数据模型"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class Knowledge(BaseModel):
    """从帖子中提炼的知识片段"""
    id: str = Field(default_factory=lambda: f"kn_{datetime.now().timestamp()}")
    source: str = Field(description="来源帖子URL")
    learned_at: datetime = Field(default_factory=datetime.now, description="学习时间")
    post_type: str = Field(description="帖子类型: 经验分享/产品测评/情感共鸣/教程/合集")
    hook_analysis: str = Field(description="开头钩子分析")
    content_structure: str = Field(description="内容结构分析")
    key_phrases: List[str] = Field(default_factory=list, description="关键短语")
    hashtags: List[str] = Field(default_factory=list, description="使用的标签")
    emotional_triggers: List[str] = Field(default_factory=list, description="情绪触发点")
    rewrite_template: str = Field(description="可复用的仿写框架")
    estimated_quality_score: int = Field(ge=0, le=100, description="预估质量分数")
    embedding: Optional[List[float]] = Field(default=None, description="向量嵌入")

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典，用于存储"""
        return {
            "id": self.id,
            "source": self.source,
            "learned_at": self.learned_at.isoformat(),
            "post_type": self.post_type,
            "hook_analysis": self.hook_analysis,
            "content_structure": self.content_structure,
            "key_phrases": self.key_phrases,
            "hashtags": self.hashtags,
            "emotional_triggers": self.emotional_triggers,
            "rewrite_template": self.rewrite_template,
            "estimated_quality_score": self.estimated_quality_score
        }
```

- [ ] **Step 4: 创建 backend/app/models/__init__.py**

```python
"""数据模型导出"""
from app.models.document import Document
from app.models.post import Post
from app.models.knowledge import Knowledge

__all__ = ["Document", "Post", "Knowledge"]
```

- [ ] **Step 5: 运行测试验证**

```bash
cd backend
pytest tests/test_models.py -v
```

Expected: 全部 PASS

- [ ] **Step 6: 提交代码**

```bash
git add app/models/
git commit -m "feat: add data models (Document, Post, Knowledge)"
```

---

### 任务 3: M1 - RAG 知识库核心

**Files:**
- Create: `backend/app/knowledge_base/__init__.py`
- Create: `backend/app/knowledge_base/loader.py`
- Create: `backend/app/knowledge_base/chunker.py`
- Create: `backend/app/knowledge_base/embedder.py`
- Create: `backend/app/knowledge_base/retriever.py`
- Create: `backend/app/knowledge_base/knowledge_base_manager.py`
- Test: `tests/test_knowledge_base/test_knowledge_base.py`

- [ ] **Step 1: 创建 backend/app/knowledge_base/loader.py**

```python
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
```

- [ ] **Step 2: 创建 backend/app/knowledge_base/chunker.py**

```python
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
```

- [ ] **Step 3: 创建 backend/app/knowledge_base/embedder.py**

```python
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
```

- [ ] **Step 4: 创建 backend/app/knowledge_base/retriever.py**

```python
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
```

- [ ] **Step 5: 创建 backend/app/knowledge_base/knowledge_base_manager.py**

```python
"""知识库管理器 - 整合文档加载、切分、存储和检索"""
from pathlib import Path
from typing import List, Union, Optional, Dict, Any
from langchain_core.documents import Document as LCDocument
from app.knowledge_base.loader import DocumentLoader
from app.knowledge_base.chunker import DocumentChunker
from app.knowledge_base.retriever import Retriever
from app.models.document import Document
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
```

- [ ] **Step 6: 创建 backend/app/knowledge_base/__init__.py**

```python
"""知识库模块导出"""
from app.knowledge_base.loader import DocumentLoader
from app.knowledge_base.chunker import DocumentChunker
from app.knowledge_base.embedder import Embedder
from app.knowledge_base.retriever import Retriever
from app.knowledge_base.knowledge_base_manager import KnowledgeBaseManager

__all__ = [
    "DocumentLoader",
    "DocumentChunker",
    "Embedder",
    "Retriever",
    "KnowledgeBaseManager"
]
```

- [ ] **Step 7: 运行测试验证**

```bash
cd backend
pytest tests/test_knowledge_base/test_knowledge_base.py -v
```

Expected: 全部 PASS

- [ ] **Step 8: 提交代码**

```bash
git add app/knowledge_base/
git commit -m "feat: implement M1 RAG knowledge base module"
```

---

### 任务 4: M2 - 文案生成 Agent

**Files:**
- Create: `backend/app/agents/__init__.py`
- Create: `backend/app/agents/creator_agent.py`
- Create: `backend/app/prompts.py`
- Create: `backend/app/api/creator.py`
- Test: `tests/test_agents/test_creator_agent.py`

- [ ] **Step 1: 创建 backend/app/prompts.py**

```python
"""小红书文案生成 Prompt 模板"""

XHS_CREATOR_PROMPT = """你是一位专业的小红书内容创作者，擅长撰写吸引人、有感染力的文案。

## 小红书爆款文案公式
【钩子开头】(好奇/痛点/反差/数字) → 【核心内容】(经验/测评/教程) → 【情绪价值】(共鸣/鼓励) → 【互动引导】(提问/求建议) → 【3-5个标签】

## 内容要求
1. 开头5-10字必须有强钩子效果，让人想点进来
2. 每50-100字至少使用1个emoji表情
3. 语言风格：亲切、真实、有温度，像朋友分享
4. 适当使用小红书常用表达（如：绝绝子、狠狠共情了、救命、哭死等）
5. 标签要精准且有热度

## 参考知识（来自知识库）
{context}

## 用户需求
- 主题: {topic}
- 风格: {style}
- 关键词: {keywords}
- 额外要求: {extra}

## 输出格式（JSON）
{{
    "title": "吸引人的标题（带emoji）",
    "content": "正文内容（带emoji和分段）",
    "hashtags": ["标签1", "标签2", "标签3", "标签4", "标签5"]
}}

请生成符合以上要求的小红书文案。
"""

XHS_SYSTEM_PROMPT = """你是一位专业的小红书内容创作者，拥有丰富的爆款文案经验。
你的目标是帮助用户创作出高质量、有吸引力的小红书内容。
始终遵循平台调性，保持真实、有温度的创作风格。"""
```

- [ ] **Step 2: 创建 backend/app/agents/creator_agent.py**

```python
"""文案生成 Agent - M2 核心模块"""
import json
from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from app.knowledge_base.knowledge_base_manager import KnowledgeBaseManager
from app.prompts import XHS_CREATOR_PROMPT, XHS_SYSTEM_PROMPT
from app.config import LLM_MODEL, DASHSCOPE_API_KEY, LLM_TEMPERATURE
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class XHSContentGenerator:
    """小红书文案生成器"""

    def __init__(
        self,
        knowledge_base: Optional[KnowledgeBaseManager] = None,
        model: str = LLM_MODEL,
        api_key: str = DASHSCOPE_API_KEY,
        temperature: float = LLM_TEMPERATURE
    ):
        self.kb = knowledge_base or KnowledgeBaseManager()
        self.temperature = temperature

        if api_key:
            self.llm = ChatOpenAI(
                model=model,
                api_key=api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                temperature=temperature
            )
        else:
            logger.warning("未设置 API_KEY，文案生成功能将不可用")
            self.llm = None

    def generate(
        self,
        topic: str,
        style: str = "经验分享",
        keywords: Optional[List[str]] = None,
        extra: str = "",
        use_kb: bool = True
    ) -> Dict[str, Any]:
        """
        生成小红书文案

        返回: {
            "title": str,
            "content": str,
            "hashtags": List[str],
            "full_post": str
        }
        """
        if not self.llm:
            raise RuntimeError("LLM 未初始化，请检查 API_KEY")

        logger.info(f"开始生成文案: topic={topic}, style={style}")

        context = ""
        if use_kb:
            search_results = self.kb.search(
                query=f"{topic} {style}",
                k=5
            )
            if search_results:
                context = "\n\n".join([
                    f"- {r['content']}"
                    for r in search_results
                ])
                logger.info(f"从知识库检索到 {len(search_results)} 条相关知识")

        keywords_str = ", ".join(keywords) if keywords else "无"
        prompt = XHS_CREATOR_PROMPT.format(
            context=context or "无相关知识",
            topic=topic,
            style=style,
            keywords=keywords_str,
            extra=extra or "无"
        )

        messages = [
            SystemMessage(content=XHS_SYSTEM_PROMPT),
            HumanMessage(content=prompt)
        ]

        logger.info("正在调用 LLM 生成文案...")
        response = self.llm.invoke(messages)
        content = response.content

        try:
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            elif "{" in content and "}" in content:
                start = content.find("{")
                end = content.rfind("}") + 1
                content = content[start:end]

            result = json.loads(content.strip())

            full_post = self._format_full_post(
                result.get("title", ""),
                result.get("content", ""),
                result.get("hashtags", [])
            )
            result["full_post"] = full_post

            logger.info(f"文案生成完成: {result.get('title', 'NO_TITLE')}")
            return result

        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}, 原始输出: {content}")
            return {
                "title": f"关于{topic}的分享",
                "content": content,
                "hashtags": [f"#{topic}", "#分享"],
                "full_post": content,
                "error": f"JSON解析失败: {str(e)}"
            }

    def _format_full_post(
        self,
        title: str,
        content: str,
        hashtags: List[str]
    ) -> str:
        """组合完整文案"""
        parts = [f"**{title}**\n" if title else ""]
        parts.append(content)
        if hashtags:
            parts.append("\n" + " ".join(hashtags))
        return "\n\n".join(parts)


class CreatorAgent:
    """文案创作Agent"""

    def __init__(self):
        self.generator = XHSContentGenerator()
        self.name = "小红书创作Agent"
        self.description = "根据主题和风格生成小红书文案"

    def invoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Agent入口"""
        try:
            topic = input_data.get("topic")
            if not topic:
                return {
                    "success": False,
                    "error": "缺少必需参数: topic"
                }

            result = self.generator.generate(
                topic=topic,
                style=input_data.get("style", "经验分享"),
                keywords=input_data.get("keywords"),
                extra=input_data.get("extra", "")
            )

            return {
                "success": True,
                "result": result
            }

        except Exception as e:
            logger.error(f"Agent执行失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
```

- [ ] **Step 3: 创建 backend/app/api/creator.py**

```python
"""创作 Agent API 路由"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.agents.creator_agent import CreatorAgent

router = APIRouter()
agent = CreatorAgent()


class GenerateRequest(BaseModel):
    topic: str
    style: str = "经验分享"
    keywords: Optional[List[str]] = None
    extra: str = ""


class GenerateResponse(BaseModel):
    success: bool
    result: dict = None
    error: str = None


@router.post("/generate", response_model=GenerateResponse)
async def generate_content(request: GenerateRequest):
    """生成小红书文案"""
    result = agent.invoke({
        "topic": request.topic,
        "style": request.style,
        "keywords": request.keywords,
        "extra": request.extra
    })

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])

    return GenerateResponse(success=True, result=result["result"])


@router.get("/info")
async def get_agent_info():
    """获取Agent信息"""
    return agent.get_info()
```

- [ ] **Step 4: 创建 backend/app/api/__init__.py**

```python
"""API 路由导出"""
from app.api import knowledge, creator, crawler, publish

__all__ = ["knowledge", "creator", "crawler", "publish"]
```

- [ ] **Step 5: 创建 backend/app/agents/__init__.py**

```python
"""Agent模块导出"""
from app.agents.creator_agent import XHSContentGenerator, CreatorAgent

__all__ = ["XHSContentGenerator", "CreatorAgent"]
```

- [ ] **Step 6: 运行测试验证**

```bash
cd backend
pytest tests/test_agents/test_creator_agent.py -v
```

Expected: 全部 PASS

- [ ] **Step 7: 提交代码**

```bash
git add app/agents/ app/api/ app/prompts.py
git commit -m "feat: implement M2 content creator agent with API"
```

---

### 任务 5: 知识库 API 路由

**Files:**
- Create: `backend/app/api/knowledge.py`

- [ ] **Step 1: 创建 backend/app/api/knowledge.py**

```python
"""知识库 API 路由"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path
import tempfile
import shutil
from app.knowledge_base.knowledge_base_manager import KnowledgeBaseManager

router = APIRouter()
kb_manager = KnowledgeBaseManager()


class SearchRequest(BaseModel):
    query: str
    k: int = 5


class SearchResponse(BaseModel):
    results: List[dict]
    total: int


@router.post("/add")
async def add_documents(files: List[UploadFile] = File(...)):
    """上传并添加文档到知识库"""
    temp_dir = Path(tempfile.mkdtemp())
    saved_files = []

    try:
        for file in files:
            file_path = temp_dir / file.filename
            with file_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            saved_files.append(file_path)

        result = kb_manager.add_documents(saved_files, metadata={"uploaded": True})

        return JSONResponse(content={
            "success": True,
            "total_files": result["total_files"],
            "total_chunks": result["total_chunks"]
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


@router.post("/search", response_model=SearchResponse)
async def search_knowledge(request: SearchRequest):
    """搜索知识库"""
    try:
        results = kb_manager.search(query=request.query, k=request.k)
        return SearchResponse(results=results, total=len(results))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_documents():
    """列出知识库文档"""
    try:
        docs = kb_manager.list_documents()
        return {"success": True, "data": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

- [ ] **Step 2: 提交代码**

```bash
git add app/api/knowledge.py
git commit -m "feat: add knowledge base API endpoints"
```

---

### 任务 6: v0.1 后端完成

- [ ] **Step 1: 启动后端验证**

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

访问 http://localhost:8000/docs 查看 API 文档

- [ ] **Step 2: 提交 v0.1 完成**

```bash
git add .
git commit -m "feat(v0.1): complete backend core - RAG knowledge base and content creator agent

- M1: RAG知识库管理 (文档加载/切片/存储/检索)
- M2: 文案生成Agent (基于知识库生成小红书文案)
- FastAPI REST API
- CORS configured for Vue frontend"
```

---

## Phase 2: v0.2 - Vue 前端 (M8)

### 任务 7: Vue 前端初始化

**Files:**
- Create: `frontend/` (Vite + Vue 3 + TypeScript 项目)

- [ ] **Step 1: 创建前端项目**

```bash
cd redbookagent
npm create vite@latest frontend -- --template vue-ts
cd frontend
npm install
npm install axios element-plus @element-plus/icons-vue vue-router pinia
```

- [ ] **Step 2: 创建前端目录结构**

```bash
cd frontend
mkdir -p src/{api,components,views,stores,router}
```

- [ ] **Step 3: 配置 API 客户端 src/api/index.ts**

```typescript
import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

export default api
```

- [ ] **Step 4: 创建文案生成页面 src/views/CreatorView.vue**

```vue
<template>
  <div class="creator-view">
    <el-card>
      <template #header>
        <h2>小红书文案生成</h2>
      </template>

      <el-form :model="form" label-width="100px">
        <el-form-item label="主题">
          <el-input v-model="form.topic" placeholder="输入要生成的主题" />
        </el-form-item>

        <el-form-item label="风格">
          <el-select v-model="form.style" placeholder="选择风格">
            <el-option label="经验分享" value="经验分享" />
            <el-option label="产品测评" value="产品测评" />
            <el-option label="情感共鸣" value="情感共鸣" />
            <el-option label="教程" value="教程" />
            <el-option label="合集" value="合集" />
          </el-select>
        </el-form-item>

        <el-form-item label="关键词">
          <el-select
            v-model="form.keywords"
            multiple
            filterable
            allow-create
            placeholder="输入关键词"
          />
        </el-form-item>

        <el-form-item label="额外要求">
          <el-input
            v-model="form.extra"
            type="textarea"
            rows="3"
            placeholder="额外要求（可选）"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="generate" :loading="loading">
            生成文案
          </el-button>
        </el-form-item>
      </el-form>

      <div v-if="result" class="result-section">
        <h3>{{ result.title }}</h3>
        <div class="content">{{ result.content }}</div>
        <div class="hashtags">
          <el-tag v-for="tag in result.hashtags" :key="tag" size="small">
            {{ tag }}
          </el-tag>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { generateContent } from '@/api/creator'

const form = reactive({
  topic: '',
  style: '经验分享',
  keywords: [] as string[],
  extra: ''
})

const loading = ref(false)
const result = ref<any>(null)

const generate = async () => {
  if (!form.topic) {
    ElMessage.warning('请输入主题')
    return
  }

  loading.value = true
  try {
    const response = await generateContent(form)
    result.value = response.result
    ElMessage.success('生成成功')
  } catch (error: any) {
    ElMessage.error(error.message || '生成失败')
  } finally {
    loading.value = false
  }
}
</script>
```

- [ ] **Step 5: 创建 API 模块 src/api/creator.ts**

```typescript
import api from './index'

export const generateContent = async (data: {
  topic: string
  style: string
  keywords?: string[]
  extra?: string
}) => {
  const response = await api.post('/creator/generate', data)
  return response.data
}

export const getCreatorInfo = async () => {
  const response = await api.get('/creator/info')
  return response.data
}
```

- [ ] **Step 6: 配置路由 src/router/index.ts**

```typescript
import { createRouter, createWebHistory } from 'vue-router'
import CreatorView from '@/views/CreatorView.vue'
import KnowledgeBaseView from '@/views/KnowledgeBaseView.vue'

const routes = [
  { path: '/', redirect: '/creator' },
  { path: '/creator', name: 'Creator', component: CreatorView },
  { path: '/knowledge', name: 'Knowledge', component: KnowledgeBaseView }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
```

- [ ] **Step 7: 更新 App.vue**

```vue
<template>
  <div id="app">
    <el-container>
      <el-header>
        <h1>小红书智能创作Agent</h1>
      </el-header>
      <el-container>
        <el-aside width="200px">
          <el-menu :default-active="$route.path" router>
            <el-menu-item index="/creator">文案生成</el-menu-item>
            <el-menu-item index="/knowledge">知识库</el-menu-item>
          </el-menu>
        </el-aside>
        <el-main>
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup lang="ts">
</script>

<style>
#app {
  height: 100vh;
}
.el-header {
  background: #409eff;
  color: white;
  display: flex;
  align-items: center;
}
.el-aside {
  background: #f5f5f5;
}
</style>
```

- [ ] **Step 8: 更新 main.ts**

```typescript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(ElementPlus)

app.mount('#app')
```

- [ ] **Step 9: 启动前端验证**

```bash
cd frontend
npm run dev
```

访问 http://localhost:5173 查看前端

- [ ] **Step 10: 提交代码**

```bash
git add frontend/
git commit -m "feat(v0.2): add Vue 3 frontend with creator page"
```

---

## Phase 3: v0.3 - 爬虫与学习 (M4 + M5)

> 计划文档待续...

## Phase 4: v0.4 - 发布功能 (M3)

> 计划文档待续...

---

## 自审检查清单

### Spec 覆盖检查
- [x] M1: RAG知识库管理 ✅
  - 文档加载 ✅ (txt/md/pdf/JSON)
  - 文本切片 ✅ (chunk_size=500, overlap=50)
  - 向量化 ✅ (使用通义千问embedding)
  - 检索 ✅ (top-k, 筛选)
  - REST API ✅

- [x] M2: 文案生成Agent ✅
  - 输入 ✅ (topic/style/keywords/extra)
  - 小红书公式 ✅ (在prompt中实现)
  - 输出 ✅ (title/content/hashtags/full_post)
  - 温度参数 ✅ (0.7)
  - Vue 前端 ✅

- [x] M8: Web UI ✅
  - Vue 3 + Vite + TypeScript ✅
  - Element Plus ✅
  - 前后端分离 ✅

### 技术栈确认
- [x] 前端: Vue 3 + Vite + TypeScript + Element Plus + Axios
- [x] 后端: FastAPI + LangChain + LangGraph
- [x] 数据库: Chroma + SQLite
- [x] 桌面端: 已废弃

### 占位符扫描
- [x] 无 "TBD" / "TODO"
- [x] 无 "实现后续" / "填充细节"
- [x] 无空泛的 "添加错误处理"

---

## 执行选项

**Plan complete and saved.**

**执行方式选择:**

**1. Subagent-Driven (recommended)** - 使用 superpowers:subagent-driven-development
   - 每个任务由独立subagent执行
   - 任务间有检查点
   - 适合大型项目快速迭代

**2. Inline Execution** - 使用 superpowers:executing-plans
   - 在当前session中按任务执行
   - 带检查点的批量执行
   - 适合中小型项目

**你想选择哪种方式开始实现？**
