"""
FastAPI FAQ Web 服务
提供 HTTP API 接口进行问答
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path
import json
import sys

# 添加 scripts 目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from faq_server import FAQServer, FAQMatch

app = FastAPI(
    title="FAQ 问答 API",
    description="基于 FAQ 知识库的问答服务",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化 FAQ 服务器
faq_server = FAQServer()


class QueryRequest(BaseModel):
    """查询请求"""
    question: str
    top_k: Optional[int] = 3


class QueryResponse(BaseModel):
    """查询响应"""
    success: bool
    question: str
    matches: List[dict]
    count: int


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "FAQ 问答 API",
        "version": "1.0.0",
        "endpoints": {
            "query": "/api/query",
            "health": "/api/health",
            "stats": "/api/stats"
        }
    }


@app.get("/api/health")
async def health():
    """健康检查"""
    return {
        "status": "healthy",
        "faq_count": len(faq_server.faqs)
    }


@app.get("/api/stats")
async def stats():
    """统计信息"""
    return {
        "faq_count": len(faq_server.faqs),
        "keyword_index_size": len(faq_server.keyword_index),
        "faq_file": str(faq_server.faq_file)
    }


@app.post("/api/query", response_model=QueryResponse)
async def query_faq(request: QueryRequest):
    """
    查询 FAQ
    
    Args:
        request: 查询请求
        
    Returns:
        查询结果
    """
    if not faq_server.faqs:
        raise HTTPException(status_code=404, detail="没有可用的 FAQ 数据")
    
    try:
        matches = faq_server.query(request.question, top_k=request.top_k)
        
        return QueryResponse(
            success=True,
            question=request.question,
            matches=[
                {
                    "question": match.question,
                    "answer": match.answer,
                    "title": match.title,
                    "source_file": match.source_file,
                    "score": match.score
                }
                for match in matches
            ],
            count=len(matches)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("FAQ Web 服务启动")
    print("=" * 60)
    print(f"服务地址: http://localhost:8000")
    print(f"API 文档: http://localhost:8000/docs")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
