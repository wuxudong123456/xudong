from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
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

# 构建数据库连接URL
SQL_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 创建数据库引擎
engine = create_engine(SQL_URL, pool_size=5)

# 得到Base基类，写数据库表类必须继承它
Base = declarative_base()

# 创建会话工厂
Session_local = sessionmaker(bind=engine)

# 数据库会话生成函数
def get_db():
    db = Session_local()
    try:
        yield db  # 生成器函数，专门用于fastapi依赖注入（每次请求产生一个会话，用完自动关闭）
    finally:
        db.close()   # 用完就关