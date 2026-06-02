"""成绩管理 Schema"""
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field


class ScoreBase(BaseModel):
    student_no: str = Field(..., max_length=50, description="学生编号")
    exam_order: int = Field(..., description="考核序次")
    score: Decimal = Field(..., max_digits=5, decimal_places=2, description="成绩")


class ScoreCreate(ScoreBase): pass


class ScoreUpdate(BaseModel):
    student_no: Optional[str] = Field(None, max_length=50)
    exam_order: Optional[int] = None
    score: Optional[Decimal] = None


class ScoreBatchItem(BaseModel):
    student_no: str
    exam_order: int
    score: Decimal


class ScoreBatchImport(BaseModel):
    items: List[ScoreBatchItem]


class ScoreFilter(BaseModel):
    student_no: Optional[str] = None
    class_id: Optional[int] = Field(None, description="按班级筛选")
    exam_order: Optional[int] = None
    score_min: Optional[Decimal] = None
    score_max: Optional[Decimal] = None
