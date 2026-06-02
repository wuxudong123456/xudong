"""班级管理 Schema"""
from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, Field


class ClassBase(BaseModel):
    class_name: str = Field(..., max_length=50, description="班级名称")
    start_time: Optional[date] = Field(None, description="开课时间")
    close_time: Optional[date] = Field(None, description="闭班时间")
    head_teacher_id: Optional[int] = Field(None, description="班主任ID")
    lecturer_id: Optional[int] = Field(None, description="授课老师ID")


class ClassCreate(ClassBase): pass


class ClassUpdate(BaseModel):
    class_name: Optional[str] = Field(None, max_length=50)
    start_time: Optional[date] = None
    close_time: Optional[date] = None
    head_teacher_id: Optional[int] = None
    lecturer_id: Optional[int] = None


class ClassResponse(ClassBase):
    class_id: int
    student_count: Optional[int] = Field(default=0, description="学生人数")
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None

    class Config:
        from_attributes = True
