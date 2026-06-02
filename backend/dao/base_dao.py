"""
DAO 泛型基类
提供通用的CRUD操作，支持软删除
所有业务DAO应继承此类
"""
from typing import TypeVar, Generic, Type, List, Optional, Any, Dict
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, func
from backend.entity.base import Base

T = TypeVar("T", bound=Base)


class BaseDAO(Generic[T]):
    """
    泛型数据访问对象基类
    注意：此基类假定实体的主键名为 "id"，不兼容使用非标准主键名的实体
    （如 Course.course_id, ClassInfo.class_id, Employment.employment_id, Teacher.teacher_id）
    :param model: SQLAlchemy模型类
    :param session: 数据库会话
    """

    def __init__(self, model: Type[T], session: Session):
        self.model = model
        self.session = session

    def _pk_attr(self):
        """获取主键属性名，默认 "id"，子类可覆盖"""
        return "id"

    # ==================== 基础CRUD ====================

    def get_by_id(self, id: int) -> Optional[T]:
        """根据ID查询单条记录"""
        pk = getattr(self.model, self._pk_attr())
        return self.session.query(self.model).filter(pk == id).first()

    def get_by_ids(self, ids: List[int]) -> List[T]:
        """根据ID列表批量查询"""
        return self.session.query(self.model).filter(self.model.id.in_(ids)).all()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        order_by: str = "id",
        desc_order: bool = False,
    ) -> List[T]:
        """
        分页查询所有记录
        :param skip: 跳过条数
        :param limit: 返回条数
        :param order_by: 排序字段
        :param desc_order: 是否倒序
        """
        query = self.session.query(self.model)
        order_column = getattr(self.model, order_by, self.model.id)
        if desc_order:
            query = query.order_by(desc(order_column))
        else:
            query = query.order_by(asc(order_column))
        return query.offset(skip).limit(limit).all()

    def count(self) -> int:
        """统计总记录数"""
        return self.session.query(func.count(self.model.id)).scalar()

    # ==================== 条件查询 ====================

    def filter_by(self, **kwargs) -> List[T]:
        """根据字段精确匹配查询"""
        return self.session.query(self.model).filter_by(**kwargs).all()

    def filter_one(self, **kwargs) -> Optional[T]:
        """根据字段精确匹配查询单条"""
        return self.session.query(self.model).filter_by(**kwargs).first()

    def filter_like(self, **kwargs) -> List[T]:
        """
        模糊查询
        :param kwargs: 字段名=搜索值
        """
        query = self.session.query(self.model)
        for key, value in kwargs.items():
            column = getattr(self.model, key, None)
            if column is not None and value:
                query = query.filter(column.like(f"%{value}%"))
        return query.all()

    # ==================== 创建与更新 ====================

    def create(self, obj_in: Dict[str, Any]) -> T:
        """创建记录"""
        db_obj = self.model(**obj_in)
        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj

    def create_batch(self, objs_in: List[Dict[str, Any]]) -> List[T]:
        """批量创建记录"""
        db_objs = [self.model(**obj) for obj in objs_in]
        self.session.add_all(db_objs)
        self.session.commit()
        for obj in db_objs:
            self.session.refresh(obj)
        return db_objs

    def update(self, id: int, obj_in: Dict[str, Any]) -> Optional[T]:
        """根据ID更新记录"""
        db_obj = self.get_by_id(id)
        if not db_obj:
            return None
        for key, value in obj_in.items():
            if hasattr(db_obj, key) and value is not None:
                setattr(db_obj, key, value)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj

    def update_by_fields(self, filters: Dict[str, Any], updates: Dict[str, Any]) -> int:
        """
        按条件批量更新
        :return: 更新的行数
        """
        query = self.session.query(self.model)
        for key, value in filters.items():
            column = getattr(self.model, key, None)
            if column is not None:
                query = query.filter(column == value)
        result = query.update(updates, synchronize_session=False)
        self.session.commit()
        return result

    # ==================== 删除 ====================

    def delete(self, id: int) -> bool:
        """硬删除"""
        db_obj = self.get_by_id(id)
        if not db_obj:
            return False
        self.session.delete(db_obj)
        self.session.commit()
        return True

    def delete_batch(self, ids: List[int]) -> int:
        """批量硬删除"""
        result = (
            self.session.query(self.model)
            .filter(self.model.id.in_(ids))
            .delete(synchronize_session=False)
        )
        self.session.commit()
        return result

    def soft_delete(self, id: int, deleted_field: str = "is_deleted") -> bool:
        """
        软删除（如果模型有is_deleted字段）
        """
        db_obj = self.get_by_id(id)
        if not db_obj or not hasattr(db_obj, deleted_field):
            return False
        setattr(db_obj, deleted_field, True)
        self.session.commit()
        return True

    # ==================== 存在性检查 ====================

    def exists(self, **kwargs) -> bool:
        """检查是否存在匹配记录"""
        return (
            self.session.query(self.model)
            .filter_by(**kwargs)
            .first()
            is not None
        )
