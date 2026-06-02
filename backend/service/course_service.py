"""课程管理业务逻辑层"""
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from backend.entity.course import Course
from backend.entity.teacher import Teacher
from backend.entity.class_info import ClassInfo


class CourseService:

    def __init__(self, db: Session):
        self.db = db

    def list_courses(self, page: int, size: int, keyword: str = None) -> Dict[str, Any]:
        query = (
            self.db.query(Course, Teacher.teacher_name, ClassInfo.class_name)
            .outerjoin(Teacher, Course.teacher_id == Teacher.teacher_id)
            .outerjoin(ClassInfo, Course.class_id == ClassInfo.class_id)
            .filter(Course.is_deleted == 0)
        )
        if keyword:
            query = query.filter(Course.course_name.like(f"%{keyword}%"))

        total = query.count()
        rows = query.order_by(Course.course_id.desc()).offset((page - 1) * size).limit(size).all()
        items = []
        for c, t_name, cls_name in rows:
            items.append({
                "course_id": c.course_id, "course_name": c.course_name,
                "course_code": c.course_code, "description": c.description,
                "teacher_id": c.teacher_id, "teacher_name": t_name,
                "class_id": c.class_id, "class_name": cls_name,
                "total_hours": c.total_hours,
                "create_time": c.create_time.isoformat() if c.create_time else None,
            })
        return {"items": items, "total": total, "page": page, "size": size,
                "pages": (total + size - 1) // size if size > 0 else 0}

    def create(self, data: dict) -> dict:
        existing = self.db.query(Course).filter(
            Course.course_code == data["course_code"], Course.is_deleted == 0
        ).first()
        if existing:
            raise HTTPException(400, f"课程代码 {data['course_code']} 已存在")
        course = Course(**data)
        self.db.add(course)
        self.db.commit()
        self.db.refresh(course)
        return {"course_id": course.course_id}

    def update(self, course_id: int, data: dict) -> dict:
        course = self.db.query(Course).filter(
            Course.course_id == course_id, Course.is_deleted == 0
        ).first()
        if not course:
            raise HTTPException(404, "课程不存在")
        for k, v in data.items():
            if v is not None: setattr(course, k, v)
        self.db.commit()
        return {"course_id": course_id}

    def delete(self, course_id: int):
        course = self.db.query(Course).filter(
            Course.course_id == course_id, Course.is_deleted == 0
        ).first()
        if not course:
            raise HTTPException(404, "课程不存在")
        course.is_deleted = 1
        self.db.commit()
