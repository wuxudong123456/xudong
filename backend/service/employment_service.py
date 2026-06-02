"""就业管理业务逻辑层"""
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.entity.employment import Employment
from backend.entity.student import Student
from backend.entity.class_info import ClassInfo


class EmploymentService:

    def __init__(self, db: Session):
        self.db = db

    def list_employments(self, page: int, size: int, keyword: str = None,
                         class_id: int = None, student_no: str = None) -> Dict[str, Any]:
        """分页查询就业信息"""
        query = (
            self.db.query(Employment, ClassInfo.class_name)
            .outerjoin(ClassInfo, Employment.class_id == ClassInfo.class_id)
            .filter(Employment.is_deleted == 0)
        )
        if keyword:
            query = query.filter(
                Employment.student_name.like(f"%{keyword}%") |
                Employment.company_name.like(f"%{keyword}%")
            )
        if class_id:
            query = query.filter(Employment.class_id == class_id)
        if student_no:
            query = query.filter(Employment.student_no == student_no)

        total = query.count()
        rows = query.order_by(Employment.employment_id.desc()).offset((page - 1) * size).limit(size).all()
        items = []
        for emp, cls_name in rows:
            items.append({
                "employment_id": emp.employment_id, "student_no": emp.student_no,
                "student_name": emp.student_name, "class_id": emp.class_id,
                "offer_send_time": emp.offer_send_time.isoformat() if emp.offer_send_time else None,
                "company_name": emp.company_name, "offer_job": emp.offer_job,
                "final_choice": emp.final_choice, "salary": emp.salary,
                "class_name": cls_name, "create_time": emp.create_time.isoformat() if emp.create_time else None,
            })
        return {"items": items, "total": total, "page": page, "size": size,
                "pages": (total + size - 1) // size if size > 0 else 0}

    def create(self, data: dict) -> dict:
        student_no = data["student_no"]
        existing = self.db.query(Employment).filter(
            Employment.student_no == student_no, Employment.is_deleted == 0
        ).first()
        if existing:
            raise HTTPException(400, f"学生 {student_no} 已有就业记录")
        # 自动从学生表填充姓名和班级（如果前端未提供）
        if not data.get("student_name") or not data.get("class_id"):
            student = self.db.query(Student).filter(
                Student.student_no == student_no, Student.is_deleted == 0
            ).first()
            if student:
                if not data.get("student_name"):
                    data["student_name"] = student.student_name
                if not data.get("class_id"):
                    data["class_id"] = student.class_id
        emp = Employment(**data)
        self.db.add(emp)
        self.db.commit()
        self.db.refresh(emp)
        return {"employment_id": emp.employment_id}

    def update(self, emp_id: int, data: dict) -> dict:
        emp = self.db.query(Employment).filter(
            Employment.employment_id == emp_id, Employment.is_deleted == 0
        ).first()
        if not emp:
            raise HTTPException(404, "就业记录不存在")
        for k, v in data.items():
            if v is not None: setattr(emp, k, v)
        self.db.commit()
        return {"employment_id": emp_id}

    def delete(self, emp_id: int):
        emp = self.db.query(Employment).filter(
            Employment.employment_id == emp_id, Employment.is_deleted == 0
        ).first()
        if not emp:
            raise HTTPException(404, "就业记录不存在")
        emp.is_deleted = 1
        self.db.commit()

    def get_stats(self) -> Dict[str, Any]:
        """就业统计: 就业率、平均薪资、按班级统计"""
        total_students = self.db.query(func.count(Student.id)).filter(Student.is_deleted == 0).scalar() or 0
        employed = self.db.query(func.count(Employment.employment_id)).filter(
            Employment.is_deleted == 0, Employment.final_choice == 1
        ).scalar() or 0
        avg_salary = self.db.query(func.avg(Employment.salary)).filter(
            Employment.is_deleted == 0, Employment.final_choice == 1
        ).scalar() or 0
        rate = round(employed / total_students * 100, 1) if total_students > 0 else 0

        # 按班级统计
        class_stats = []
        classes = self.db.query(ClassInfo).filter(ClassInfo.is_deleted == 0).all()
        for cls in classes:
            total_in_class = self.db.query(func.count(Student.id)).filter(
                Student.class_id == cls.class_id, Student.is_deleted == 0
            ).scalar() or 0
            cnt = self.db.query(func.count(Employment.employment_id)).filter(
                Employment.class_id == cls.class_id, Employment.is_deleted == 0,
                Employment.final_choice == 1
            ).scalar() or 0
            avg = self.db.query(func.avg(Employment.salary)).filter(
                Employment.class_id == cls.class_id, Employment.is_deleted == 0
            ).scalar() or 0
            rate = round(cnt / total_in_class * 100, 1) if total_in_class > 0 else 0
            class_stats.append({
                "class_name": cls.class_name,
                "total_students": total_in_class,
                "employed_count": cnt,
                "employment_rate": rate,
                "avg_salary": float(avg),
            })

        return {"employment_rate": rate, "avg_salary": float(avg_salary),
                "employed_count": employed, "total_students": total_students,
                "by_class": class_stats}
