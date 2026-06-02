"""
运势占卜接口
"""
from fastapi import APIRouter, Query, Depends
from backend.dependencies import get_current_user
from backend.entity.user import User
from backend.service.fortune_service import FortuneService

router = APIRouter()


@router.get("/today", summary="今日运势")
async def get_today_fortune(
    zodiac: str = Query(None, description="星座，如: 白羊座"),
    current_user: User = Depends(get_current_user),
):
    """生成今日运势"""
    service = FortuneService()

    # 尝试从用户资料获取生日
    birth_date = None
    # TODO: 从user_profile获取

    fortune = await service.generate_fortune(birth_date=birth_date, zodiac=zodiac)
    return {"code": 200, "message": "success", "data": fortune}
