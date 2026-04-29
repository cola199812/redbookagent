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
