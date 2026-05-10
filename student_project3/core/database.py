# 异步数据库配置
# 修改说明：从同步模式改为异步模式，使用 AsyncSession 和 create_async_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 从环境变量获取数据库配置
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "123456")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "student")

# 构建异步数据库连接URL（需要加 asyncmy 驱动）
ASYNC_SQL_URL = f"mysql+aiomysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 创建异步数据库引擎
async_engine = create_async_engine(ASYNC_SQL_URL, pool_size=5, echo=False)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False  # 提交后不自动过期，便于读取属性
)

# 得到Base基类
Base = declarative_base()


# 异步数据库会话生成函数（用于 FastAPI 依赖注入）
async def get_db():
    """
    异步数据库会话依赖注入函数

    :yield: AsyncSession 实例
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
