"""Pydantic 请求/响应模型"""
from pydantic import BaseModel, Field


class RetrieveRequest(BaseModel):
    query: str = Field(..., min_length=1, description="检索查询词")
    top_k: int = Field(default=10, ge=1, le=50, description="返回结果数量")


class RetrieveResult(BaseModel):
    id: int
    chapter_num: int
    title: str
    chunk_index: int
    content: str
    score: float


class RetrieveResponse(BaseModel):
    results: list[RetrieveResult]
    total: int


class QARequest(BaseModel):
    question: str = Field(..., min_length=1, description="用户问题")
    top_k: int = Field(default=5, ge=1, le=20, description="检索数量")


class SourceItem(BaseModel):
    type: str
    score: float
    chapter_num: int | None = None
    title: str | None = None
    content: str | None = None
    question: str | None = None
    answer: str | None = None


class QAResponse(BaseModel):
    answer: str
    sources: list[SourceItem]
