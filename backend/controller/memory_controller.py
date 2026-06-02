"""
记忆管理接口
会话列表、历史加载、会话删除
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from backend.dependencies import get_db, get_current_user
from backend.entity.user import User
from backend.service.memory_service import MemoryService

router = APIRouter()


class CreateSessionRequest(BaseModel):
    character: str = Field("bajie", description="角色: bajie/luzhishen/lindaiyu/zhugeliang")
    memory_type: str = Field("chat", description="类型: chat/query/game")


@router.get("/sessions", summary="获取会话列表")
def list_sessions(
    memory_type: str = Query("chat", description="记忆类型"),
    character: Optional[str] = Query(None, description="按角色筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = MemoryService(db)
    result = service.list_sessions(current_user.id, memory_type, character)
    return {"code": 200, "message": "success", "data": result}


@router.post("/sessions", summary="创建新会话")
def create_session(
    req: CreateSessionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = MemoryService(db)
    session_id = service.create_session(current_user.id, req.character, req.memory_type)
    return {"code": 200, "message": "创建成功", "data": {"session_id": session_id}}


@router.get("/sessions/{session_id}", summary="加载会话历史")
def load_history(
    session_id: str,
    limit: int = Query(50, description="最大消息数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = MemoryService(db)
    messages = service.load_history(session_id, current_user.id, limit)
    return {"code": 200, "message": "success", "data": messages}


@router.delete("/sessions/{session_id}", summary="删除会话")
def delete_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = MemoryService(db)
    ok = service.delete_session(session_id, current_user.id)
    return {"code": 200, "message": "删除成功" if ok else "会话不存在", "data": None}


@router.get("/query-history", summary="获取智能问数历史")
def query_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = MemoryService(db)
    result = service.get_query_history(current_user.id)
    return {"code": 200, "message": "success", "data": result}