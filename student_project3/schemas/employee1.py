import re

from pydantic import BaseModel, Field,field_validator
from typing import Optional
from datetime import date


class CreateEmployment(BaseModel):
    student_no: str = Field(pattern=r"^XS\d{7}$",description="学号")
    student_name: Optional[str] = Field(None)
    class_id: Optional[int] = Field(None)
    job_open_time: Optional[date] = Field(None,description="就业开始时间")
    offer_send_time: Optional[date] = Field(None,description="offer下发时间")
    company_name: Optional[str] = Field(None,description="公司名称")
    salary: Optional[int] = Field(None,description="薪资")

    @field_validator('student_no')
    def check_student_no(cls, value):
        if not re.match(r"^XS\d{7}$", value):
            raise ValueError("学号必须是 XS + 7 位数字，如 XS2400001")
        return value


class UpdateEmployment(BaseModel):
    student_name: Optional[str] = Field(None, description="学生姓名")
    class_id: Optional[int] = Field(None, description="班级id")
    job_open_time: Optional[date] = Field(None, description="就业开始时间")
    offer_send_time: Optional[date] = Field(None, description="offer下发时间")
    company_name: Optional[str] = Field(None, description="公司名称")
    salary: Optional[int] = Field(None, description="薪资")


class EmploymentResponse(BaseModel):
    employment_id: int
    student_no: str
    student_name: Optional[str]
    class_id: Optional[int]
    job_open_time: Optional[date] = None
    offer_send_time: Optional[date] = None
    company_name: Optional[str] = None
    salary: Optional[int] = None

    #数据库 ORM 对象实现自动序列化返回前端
    class Config:
        from_attributes = True