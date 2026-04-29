"""FastAPI 主入口"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import CORS_ORIGINS
from app.api.knowledge import router as knowledge_router
from app.api.creator import router as creator_router

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
app.include_router(knowledge_router, prefix="/api/knowledge", tags=["knowledge"])
app.include_router(creator_router, prefix="/api/creator", tags=["creator"])


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "version": "0.1.0"}


@app.get("/")
async def root():
    """根路径"""
    return {"message": "RedBook Agent API", "docs": "/docs"}
