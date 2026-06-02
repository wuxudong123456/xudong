"""
应用配置管理模块
从 .env 文件和环境变量中读取配置
"""
import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """应用全局配置"""
    # 数据库配置
    DB_USER: str = Field(default="root", alias="DB_USER")
    DB_PASSWORD: str = Field(default="123456", alias="DB_PASSWORD")
    DB_HOST: str = Field(default="localhost", alias="DB_HOST")
    DB_PORT: str = Field(default="3306", alias="DB_PORT")
    DB_NAME: str = Field(default="student-mananger", alias="DB_NAME")

    # DeepSeek API 配置
    DEEPSEEK_API_KEY: str = Field(default="", alias="DEEPSEEK_API_KEY")
    DEEPSEEK_BASE_URL: str = Field(default="https://api.deepseek.com/v1", alias="DEEPSEEK_BASE_URL")
    DEEPSEEK_MODEL: str = Field(default="deepseek-chat", alias="DEEPSEEK_MODEL")
    DEEPSEEK_EMBEDDING_MODEL: str = Field(default="text-embedding-3-small", alias="DEEPSEEK_EMBEDDING_MODEL")

    # 阿里云DashScope配置
    ALIYUN_API_KEY: str = Field(default="", alias="ALIYUN_API_KEY")
    ALIYUN_BASE_URL: str = Field(default="https://dashscope.aliyuncs.com/api/v1", alias="ALIYUN_BASE_URL")
    ALIYUN_CHAT_MODEL: str = Field(default="qwen-turbo", alias="ALIYUN_CHAT_MODEL")
    ALIYUN_EMBEDDING_MODEL: str = Field(default="text-embedding-v3", alias="ALIYUN_EMBEDDING_MODEL")
    ALIYUN_TTS_MODEL: str = Field(default="sambert-zhichu", alias="ALIYUN_TTS_MODEL")
    ALIYUN_ASR_MODEL: str = Field(default="qwen-audio-asr", alias="ALIYUN_ASR_MODEL")

    # 天气API配置 (和风天气)
    WEATHER_API_KEY: str = Field(default="", alias="WEATHER_API_KEY")

    # Milvus 向量数据库配置
    MILVUS_HOST: str = Field(default="127.0.0.1", alias="MILVUS_HOST")
    MILVUS_PORT: str = Field(default="19530", alias="MILVUS_PORT")
    MILVUS_COLLECTION_NAME: str = Field(default="journey_to_the_west", alias="MILVUS_COLLECTION_NAME")

    # Neo4j 图数据库配置
    NEO4J_URI: str = Field(default="bolt://localhost:7687", alias="NEO4J_URI")
    NEO4J_USER: str = Field(default="neo4j", alias="NEO4J_USER")
    NEO4J_PASSWORD: str = Field(default="password", alias="NEO4J_PASSWORD")

    # JWT 认证配置
    JWT_SECRET_KEY: str = Field(default="student-manager-secret", alias="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = Field(default="HS256", alias="JWT_ALGORITHM")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=120, alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, alias="JWT_REFRESH_TOKEN_EXPIRE_DAYS")

    # 应用配置
    APP_NAME: str = Field(default="学生管理系统", alias="APP_NAME")
    APP_VERSION: str = Field(default="1.0.0", alias="APP_VERSION")
    APP_DEBUG: bool = Field(default=True, alias="APP_DEBUG")

    # 文件上传配置
    UPLOAD_DIR: str = Field(default="./uploads", alias="UPLOAD_DIR")
    MAX_UPLOAD_SIZE_MB: int = Field(default=10, alias="MAX_UPLOAD_SIZE_MB")

    # HuggingFace 镜像
    HF_ENDPOINT: str = Field(default="", alias="HF_ENDPOINT")

    # CORS 配置
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"],
        alias="CORS_ORIGINS"
    )

    @property
    def SQL_URL(self) -> str:
        """构建MySQL连接URL"""
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"

    class Config:
        # 使用 config.py 所在目录的父目录（项目根目录）作为 .env 的查找基准
        env_file = str(Path(__file__).resolve().parent.parent / ".env")
        env_file_encoding = "utf-8"
        case_sensitive = False


# 全局单例配置对象
settings = Settings()
