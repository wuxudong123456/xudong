"""学生管理系统 - FastAPI 主入口"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from api import student_info, score, employee1, teacher, class_info_api
from dotenv import load_dotenv
import os
import logging

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 从环境变量获取服务配置
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))

# 创建系统
app = FastAPI(
    title="学生管理系统",
    version="2.0",
    description="基于 FastAPI 的学生管理系统，提供学生、成绩、班级、教师、就业等管理功能"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载前端静态文件
frontend_path = os.path.join(os.path.dirname(__file__), "frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

# 导入子路由
app.include_router(student_info.router, tags=["学生管理"])
app.include_router(score.router, tags=["学生成绩"])
app.include_router(employee1.router, tags=["就业模块"])
app.include_router(teacher.router, tags=["老师管理模块"])
app.include_router(class_info_api.class_router, tags=["班级管理"])


# 全局异常处理器
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    处理 HTTP 异常，统一返回格式
    """
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.status_code, "message": exc.detail, "data": None}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    处理未捕获的异常，记录日志并返回友好错误信息
    """
    logger.error(f"Unexpected Exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"code": 500, "message": "服务器内部错误", "data": None}
    )


# 健康检查接口
@app.get("/health", tags=["健康检查"])
async def health_check():
    """
    服务健康检查接口
    """
    return {"code": 200, "message": "服务运行正常", "data": None}


# 根路径
@app.get("/", tags=["首页"])
async def root():
    """
    系统首页
    """
    return {"message": "欢迎来到学生管理系统", "frontend": "/static/index.html", "docs": "/docs"}

# 启动服务，监听指定端口
if __name__ == '__main__':
    import uvicorn
    logger.info(f"Starting server on {HOST}:{PORT}")
    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)