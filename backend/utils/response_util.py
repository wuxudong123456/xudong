"""
统一API响应格式模块
"""
from typing import Any, Optional, Dict, List
from pydantic import BaseModel


class ApiResponse(BaseModel):
    """统一响应格式"""
    code: int = 200
    message: str = "success"
    data: Any = None

    @staticmethod
    def success(data: Any = None, message: str = "操作成功") -> dict:
        """成功响应"""
        return {"code": 200, "message": message, "data": data}

    @staticmethod
    def error(message: str = "操作失败", code: int = 400, data: Any = None) -> dict:
        """错误响应"""
        return {"code": code, "message": message, "data": data}

    @staticmethod
    def page(
        items: List[Any],
        total: int,
        page: int,
        size: int,
        message: str = "查询成功"
    ) -> dict:
        """分页响应"""
        return {
            "code": 200,
            "message": message,
            "data": {
                "items": items,
                "total": total,
                "page": page,
                "size": size,
                "pages": (total + size - 1) // size if size > 0 else 0,
            }
        }


class PageRequest(BaseModel):
    """分页请求基类"""
    page: int = 1
    size: int = 20
