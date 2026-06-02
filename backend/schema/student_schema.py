"""
学生管理 Pydantic Schema
定义请求和响应的数据校验模型
"""
from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, Field


class StudentBase(BaseModel):
    """学生基础字段"""
    student_no: str = Field(..., max_length=50, description="学号")
    class_id: int = Field(..., description="班级ID")
    student_name: str = Field(..., max_length=50, description="学生姓名")
    gender: Optional[str] = Field(None, max_length=10, description="性别")
    age: Optional[int] = Field(None, ge=0, le=100, description="年龄")
    native_place: Optional[str] = Field(None, max_length=100, description="籍贯")
    graduate_school: Optional[str] = Field(None, max_length=100, description="毕业院校")
    major: Optional[str] = Field(None, max_length=100, description="专业")
    education: Optional[str] = Field(None, max_length=50, description="学历")
    admission_time: Optional[date] = Field(None, description="入学时间")
    graduate_time: Optional[date] = Field(None, description="毕业时间")
    advisor_id: Optional[int] = Field(None, description="顾问编号")
    job_open_time: Optional[date] = Field(None, description="就业开放时间")


class StudentCreate(StudentBase):
    """新增学生请求"""
    pass


class StudentUpdate(BaseModel):
    """编辑学生请求，所有字段可选"""
    student_no: Optional[str] = Field(None, max_length=50)
    class_id: Optional[int] = None
    student_name: Optional[str] = Field(None, max_length=50)
    gender: Optional[str] = None
    age: Optional[int] = None
    native_place: Optional[str] = None
    graduate_school: Optional[str] = None
    major: Optional[str] = None
    education: Optional[str] = None
    admission_time: Optional[date] = None
    graduate_time: Optional[date] = None
    advisor_id: Optional[int] = None
    job_open_time: Optional[date] = None


class StudentResponse(StudentBase):
    """学生信息响应"""
    id: int
    is_deleted: int = 0
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None
    class_name: Optional[str] = Field(None, description="班级名称(联查)")

    class Config:
        from_attributes = True


class StudentFilter(BaseModel):
    """学生查询筛选条件"""
    keyword: Optional[str] = Field(None, description="关键词(学号/姓名模糊搜索)")
    class_id: Optional[int] = Field(None, description="班级ID筛选")
    education: Optional[str] = Field(None, description="学历筛选")
    gender: Optional[str] = Field(None, description="性别筛选")


class BatchDeleteRequest(BaseModel):
    """批量删除请求"""
    ids: List[int] = Field(..., description="待删除的学生ID列表")
