"""
RAG知识问答接口控制层
提供基于四大名著（西游记/三国演义/红楼梦/水浒传）全文的RAG知识问答API
跨集合向量检索，按语义相似度精准匹配
"""
from fastapi import APIRouter, Query, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from backend.dependencies import get_db, get_current_user
from backend.entity.user import User
from backend.service.rag_service import RAGService

router = APIRouter()


@router.get("/qa", summary="四大名著RAG知识问答（非流式）")
async def knowledge_qa(
    question: str = Query(..., description="问题，如：孙悟空大闹天宫是哪一回？曹操在哪一回败走华容道？"),
    top_k: int = Query(5, description="每个名著集合检索的相似文本块数量"),
    mode: str = Query("auto", description="查询模式：auto自动, rag原文, graph图谱, hybrid融合"),
    current_user: User = Depends(get_current_user),
):
    """
    基于四大名著全文的RAG知识问答（增强版）
    支持智能书籍路由、人物关系图谱、融合查询
    """
    service = RAGService()
    result = await service.answer_question_async(question, top_k=top_k, mode=mode)
    return {"code": 200, "message": "查询成功", "data": result}


@router.get("/qa/stream", summary="RAG知识问答（SSE流式）")
async def knowledge_qa_stream(
    question: str = Query(..., description="问题"),
    top_k: int = Query(5, description="检索数量"),
    mode: str = Query("auto", description="查询模式：auto自动, rag原文, graph图谱, hybrid融合"),
    current_user: User = Depends(get_current_user),
):
    """
    流式RAG知识问答，通过Server-Sent Events逐步返回答案
    前端使用 EventSource 或 fetch + ReadableStream 接收
    """
    service = RAGService()

    async def event_generator():
        try:
            async for chunk in service.answer_question_stream(question, top_k=top_k, mode=mode):
                # SSE格式: data: <content>\n\n
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


@router.get("/collection-info", summary="查询向量库状态")
def get_collection_info():
    """获取Milvus向量库的集合状态和文档数量（公开接口）"""
    service = RAGService()
    info = service.get_collection_info()
    return {"code": 200, "message": "查询成功", "data": info}
