from pydantic import BaseModel,Field
from datetime import date
from typing import Optional, List

# 创建学生信息请求体
class StudentCreate(BaseModel):
    student_no: str
    class_id: int
    student_name: str
    native_place: str
    graduate_school: str
    major: str
    admission_time: date
    graduation_time: date
    education: str
    advisor_id: int
    age: int = Field(...,ge=1) #年龄必须大于等于1
    gender: str = Field(...,pattern=r"^(男|女)$") #只能填入男或女

# 更新学生信息的请求体
class StudentUpdate(BaseModel): #全部选填
    student_no: Optional[str] = None
    class_id: Optional[int] = None
    student_name: Optional[str] = None
    native_place: Optional[str] = None
    graduate_school: Optional[str] = None
    major: Optional[str] = None
    admission_time: Optional[date] = None
    graduation_time: Optional[date] = None
    education: Optional[str] = None
    advisor_id: Optional[int] = None
    age: Optional[int] = Field(None,ge=1)
    gender: Optional[str] = Field(None,pattern=r"^(男|女)$")

# 响应体：返回包括student_id的数据
class StudentResponse(StudentCreate): #继承父类所有的字段
    id: int

    class Config:
        from_attributes = True #将读取到的类属性转化可返回的字典/json

#响应体：返回分页
class StudentListResponse(BaseModel):
    total: int #总条数
    data: List[StudentResponse] #学生列表
    page: int #当前页码
    page_size: int #每页条数
