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

    class Config:
        json_schema_extra = {
            "example": {
                "id": "kn_1714392000.789",
                "source": "https://www.xiaohongshu.com/explore/xxx",
                "learned_at": "2026-04-29T10:30:00",
                "post_type": "产品测评",
                "hook_analysis": "开头用了'被问了100遍'制造稀缺感",
                "content_structure": "痛点引入 → 产品介绍 → 使用前后对比 → 价格锚点 → 引导购买",
                "key_phrases": ["无限回购", "亲测有效", "黄黑皮救星"],
                "hashtags": ["#我的护肤日常", "#平价好物"],
                "emotional_triggers": ["焦虑（皮肤问题）", "获得感（效果对比）"],
                "rewrite_template": "【开头】描述常见困扰...",
                "estimated_quality_score": 92
            }
        }
