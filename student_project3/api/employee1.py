from fastapi import APIRouter,Depends, Query

from service.employee1 import *
from core.database import get_db
#路由接口
router = APIRouter(prefix="/employment",tags=["就业模块"])

#通过学生姓名模糊查询，就业公司模糊查询，班级id查询所有就业信息接口
@router.get("/", response_model=dict)
def get_all_api(
        skip:int=Query(0,description="分页偏移量"),
        limit:int=Query(10,description="每页条数"),
        student_name:str=Query(None,description="学生姓名"),
        company_name:str=Query(None,description="就业公司"),
        class_id:int=Query(None,description="班级ID"),
        db:Session = Depends(get_db)
):
    #得到所有学生信息的列表
    total, items = EmploymentService.get_all_service(db, skip, limit, student_name,company_name, class_id)
    return {
        "code": 200,
        "message": "查询成功",
        "total": total,
        "data": [EmploymentResponse.model_validate(item).model_dump() for item in items],
        "skip": skip,
        "limit": limit
    }

# 按薪资区间查询就业信息
@router.get("/salary/range", response_model=dict)
def get_emp_by_salary_range(
    salary_min: int = Query(..., description="最低薪资"),
    salary_max: int = Query(..., description="最高薪资"),
    db: Session = Depends(get_db)
):
    emp_list = EmploymentService.get_by_salary_range_service(db, salary_min, salary_max)
    return {
        "code": 200,
        "message": "查询成功",
        "data": [EmploymentResponse.model_validate(item).model_dump() for item in emp_list]
    }

#就业统计接口
@router.get("/statistics",response_model=dict)
def get_employment_statistics(db:Session = Depends(get_db)):
    data = EmploymentService.get_statistics_service(db)
    return {
        "code": 200,
        "message": "统计成功",
        "data":data
    }

#新增就业信息接口
@router.post("/",response_model=dict)    #接口统一包裹成字典格式
def create_employment_api(data:CreateEmployment,db:Session = Depends(get_db)):
    emp = EmploymentService.create_employment_service(db,data)
    return {"code": 200,
            "message": "添加成功",
            "data": EmploymentResponse.model_validate(emp).model_dump()}
            #数据库对象转成前端可识别的字典格式
#通过学号查询单条信息接口
@router.get("/{student_no}",response_model=dict)
def get_student_no_api(student_no:str,db:Session = Depends(get_db)):
    emp = EmploymentService.get_student_no_service(db,student_no)
    return {"code": 200,
            "message": "查询成功",
            "data": EmploymentResponse.model_validate(emp).model_dump()}
    # 数据库对象转成前端可识别的字典格式


#通过就业id查询并修改就业信息
@router.put("/{employment_id}",response_model=dict)
def update_employment_api(employment_id:int,data:UpdateEmployment,db:Session = Depends(get_db)):
    emp = EmploymentService.update_employment_service(db,employment_id,data)
    return {"code": 200,
            "message": "修改成功",
            "data": EmploymentResponse.model_validate(emp).model_dump()}
            # 数据库对象转成前端可识别的字典格式
#通过就业id查询并删除学生就业信息
@router.delete("/{employment_id}",response_model=dict)
def delete_employment_api(employment_id:int,db:Session = Depends(get_db)):
    EmploymentService.delete_employment_service(db,employment_id)
    return {"code": 200,
            "message": "删除成功",
            "data": None}

#恢复删除的就业信息数据
@router.put("/restore/{employment_id}", response_model=dict)
def restore_employment_api(employment_id:int,db:Session = Depends(get_db)):
    EmploymentService.restore_employment_service(db,employment_id)
    return {
        "code": 200,
        "message": "恢复成功",
        "data": None
    }





