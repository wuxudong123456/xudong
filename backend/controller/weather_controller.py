"""
天气查询接口
"""
from fastapi import APIRouter, Query, Depends
from backend.dependencies import get_current_user
from backend.entity.user import User
from backend.service.weather_service import WeatherService

router = APIRouter()


@router.get("/now", summary="查询当前天气")
async def get_weather(
    city: str = Query(..., description="城市名，如: 北京、上海"),
    current_user: User = Depends(get_current_user),
):
    """查询指定城市的当前天气，返回八戒口吻的回复"""
    service = WeatherService()
    reply = await service.get_weather_reply(city)
    return {"code": 200, "message": "success", "data": {"city": city, "reply": reply}}
