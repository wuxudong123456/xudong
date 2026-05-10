from pydantic import BaseModel, Field
from typing import Optional

# 请求体模型
# 添加成绩时的请求参数
class Score_QQ(BaseModel):
    student_no: str = Field(..., min_length=3, max_length=20)  # 学号
    exam_order: int = Field(..., ge=1)                         # 考试序号
    score: Optional[float] = Field(None, ge=0, le=100)         # 分数 Optional：可以不传 / 可以为 None 意思：成绩可填、也可以不填

# 修改成绩时的请求参数
class ScoreUpdate(BaseModel):
    score: Optional[float] = Field(None, ge=0, le=100)         # 要修改的分数


# 基础数据结构
# 单条成绩详情（返回给前端）
class ScoreResponseItem(BaseModel):
    id: int                 # 成绩ID
    student_no: str         # 学号
    exam_order: int         # 考试序号
    score: Optional[float]  # 分数

    class Config:
        from_attributes = True  # Pydantic会自动把ORM对象转成定义的模型

# 所有科目80分以上的学生信息
class StudentAbove80(BaseModel):
    student_no: str         # 学号
    student_name: str       # 姓名
    score: float | None     # 最低分

    class Config:
        from_attributes = True

# 单条不及格记录
class FailScoreItem(BaseModel):
    exam_order: int  # 考试序号
    score: float     # 分数

    class Config:
        from_attributes = True

# 多次不及格的学生信息
class StudentFail(BaseModel):
    student_no: str               # 学号
    student_name: str             # 姓名
    fail_records: list[FailScoreItem]  # 不及格记录列表

    class Config:
        from_attributes = True

# 班级平均分统计信息
class ClassAvgScore(BaseModel):
    class_id: int           # 班级ID
    exam_order: int         # 考试序号
    avg_score: float | None # 平均分

    class Config:
        from_attributes = True

# 统一响应包装模型
# 单条成绩统一响应
class ScoreResponse(BaseModel):
    code: int                # 状态码
    message: str             # 提示信息
    data: ScoreResponseItem  # 成绩数据

    class Config:
        from_attributes = True

# 成绩分页查询响应
class Score_Page_Response(BaseModel):
    code: int                     # 状态码
    message: str                  # 提示信息
    data: list[ScoreResponseItem] # 成绩列表
    total: int                    # 总条数
    page: int                     # 当前页码
    size: int                     # 每页条数

    class Config:
        from_attributes = True

# 80分以上学生统一响应
class StudentAbove80Response(BaseModel):
    code: int                      # 状态码
    message: str                   # 提示信息
    data: list[StudentAbove80]     # 学生列表

    class Config:
        from_attributes = True

# 多次不及格学生统一响应
class StudentFailResponse(BaseModel):
    code: int                   # 状态码
    message: str                # 提示信息
    data: list[StudentFail]     # 学生列表

    class Config:
        from_attributes = True

# 班级平均分统计统一响应
class ClassAvgScoreResponse(BaseModel):
    code: int                    # 状态码
    message: str                 # 提示信息
    data: list[ClassAvgScore]    # 统计数据

    class Config:
        from_attributes = True