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
