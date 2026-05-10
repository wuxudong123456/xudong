from sqlalchemy.orm import Session
from sqlalchemy import func
from models.employee1 import Employment
from schemas.employee1 import CreateEmployment, UpdateEmployment

# DAO层：只做数据库增删改查，不写业务逻辑
# 全部使用 @staticmethod 静态方法，
# 可以直接通过类名加方法统一调用，降低耦合度
class EmploymentDao:
    # 查询所有就业记录
    @staticmethod
    def get_all(
            db:Session,
            skip: int = 0,
            limit: int = 10,
            student_name: str = None,
            company_name:str = None,
            class_id: int = None
                ):
        # 通过软删除标记为0的，学生姓名模糊查询以及班级id，分页查询所有就业记录
        query = db.query(Employment).filter(Employment.is_deleted == 0)
        if student_name:
            query = query.filter(Employment.student_name.like(f"%{student_name}%"))
        if company_name:
            query = query.filter(Employment.company_name.like(f"%{company_name}%"))
        if class_id is not None:  # 这里修复：防止 class_id=0 失效
            query = query.filter(Employment.class_id == class_id)
        total = query.count()  # 总条数
        items = query.offset(skip * limit).limit(limit).all()  # 正确分页公式
        return total,items

    @staticmethod
    def get_by_salary_range(db: Session, salary_min: int, salary_max: int):
        return db.query(Employment).filter(
            Employment.salary.between(salary_min, salary_max),
            Employment.is_deleted == 0
        ).all()

    #就业模块统计分析
    @staticmethod
    #薪资top5
    def get_salary_top5(db:Session):
        return db.query(Employment).filter(
            Employment.is_deleted == 0,
            Employment.salary.isnot(None)
        ).order_by(Employment.salary.desc()).limit(5).all()

    @staticmethod
    #班级平均薪资
    def get_class_avg(db:Session):
        return db.query(Employment.class_id,
                        func.avg(Employment.salary).label("avg_salary")
                        ).filter(
            Employment.is_deleted == 0,
            Employment.salary.isnot(None)
        ).group_by(Employment.class_id).all()

    #通过学号查询就业记录
    @staticmethod
    def get_student_no_by(db:Session,student_no:str):
        return db.query(Employment).filter(Employment.student_no == student_no,
                                           Employment.is_deleted == 0).first()  #只查未删除的

    #通过就业id查询单条就业记录
    @staticmethod
    def get_employment_id_by(db:Session,employment_id:int):
        return db.query(Employment).filter(Employment.employment_id == employment_id,
                                           Employment.is_deleted == 0).first()  #只查未删除的

    #新增就业数据
    @staticmethod
    def create_employment(db:Session,data:CreateEmployment):
        # 把请求体数据转为数据库模型对象
        emp = Employment(**data.dict())
        #添加到数据库
        db.add(emp)
        #提交事务
        db.commit()
        #刷新数据库新增的就业记录
        db.refresh(emp)
        return emp

    #修改前端传过来的就业数据
    @staticmethod
    # exclude_unset=True：只更新前端传了的字段,前端传什么就改什么
    def update_employment(db:Session,employment_id:int,data:UpdateEmployment):
        db.query(Employment).filter(Employment.employment_id == employment_id,
                                    Employment.is_deleted == 0).update(data.dict(exclude_unset=True))
        db.commit()

    #逻辑删除就业记录
    @staticmethod
    def delete_employment(db:Session,employment_id:int):
        db.query(Employment).filter(
            Employment.employment_id == employment_id
        ).update({"is_deleted":1})  #只改标记，不删数据
        db.commit()
        return employment_id

    #恢复逻辑删除的数据
    @staticmethod
    def restore_employment(db:Session,employment_id:int):
        #查询数据(包括已删除)
        emp = db.query(Employment).filter(Employment.employment_id == employment_id).first()
        if not emp:
            return None
        #对已删除数据is_deleted为1的数据恢复为0
        emp.is_deleted = 0
        db.commit()
        db.refresh(emp)
        return emp




