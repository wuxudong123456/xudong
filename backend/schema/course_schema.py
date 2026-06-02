"""课程管理 Schema"""
from typing import Optional
from pydantic import BaseModel, Field


class CourseBase(BaseModel):
    course_name: str = Field(..., max_length=100, description="课程名称")
    course_code: str = Field(..., max_length=50, description="课程代码")
    description: Optional[str] = Field(None, description="课程描述")
    teacher_id: Optional[int] = Field(None, description="授课老师ID")
    class_id: Optional[int] = Field(None, description="关联班级ID")
    total_hours: Optional[int] = Field(None, description="总课时")


class CourseCreate(CourseBase): pass


class CourseUpdate(BaseModel):
    course_name: Optional[str] = Field(None, max_length=100)
    course_code: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    teacher_id: Optional[int] = None
    class_id: Optional[int] = None
    total_hours: Optional[int] = None
