"""
班级管理业务逻辑层
"""
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.entity.class_info import ClassInfo
from backend.entity.student import Student


class ClassService:
    """班级管理服务"""

    def __init__(self, db: Session):
        self.db = db

    def list_classes(self, page: int, size: int, keyword: str = None) -> Dict[str, Any]:
        """分页查询班级列表(含学生人数统计)"""
        query = self.db.query(ClassInfo).filter(ClassInfo.is_deleted == 0)
        if keyword:
            query = query.filter(ClassInfo.class_name.like(f"%{keyword}%"))

        total = query.count()
        rows = query.order_by(ClassInfo.class_id.asc()).offset((page - 1) * size).limit(size).all()

        items = []
        for cls in rows:
            # 统计班级学生人数
            student_count = self.db.query(func.count(Student.id)).filter(
                Student.class_id == cls.class_id,
                Student.is_deleted == 0,
            ).scalar() or 0
            items.append({
                "class_id": cls.class_id,
                "class_name": cls.class_name,
                "start_time": cls.start_time.isoformat() if cls.start_time else None,
                "close_time": cls.close_time.isoformat() if cls.close_time else None,
                "head_teacher_id": cls.head_teacher_id,
                "lecturer_id": cls.lecturer_id,
                "student_count": student_count,
                "create_time": cls.create_time.isoformat() if cls.create_time else None,
            })

        return {"items": items, "total": total, "page": page, "size": size,
                "pages": (total + size - 1) // size if size > 0 else 0}

    def get_class(self, class_id: int) -> dict:
        cls = self.db.query(ClassInfo).filter(
            ClassInfo.class_id == class_id, ClassInfo.is_deleted == 0
        ).first()
        if not cls:
            raise HTTPException(status_code=404, detail="班级不存在")
        student_count = self.db.query(func.count(Student.id)).filter(
            Student.class_id == class_id, Student.is_deleted == 0
        ).scalar() or 0
        return {
            "class_id": cls.class_id, "class_name": cls.class_name,
            "start_time": cls.start_time, "close_time": cls.close_time,
            "head_teacher_id": cls.head_teacher_id, "lecturer_id": cls.lecturer_id,
            "student_count": student_count,
            "create_time": cls.create_time, "update_time": cls.update_time,
        }

    def create_class(self, data: dict) -> dict:
        cls = ClassInfo(**data)
        self.db.add(cls)
        self.db.commit()
        self.db.refresh(cls)
        return {"class_id": cls.class_id}

    def update_class(self, class_id: int, data: dict) -> dict:
        cls = self.db.query(ClassInfo).filter(
            ClassInfo.class_id == class_id, ClassInfo.is_deleted == 0
        ).first()
        if not cls:
            raise HTTPException(status_code=404, detail="班级不存在")
        for k, v in data.items():
            if v is not None:
                setattr(cls, k, v)
        self.db.commit()
        return {"class_id": class_id}

    def delete_class(self, class_id: int):
        cls = self.db.query(ClassInfo).filter(
            ClassInfo.class_id == class_id, ClassInfo.is_deleted == 0
        ).first()
        if not cls:
            raise HTTPException(status_code=404, detail="班级不存在")
        cls.is_deleted = 1
        self.db.commit()

    def get_class_students(self, class_id: int, page: int, size: int) -> dict:
        """查询班级下的学生列表"""
        query = self.db.query(Student).filter(
            Student.class_id == class_id, Student.is_deleted == 0
        )
        total = query.count()
        rows = query.offset((page - 1) * size).limit(size).all()
        items = [{
            "id": s.id, "student_no": s.student_no, "student_name": s.student_name,
            "gender": s.gender, "education": s.education, "age": s.age,
        } for s in rows]
        return {"items": items, "total": total, "page": page, "size": size,
                "pages": (total + size - 1) // size if size > 0 else 0}
