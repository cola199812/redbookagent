"""知识库 API 路由"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
from pathlib import Path
import tempfile
import shutil
from app.knowledge_base.knowledge_base_manager import KnowledgeBaseManager

router = APIRouter()
kb_manager = KnowledgeBaseManager()


class SearchRequest(BaseModel):
    query: str
    k: int = 5


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


@router.post("/search")
async def search_knowledge(request: SearchRequest):
    """搜索知识库"""
    try:
        results = kb_manager.search(query=request.query, k=request.k)
        return {"results": results, "total": len(results)}
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
