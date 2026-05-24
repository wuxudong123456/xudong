"""
数据库连接管理模块
使用 SQLAlchemy 管理 MySQL 连接和会话
"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import DisconnectionError
from backend.config import settings


def _ping_on_checkout(dbapi_connection, connection_record, connection_proxy):
    """每次从连接池取出连接时 ping 检查可用性"""
    try:
        dbapi_connection.ping(reconnect=True)
    except Exception:
        raise DisconnectionError()


# 创建数据库引擎
engine = create_engine(
    settings.SQL_URL,
    pool_size=20,
    max_overflow=40,
    pool_recycle=3600,      # 连接回收时间(秒)
    pool_pre_ping=True,      # 预检连接可用性
    echo=settings.APP_DEBUG, # 开发环境打印SQL
)

# 每次检出连接时做 ping 检查
event.listen(engine, "checkout", _ping_on_checkout)

# 创建会话工厂
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Session:
    """
    获取数据库会话，作为 FastAPI 依赖注入使用。
    请求结束时自动关闭会话。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
