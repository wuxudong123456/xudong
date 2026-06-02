"""
多智能体编排接口控制层
提供统一的智能体聊天入口，SSE流式返回
"""
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List
from backend.dependencies import get_db, get_current_user
from backend.entity.user import User
from backend.service.agent_service import AgentService, classify_intent

router = APIRouter()


class AgentMessage(BaseModel):
    """智能体消息请求"""
    message: str = Field(..., description="用户消息内容")
    history: Optional[List[dict]] = Field(None, description="对话历史 [{\"role\":\"user/assistant\",\"content\":\"...\"}]")
    character: str = Field("bajie", description="角色: bajie/luzhishen/lindaiyu/zhugeliang")
    session_id: Optional[str] = Field(None, description="会话ID（用于记忆持久化）")


class AgentResponse(BaseModel):
    """智能体非流式响应"""
    intent: str = Field(..., description="识别的意图")
    agent: str = Field(..., description="处理的Agent名称")
    reply: str = Field(..., description="回复内容")
    data: Optional[dict] = Field(None, description="附加数据")


@router.post("/chat", summary="多智能体对话（非流式）")
async def agent_chat(
    req: AgentMessage,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """多智能体统一对话入口（自动存档）"""
    from backend.service.memory_service import MemoryService

    service = AgentService(db=db)
    memory = MemoryService(db)

    session_id = req.session_id
    if not session_id:
        session_id = memory.create_session(current_user.id, req.character)

    result = await service.process_message(
        req.message, req.history, req.character, user_id=current_user.id)

    # 自动存档
    reply_text = result.get("reply", "")
    if reply_text and session_id:
        memory.save_exchange(
            current_user.id, session_id,
            req.message, reply_text,
            memory_type="chat", character=req.character,
        )

    return {"code": 200, "message": "success", "data": result}


@router.post("/chat/stream", summary="多智能体对话（SSE流式）")
async def agent_chat_stream(
    req: AgentMessage,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    多智能体流式对话（自动存档）
    """
    from backend.service.memory_service import MemoryService
    import json as _json

    service = AgentService(db=db)
    memory = MemoryService(db)
    full_reply = []

    # 确保有 session_id
    session_id = req.session_id
    if not session_id:
        session_id = memory.create_session(current_user.id, req.character)

    async def event_generator():
        nonlocal full_reply
        try:
            async for event in service.process_message_stream(
                req.message, req.history, req.character, user_id=current_user.id):
                # 收集回复文本用于存档
                if event.startswith("data:") and "[DONE]" not in event:
                    try:
                        data_str = event[5:].strip()
                        data = _json.loads(data_str)
                        if data.get("content"):
                            full_reply.append(data["content"])
                    except Exception:
                        pass
                yield event
        except Exception as e:
            yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"
        finally:
            # 流结束后自动保存 + 记忆提取
            reply_text = "".join(full_reply)
            if reply_text:
                try:
                    memory.save_exchange(
                        current_user.id, session_id,
                        req.message, reply_text,
                        memory_type="chat", character=req.character,
                    )
                except Exception as save_err:
                    import logging
                    logging.getLogger("agent").error("存档失败: %s", save_err)

            if reply_text:
                try:
                    from backend.utils.memory_extractor import MemoryExtractor
                    exchange = [
                        {"role": "user", "content": req.message},
                        {"role": "assistant", "content": reply_text},
                    ]
                    MemoryExtractor.extract_memories(current_user.id, exchange)
                except Exception:
                    pass

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


@router.post("/classify", summary="意图分类（调试用）")
async def classify_message(
    req: AgentMessage,
    current_user: User = Depends(get_current_user),
):
    """单独测试意图分类功能"""
    intent = await classify_intent(req.message)
    return {"code": 200, "message": "success", "data": {"intent": intent}}
