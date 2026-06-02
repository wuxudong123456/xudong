"""
学生数据访问层
封装学生相关的数据库查询操作
"""
from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from backend.entity.student import Student
from backend.entity.class_info import ClassInfo


class StudentDAO:
    """学生数据访问对象"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, student_id: int) -> Optional[Student]:
        """根据主键ID查询学生"""
        return (
            self.db.query(Student)
            .filter(Student.id == student_id, Student.is_deleted == 0)
            .first()
        )

    def get_by_student_no(self, student_no: str, exclude_id: Optional[int] = None) -> Optional[Student]:
        """根据学号查询学生"""
        query = self.db.query(Student).filter(
            Student.student_no == student_no,
            Student.is_deleted == 0,
        )
        if exclude_id:
            query = query.filter(Student.id != exclude_id)
        return query.first()

    def get_page(
        self, page: int = 1, size: int = 20,
        keyword: Optional[str] = None,
        class_id: Optional[int] = None,
        education: Optional[str] = None,
        gender: Optional[str] = None,
    ) -> Tuple[int, List[Dict[str, Any]]]:
        """
        分页查询学生列表(联查班级名称)
        :return: (总记录数, [学生字典+class_name])
        """
        # 基础查询: JOIN class_info 获取班级名称
        query = (
            self.db.query(Student, ClassInfo.class_name)
            .outerjoin(ClassInfo, Student.class_id == ClassInfo.class_id)
            .filter(Student.is_deleted == 0)
        )
        # 关键词搜索: 学号/姓名模糊匹配
        if keyword:
            query = query.filter(
                or_(
                    Student.student_name.like(f"%{keyword}%"),
                    Student.student_no.like(f"%{keyword}%"),
                )
            )
        # 班级筛选
        if class_id:
            query = query.filter(Student.class_id == class_id)
        # 学历筛选
        if education:
            query = query.filter(Student.education == education)
        # 性别筛选
        if gender:
            query = query.filter(Student.gender == gender)

        total = query.count()
        rows = (
            query.order_by(Student.id.desc())
            .offset((page - 1) * size)
            .limit(size)
            .all()
        )
        # 组装返回数据
        items = []
        for student, class_name in rows:
            item = {
                "id": student.id,
                "student_no": student.student_no,
                "class_id": student.class_id,
                "student_name": student.student_name,
                "gender": student.gender,
                "age": student.age,
                "native_place": student.native_place,
                "graduate_school": student.graduate_school,
                "major": student.major,
                "education": student.education,
                "admission_time": student.admission_time,
                "graduate_time": student.graduate_time,
                "advisor_id": student.advisor_id,
                "job_open_time": student.job_open_time,
                "create_time": student.create_time,
                "update_time": student.update_time,
                "class_name": class_name,
            }
            items.append(item)
        return total, items

    def get_all(self, filters: Optional[Dict] = None) -> List[Student]:
        """获取全部学生(用于导出)"""
        query = self.db.query(Student).filter(Student.is_deleted == 0)
        if filters:
            if filters.get("class_id"):
                query = query.filter(Student.class_id == filters["class_id"])
        return query.all()

    def create(self, data: dict) -> Student:
        """新增学生"""
        student = Student(**data)
        self.db.add(student)
        self.db.commit()
        self.db.refresh(student)
        return student

    def batch_create(self, data_list: List[dict]) -> List[Student]:
        """批量新增学生"""
        students = [Student(**data) for data in data_list]
        self.db.add_all(students)
        self.db.commit()
        return students

    def update(self, student_id: int, data: dict) -> Optional[Student]:
        """更新学生信息"""
        student = self.get_by_id(student_id)
        if not student:
            return None
        for field, value in data.items():
            if value is not None:
                setattr(student, field, value)
        self.db.commit()
        self.db.refresh(student)
        return student

    def soft_delete(self, student_id: int) -> bool:
        """软删除学生"""
        student = self.get_by_id(student_id)
        if not student:
            return False
        student.is_deleted = 1
        self.db.commit()
        return True

    def batch_soft_delete(self, ids: List[int]) -> int:
        """批量软删除，返回删除数量"""
        count = (
            self.db.query(Student)
            .filter(Student.id.in_(ids), Student.is_deleted == 0)
            .update({"is_deleted": 1}, synchronize_session=False)
        )
        self.db.commit()
        return count
