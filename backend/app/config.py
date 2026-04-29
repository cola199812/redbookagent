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
