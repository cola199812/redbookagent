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


@router.post("/generate")
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

    return result


@router.get("/info")
async def get_agent_info():
    """获取Agent信息"""
    return agent.get_info()
