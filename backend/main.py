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
from backend.utils.logger import setup_logging, get_logger

# 初始化日志系统
setup_logging(log_dir="logs", app_name="student-manager", log_level="INFO")
logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    - 启动时: 自动创建数据库表，检查外部服务状态
    - 关闭时: 清理数据库连接池
    """
    # 启动: 确保所有实体表已创建 (不存在则创建)
    Base.metadata.create_all(bind=engine)

    # 尝试连接Milvus（非关键路径，失败不影响系统启动）
    milvus_ready = False
    try:
        from backend.utils.milvus_util import connect_milvus, get_all_collections
        connect_milvus()
        # 检查向量库数据状态
        stats = get_all_collections()
        ready_count = sum(1 for s in stats.values() if s.get("exists") and s.get("num_entities", 0) > 0)
        if ready_count == 0:
            logger.warning(
                "Milvus 向量库中没有数据。请运行以下命令导入四大名著文本：\n"
                "  python scripts/init_milvus.py   （创建集合）\n"
                "  python scripts/ingest_novel.py   （导入全文数据）"
            )
        else:
            logger.info("Milvus 向量库就绪: %s/4 个集合有数据", ready_count)
        milvus_ready = True
    except Exception as e:
        logger.warning("Milvus 连接失败: %s", e)

    # 检查Neo4j状态
    try:
        from backend.utils.neo4j_util import neo4j_client
        if neo4j_client.is_connected():
            # 检查是否有数据
            stats = neo4j_client.execute_query("MATCH (p:Person) RETURN count(p) as cnt")
            person_count = stats[0]["cnt"] if stats else 0
            if person_count == 0:
                logger.warning(
                    "Neo4j 已连接但没有人物数据。请运行: python scripts/init_neo4j.py"
                )
            else:
                logger.info("Neo4j 图谱就绪: %s 个人物节点", person_count)
        else:
            logger.warning("Neo4j 未连接，图谱功能不可用")
    except Exception as e:
        logger.warning("Neo4j 状态检查失败: %s", e)

    logger.info("%s v%s 已启动", settings.APP_NAME, settings.APP_VERSION)
    yield
    # 关闭: 回收数据库引擎连接池
    engine.dispose()
    logger.info("%s 已停止", settings.APP_NAME)


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
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
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

# 学生管理
from backend.controller.student_controller import router as student_router
app.include_router(student_router, prefix="/api/v1/students", tags=["学生管理"])

# 班级管理
from backend.controller.class_controller import router as class_router
app.include_router(class_router, prefix="/api/v1/classes", tags=["班级管理"])

# 成绩管理
from backend.controller.score_controller import router as score_router
app.include_router(score_router, prefix="/api/v1/scores", tags=["成绩管理"])

# 就业管理
from backend.controller.employment_controller import router as employment_router
app.include_router(employment_router, prefix="/api/v1/employment", tags=["就业管理"])

# 课程管理
from backend.controller.course_controller import router as course_router
app.include_router(course_router, prefix="/api/v1/courses", tags=["课程管理"])

# 操作日志
from backend.controller.log_controller import router as log_router
app.include_router(log_router, prefix="/api/v1/logs", tags=["操作日志"])

# 仪表盘
from backend.controller.dashboard_controller import router as dashboard_router
app.include_router(dashboard_router, prefix="/api/v1/dashboard", tags=["仪表盘"])

# 用户管理
from backend.controller.user_controller import router as user_router
app.include_router(user_router, prefix="/api/v1/users", tags=["用户管理"])

# RAG知识问答
from backend.controller.rag_controller import router as rag_router
app.include_router(rag_router, prefix="/api/v1/rag", tags=["四大名著RAG问答"])

# 八戒功能（灯谜/诗词/社交/情绪）
from backend.controller.bajie_controller import router as bajie_router
app.include_router(bajie_router, prefix="/api/v1/bajie", tags=["八戒功能"])

# 多智能体编排
from backend.controller.agent_controller import router as agent_router
app.include_router(agent_router, prefix="/api/v1/agent", tags=["多智能体"])

# 天气查询
from backend.controller.weather_controller import router as weather_router
app.include_router(weather_router, prefix="/api/v1/weather", tags=["天气查询"])

# 运势占卜
from backend.controller.fortune_controller import router as fortune_router
app.include_router(fortune_router, prefix="/api/v1/fortune", tags=["运势占卜"])

# 人物关系图谱
from backend.controller.graph_controller import router as graph_router
app.include_router(graph_router, prefix="/api/v1/graph", tags=["人物关系图谱"])

# 智能问数（NL2SQL）
from backend.controller.smart_query_controller import router as smart_query_router
app.include_router(smart_query_router, prefix="/api/v1/smart-query", tags=["智能问数"])

# 记忆管理
from backend.controller.memory_controller import router as memory_router
app.include_router(memory_router, prefix="/api/v1/memory", tags=["记忆管理"])

# 主动对话（SSE）
from backend.controller.proactive_controller import router as proactive_router
app.include_router(proactive_router, prefix="/api/v1/memory", tags=["主动对话"])

# 语音交互
from backend.controller.audio_controller import router as audio_router
app.include_router(audio_router, prefix="/api/v1/audio")

# 导出 app 供 uvicorn 使用
# 启动命令: uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8008, reload=True)