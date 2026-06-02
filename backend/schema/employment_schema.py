"""就业管理 Schema"""
from typing import Optional
from datetime import date
from pydantic import BaseModel, Field


class EmploymentBase(BaseModel):
    student_no: str = Field(..., max_length=50, description="学生编号")
    student_name: Optional[str] = Field(None, max_length=50, description="学生姓名")
    class_id: Optional[int] = Field(None, description="班级ID")
    offer_send_time: Optional[date] = Field(None, validation_alias='employment_date', description="offer下发时间")
    company_name: Optional[str] = Field(None, max_length=100, description="就业公司")
    offer_job: Optional[str] = Field(None, validation_alias='position', max_length=50, description="offer岗位")
    final_choice: Optional[int] = Field(None, description="是否最终选择: 0=否, 1=是")
    salary: Optional[int] = Field(None, description="就业薪资")


class EmploymentCreate(EmploymentBase): pass


class EmploymentUpdate(BaseModel):
    student_no: Optional[str] = Field(None, max_length=50)
    student_name: Optional[str] = Field(None, max_length=50)
    class_id: Optional[int] = None
    offer_send_time: Optional[date] = Field(None, validation_alias='employment_date')
    company_name: Optional[str] = Field(None, max_length=100)
    offer_job: Optional[str] = Field(None, validation_alias='position', max_length=50)
    final_choice: Optional[int] = None
    salary: Optional[int] = None
