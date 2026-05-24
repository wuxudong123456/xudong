"""
FastAPI 主应用入口
负责应用初始化、中间件注册、路由挂载、异常处理注册
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.config import settings
from backend.database import engine
from backend.entity.base import Base
from backend.middleware import (
    global_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    - 启动时: 自动创建数据库表
    - 关闭时: 清理数据库连接池
    """
    # 启动: 确保所有实体表已创建 (不存在则创建)
    Base.metadata.create_all(bind=engine)
    print(f"[启动] {settings.APP_NAME} v{settings.APP_VERSION} 已启动")
    yield
    # 关闭: 回收数据库引擎连接池
    engine.dispose()
    print(f"[关闭] {settings.APP_NAME} 已停止")


# 创建 FastAPI 应用实例
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="学生管理系统 + 猪八戒多智能体 AI 问答",
    lifespan=lifespan,
)

# --- CORS 跨域中间件 ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 全局异常处理器注册 ---
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)


# --- 健康检查接口 ---
@app.get("/api/v1/system/health", tags=["系统"])
def health_check():
    """
    系统健康检查接口
    返回数据库连接状态、应用版本信息
    """
    try:
        # 尝试验证数据库连接
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "code": 200,
        "message": "success",
        "data": {
            "app_name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "database": db_status,
            "milvus_host": settings.MILVUS_HOST,
        },
    }


# ==========================================
# 路由注册
# ==========================================
# 认证模块
from backend.controller.auth_controller import router as auth_router
app.include_router(auth_router, prefix="/api/v1/auth", tags=["认证"])

# 后续阶段逐步挂载以下路由:
# from backend.controller.student_controller import router as student_router
# app.include_router(student_router, prefix="/api/v1/students", tags=["学生管理"])

# 导出 app 供 uvicorn 使用
# 启动命令: uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
