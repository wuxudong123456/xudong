"""
应用配置管理模块
从 .env 文件和环境变量中读取配置
"""
import os
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

    # Milvus 向量数据库配置
    MILVUS_HOST: str = Field(default="127.0.0.1", alias="MILVUS_HOST")
    MILVUS_PORT: str = Field(default="19530", alias="MILVUS_PORT")
    MILVUS_COLLECTION_NAME: str = Field(default="journey_to_the_west", alias="MILVUS_COLLECTION_NAME")

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

    # CORS 配置
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"],
        alias="CORS_ORIGINS"
    )

    @property
    def SQL_URL(self) -> str:
        """构建MySQL连接URL，数据库名含连字符需backtick转义"""
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# 全局单例配置对象
settings = Settings()
