from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

class ClassCreate(BaseModel):
    class_name: str
    start_time: Optional[date] = None
    head_teacher_id: Optional[int] = None
    lecturer_id: Optional[int] = None

class ClassUpdate(BaseModel):
    class_name: Optional[str] = None
    start_time: Optional[date] = None
    head_teacher_id: Optional[int] = None
    lecturer_id: Optional[int] = None

class ClassResp(ClassCreate):
    class_id: int
    is_deleted:int
    create_time: datetime
    update_time: datetime


    #数据库对象 → 自动转成 JSON
    class Config:
        orm_mode = True