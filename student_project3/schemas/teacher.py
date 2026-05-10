from pydantic import BaseModel,Field
from typing import Optional, List
from datetime import datetime,date
from enum import Enum
#性别枚举
class GenderEnum(str, Enum):
    男 = "男"
    女 = "女"
#新增的请求体
class TeacherCreate(BaseModel):
    teacher_name: str=Field(...,max_length=10,min_length=2)
    gender: Optional[GenderEnum] = None  #请求体嵌套
    phone: Optional[str] = None

#修改的请求体
class TeacherUpdate(BaseModel):
    teacher_name: Optional[str] = None
    gender: Optional[str] = None
    phone: Optional[str] = None

#返回信息的响应体
class TeacherResponse(BaseModel):
    teacher_id: int
    teacher_name: str
    gender: Optional[str] = None
    phone: Optional[str] = None


    class Config:
        from_attributes = True  #从数据库模型读取数据转变类型返回前端
#条件查询的响应体
class TeacherListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    data: List[TeacherResponse]


#统计信息的响应模型
class TeacherStatsResponse(BaseModel):
    total: int
    male_count: int
    female_count: int







