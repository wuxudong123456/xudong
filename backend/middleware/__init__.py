"""
全局异常处理中间件
捕获所有未处理的异常并返回统一格式的错误响应
"""
import traceback
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


async def global_exception_handler(request: Request, exc: Exception):
    """
    全局异常处理器
    处理所有未被下层capture的异常，返回统一错误格式
    """
    # 打印异常堆栈供排查
    traceback.print_exc()

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": 500,
            "message": f"服务器内部错误: {str(exc)}",
            "data": None,
        },
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """HTTP异常处理器 (401/403/404等)"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": exc.detail,
            "data": None,
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    参数校验异常处理器
    将Pydantic校验错误翻译为中文提示
    """
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        msg = error["msg"]
        errors.append(f"字段'{field}'校验失败: {msg}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": 422,
            "message": "参数校验失败",
            "data": errors,
        },
    )
