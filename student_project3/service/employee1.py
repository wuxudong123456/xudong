# 业务逻辑处理层：处理业务，调用dao层
# 全部使用 @staticmethod 静态方法
from fastapi import HTTPException
from dao.employee1 import *
from schemas.employee1 import EmploymentResponse

class EmploymentService:
    """就业服务类，处理就业相关业务逻辑"""

    @staticmethod
    def get_all_service(db: Session, skip: int, limit: int, student_name: str, company_name: str, class_id: int):
        """
        分页查询所有就业记录
        
        :param db: 数据库会话
        :param skip: 分页偏移量
        :param limit: 每页条数
        :param student_name: 学生姓名（模糊查询）
        :param company_name: 公司名称（模糊查询）
        :param class_id: 班级ID
        :return: 就业记录列表
        """
        return EmploymentDao.get_all(db, skip, limit, student_name, company_name, class_id)

    @staticmethod
    def get_by_salary_range_service(db: Session, salary_min: int, salary_max: int):
        """
        按薪资区间查询就业记录
        
        :param db: 数据库会话
        :param salary_min: 最低薪资
        :param salary_max: 最高薪资
        :return: 薪资区间内的就业记录列表
        :raises HTTPException: 当该薪资区间无数据时抛出404错误
        """
        emp_list = EmploymentDao.get_by_salary_range(db, salary_min, salary_max)
        if not emp_list:
            raise HTTPException(404, "该薪资区间暂无就业信息")
        return emp_list

    @staticmethod
    def get_statistics_service(db: Session):
        """
        获取就业统计数据
        
        :param db: 数据库会话
        :return: 包含薪资前五和班级平均薪资的统计数据
        """
        # 薪资前五
        top5 = EmploymentDao.get_salary_top5(db)
        # 班级平均薪资
        class_avg_salary = EmploymentDao.get_class_avg(db)
        # 把获取的class_avg_salary平均薪资遍历并添加到空列表中
        class_result = []
        for item in class_avg_salary:
            class_result.append({
                "class_id": item.class_id,
                "avg_salary": float(item.avg_salary) if item.avg_salary else 0
            })

        return {
            "salary_top5": [EmploymentResponse.model_validate(i).model_dump() for i in top5],
            "class_average_salary": class_result
        }

    @staticmethod
    def get_student_no_service(db: Session, student_no: str):
        """
        通过学号查询就业记录
        
        :param db: 数据库会话
        :param student_no: 学生学号
        :return: 就业记录
        :raises HTTPException: 当学生不存在时抛出404错误
        """
        emp = EmploymentDao.get_student_no_by(db, student_no)
        if not emp:
            raise HTTPException(404, "学生不存在")
        return emp

    @staticmethod
    def get_employment_id_service(db: Session, employment_id: int):
        """
        通过就业ID查询单条就业记录
        
        :param db: 数据库会话
        :param employment_id: 就业记录ID
        :return: 就业记录
        """
        return EmploymentDao.get_employment_id_by(db, employment_id)

    @staticmethod
    def create_employment_service(db: Session, data: CreateEmployment):
        """
        新增就业数据
        
        :param db: 数据库会话
        :param data: 就业数据
        :return: 创建的就业记录
        :raises HTTPException: 当就业信息已存在时抛出409错误
        """
        exist = EmploymentDao.get_student_no_by(db, data.student_no)
        if exist:
            raise HTTPException(409, "就业信息已存在")
        return EmploymentDao.create_employment(db, data)

    @staticmethod
    def update_employment_service(db: Session, employment_id: int, data: UpdateEmployment):
        """
        修改就业数据
        
        :param db: 数据库会话
        :param employment_id: 就业记录ID
        :param data: 更新数据
        :return: 更新后的就业记录
        :raises HTTPException: 当就业记录不存在时抛出404错误
        """
        emp = EmploymentDao.get_employment_id_by(db, employment_id)
        if not emp:
            raise HTTPException(404, "就业记录不存在")
        EmploymentDao.update_employment(db, employment_id, data)
        return EmploymentDao.get_employment_id_by(db, employment_id)

    @staticmethod
    def delete_employment_service(db: Session, employment_id: int):
        """
        逻辑删除就业记录
        
        :param db: 数据库会话
        :param employment_id: 就业记录ID
        :return: 删除结果
        :raises HTTPException: 当就业记录不存在时抛出404错误
        """
        emp = EmploymentDao.get_employment_id_by(db, employment_id)
        if not emp:
            raise HTTPException(404, "就业记录不存在")
        EmploymentDao.delete_employment(db, employment_id)
        return {"code": 200, "message": "删除成功", "data": employment_id}

    @staticmethod
    def restore_employment_service(db: Session, employment_id: int):
        """
        恢复逻辑删除的就业记录
        
        :param db: 数据库会话
        :param employment_id: 就业记录ID
        :return: 恢复后的就业记录
        :raises HTTPException: 当就业记录不存在时抛出404错误
        """
        emp = EmploymentDao.restore_employment(db, employment_id)
        if not emp:
            raise HTTPException(status_code=404, detail="就业信息不存在，无法恢复")
        return emp