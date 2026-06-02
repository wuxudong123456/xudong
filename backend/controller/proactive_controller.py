"""
主动对话 SSE 控制器
每15秒检查一次，有消息就推送给前端
"""
import asyncio
import json
import logging
from typing import Optional
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from backend.dependencies import get_db, get_current_user
from backend.entity.user import User
from backend.service.proactive_service import ProactiveService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/proactive-stream", summary="主动对话SSE流")
async def proactive_stream(
    character: Optional[str] = Query("bajie"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    每15秒检查是否有主动搭话，有则推送SSE事件
    event: proactive
    data: {"type": "见面问候", "content": "..."}
    """

    async def event_generator():
        user_id = current_user.id
        try:
            while True:
                await asyncio.sleep(15)
                try:
                    result = ProactiveService.check_and_generate(
                        user_id, db, character)
                    if result:
                        data = json.dumps(result, ensure_ascii=False)
                        yield f"event: proactive\ndata: {data}\n\n"
                except Exception as e:
                    logger.error("Proactive check error: %s", e)
        except asyncio.CancelledError:
            logger.info("Proactive stream cancelled for user %s", user_id)
        except Exception as e:
            logger.error("Proactive stream error: %s", e)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
